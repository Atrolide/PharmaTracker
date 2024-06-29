"""Main entrypoint for the app"""

# General
import logging
from contextlib import asynccontextmanager

# FastAPI
from fastapi import FastAPI, Request, Form, status
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


@app.get("/login", response_class=HTMLResponse, tags=["User Authentication"])
async def read_login(request: Request):
    """Displays the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse, tags=["User Authentication"])
async def read_register(request: Request):
    """Displays the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/submit-login", response_class=HTMLResponse)
async def submit_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
) -> RedirectResponse or templates.TemplateResponse:  # type: ignore
    """Handles login submission."""
    try:
        login_input = LoginInput(
            email=email, password=password
            )
        
        response = await cognito_client.auth_user(
            login_input.email, login_input.password
        )
        
        if response.get("AuthenticationResult", {}).get("AccessToken"):
            logger.info({"message": "Login successfull", "status_code": 200})
            return templates.TemplateResponse("index.html", {"request": request})
        
        logger.error(
            {"error": str(response["error"]), "status_code": response["status_code"]}
        )
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": str(response["error"])},
            status_code=response["status_code"],
        )
    except ValidationError as val_err:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error_message": str(val_err.errors()[0]["msg"])
                .replace("Value error, ", "")
                .strip(),
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
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
            return templates.TemplateResponse("index.html", {"request": request})

        # Error
        logger.error(
            {"error": str(response["error"]), "status_code": response["status_code"]}
        )
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": str(response["error"])},
            status_code=response["status_code"],
        )

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
