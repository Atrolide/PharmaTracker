"""Main entrypoint for the app"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

from pydantic import ValidationError

from src.modules.models.inputs.app_inputs import LoginInput, RegisterInput
from src.modules.services.aws.cognito_service import CognitoClient


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=W0613, W0621
    """Manages the startup and shutdown of the FastAPI application."""
    print("Application has started")
    yield
    print("Application is shutting down")


tags_metadata = [
    {
        "name": "User Authentication",
        "description": "Endpoints for user authentication.",
    },
    {
        "name": "Data Operations",
        "description": "Endpoints for creating, reading, updating, and deleting data.",
    },
]

app = FastAPI(lifespan=lifespan, docs_url="/", openapi_tags=tags_metadata)
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


@app.post(
    "/submit-login",
    response_class=HTMLResponse,
    tags=["User Authentication"],
    operation_id="LoginUser",
)
async def submit_login(
    request: Request, email: str = Form(...), password: str = Form(...)
) -> RedirectResponse or templates.TemplateResponse:  # type: ignore
    """Handles login submission."""
    try:
        login_data = LoginInput(email=email, password=password)
        if login_data.password == "aaa":
            # Redirect to dashboard after successful login
            return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        else:
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error_message": "Incorrect password"},
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
    except ValidationError as val_err:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": str(val_err.errors()[0]["msg"])},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@app.post(
    "/submit-register",
    response_class=HTMLResponse,
    operation_id="RegisterUser",
    tags=["User Authentication"],
)
async def submit_register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Handles user account creation"""
    try:
        register_input = RegisterInput(
            email=email, password=password, confirm_password=confirm_password
        )

        # Attempt to register the user
        response = await cognito_client.create_user_account(
            register_input.email, register_input.password
        )

        if response.get('UserSub'):
            return templates.TemplateResponse("index.html", {"request": request})
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": str(response["error"])},
            status_code=response["status_code"],
        )
    except ValidationError as val_err:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": str(val_err.errors()[0]["msg"])},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
