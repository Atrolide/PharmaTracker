"""Main entrypoint for the app"""

# General
import logging
from contextlib import asynccontextmanager
from functools import wraps

# FastAPI
from fastapi import FastAPI, Request, Response, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

# Pydantic
from pydantic import ValidationError

# Internal
from src.modules.models.inputs.app_inputs import LoginInput, RegisterInput
from src.modules.services.aws.cognito_service import CognitoClient


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=W0613, W0621
    """Manages the startup and shutdown of the FastAPI application."""
    print("Application has started")
    yield
    print("Application is shutting down")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="src/frontend/templates")
app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")


cognito_client = CognitoClient()


def login_required(func):
    """
    Defines a decorator for protected routes
    """
    @wraps(func)
    async def decorated_function(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            return RedirectResponse(url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        token = request.cookies.get('session_token')
        if not token:
            return RedirectResponse(url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        if 'error' in cognito_client.get_current_user(token=token):
            return RedirectResponse(url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        return await func(*args, **kwargs)
    return decorated_function


@app.get("/", response_class=HTMLResponse)
@login_required
async def get_root(request: Request):
    """Displays the login page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "success_message": "Welcome "}
        )

@app.get("/login", response_class=HTMLResponse)
async def read_login(request: Request):
    """Displays the login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def read_register(request: Request):
    """Displays the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/logout")
async def logout() -> RedirectResponse:
    """
    Clears cookies, logs out user.
    """
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie(
        key="session_token",
        httponly=True,
        secure=True,
        samesite="strict"
        )
    return redirect


@app.post("/submit-login", response_class=HTMLResponse)
async def submit_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
) -> RedirectResponse or templates.TemplateResponse:  # type: ignore
    """Handles login submission."""
    try:
        # Validate Inputs
        login_input = LoginInput(
            email=email, password=password
            )
        # Attempt to authorize user
        response = await cognito_client.auth_user(
            login_input.email, login_input.password
        )

        # Success
        if session_token := response.get("AuthenticationResult", {}).get("AccessToken"):
            logger.info({"message": "Login successfull", "status_code": 302})
            redirect = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
            redirect.set_cookie(
                key="session_token",
                value=session_token,
                httponly=True,
                samesite="strict"
                )
            return redirect
        # Error
        logger.error(
            {"error": str(response["error"]), "status_code": response["status_code"]}
        )
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": str(response["error"])},
            status_code=response["status_code"],
        )
    # Client side Exceptions
    except ValidationError as val_err:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": str(val_err.errors()[0]["msg"]).replace("Value error, ", "").strip()},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.post("/submit-register", response_class=HTMLResponse)
async def submit_register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
) -> templates.TemplateResponse:        # type: ignore
    """Handles user account creation"""
    try:
        # Validate Inputs
        register_input = RegisterInput(
            email=email, password=password, confirm_password=confirm_password
        )

        # Attempt to register the user
        response = await cognito_client.create_user_account(
            register_input.email, register_input.password
        )

        # Success
        if response.get("UserSub"):
            logger.info({"message": "User registered successfully", "status_code": 200})
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "success_message": "Check your inbox to confirm an email address and log in!"},
                status_code=200
            )

        # Error
        logger.error(
            {"error": str(response["error"]), "status_code": response["status_code"]}
        )
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": str(response["error"])},
            status_code=response["status_code"],
        )
    # Client side Exceptions
    except ValidationError as val_err:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": str(val_err.errors()[0]["msg"]).replace("Value error, ", "").strip()},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
