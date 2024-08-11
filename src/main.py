"""Main entrypoint for the app"""

# General
import logging
from contextlib import asynccontextmanager
from functools import wraps
from datetime import datetime

# FastAPI
from fastapi import FastAPI, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

# Pydantic
from pydantic import ValidationError

# Internal
from src.modules.models.inputs.app_inputs import (
    LoginInput,
    RegisterInput,
    MedicineInput,
    UpdateMedicineInput,
)
from src.modules.services.aws.cognito_service import CognitoClient
from src.modules.services.aws.dynamodb_service import DynamoDBClient


# App configuration

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
dynamo_db_client = DynamoDBClient()


def login_required(func):
    """
    Defines a decorator for protected routes
    """

    @wraps(func)
    async def decorated_function(*args, **kwargs):
        request = kwargs.get("request")
        if not request:
            return RedirectResponse(
                url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )
        token = request.cookies.get("session_token")
        if not token:
            return RedirectResponse(
                url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )
        if "error" in cognito_client.get_current_user(token=token):
            redirect = RedirectResponse(
                url="/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT
            )
            redirect.delete_cookie(
                key="session_token", httponly=True, samesite="strict"
            )
            return redirect
        return await func(*args, **kwargs)

    return decorated_function


### GET Endpoints ###

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
    if request.cookies.get("session_token"):
        return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def read_register(request: Request):
    """Displays the registration page."""
    if request.cookies.get("session_token"):
        return RedirectResponse(url="/", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/medkit", response_class=HTMLResponse)
@login_required
async def get_medkit(request: Request):
    """Displays the medkit page with the list of medicines."""

    token = request.cookies.get("session_token")
    user_sub = cognito_client.get_current_user(token=token).get("user_sub")

    medicine_list = await dynamo_db_client.get_medicines_by_user_sub(user_sub)

    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m").date().replace(day=1)
        except ValueError:
            return None

    today = datetime.now().date().replace(day=1)  # Get today's date

    medicine = [
        {
            "medicine_name": item.get("medicine_name", {}).get("S", "Unknown"),
            "medicine_type": item.get("medicine_type", {}).get("S", "Unknown"),
            "quantity": item.get("quantity", {}).get("N", "0"),
            "expiration_date": item.get("expiration_date", {}).get("S", "N/A"),
            "medicine_id": item.get("medicine_id", {}).get("S", ""),
            "is_expired": parse_date(item.get("expiration_date", {}).get("S", "N/A")) < today  # Compare dates
        }
        for item in medicine_list
    ]
    
    sorted_medicine = sorted(medicine, key=lambda x: x['medicine_name'].lower())

    return templates.TemplateResponse(
        "medkit.html", {"request": request, "medicines": sorted_medicine}
    )



@app.get("/about", response_class=HTMLResponse)
@login_required
async def get_about(request: Request):
    """Displays the login page."""
    return templates.TemplateResponse("about.html", {"request": request})


### POST Endpoints ###

@app.post("/logout")
async def logout() -> RedirectResponse:
    """
    Clears cookies, logs out user.
    """
    redirect = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    redirect.delete_cookie(
        key="session_token",
        httponly=True,
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
            logger.info({"message": ".main(CognitoClient) - Login successful", "status_code": 200})
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
            logger.info({"message": ".main(CognitoClient) - User registered successfully", "status_code": 200})
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


@app.post("/add_medicine", response_class=HTMLResponse)
async def add_medicine(
    request: Request,
    medicine_name: str = Form(...),
    medicine_type: str = Form(...),
    quantity: int = Form(...),
    expiration_date: str = Form(...),
):
    """Handles medicine form submition"""

    token = request.cookies.get('session_token')
    user_sub = cognito_client.get_current_user(token=token).get("user_sub")
    try:
        medicine_input = MedicineInput(
            user_sub=user_sub,
            medicine_name=medicine_name,
            medicine_type=medicine_type,
            quantity=quantity,
            expiration_date=expiration_date,
        )
        await dynamo_db_client.insert_medicine(medicine_input)
        logger.info({"message": ".main(DynamoDBClient) - Medicine data uploaded", "status_code": 200})
        return RedirectResponse(url="/medkit", status_code=status.HTTP_303_SEE_OTHER)
# TODO: Correct error handling
    except ValidationError as val_err:
        return templates.TemplateResponse(
            "medkit.html",
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
            "medkit.html",
            {"request": request, "error_message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@app.post("/delete_medicine", response_class=HTMLResponse)
async def delete_medicine(
    request: Request,
    medicine_id: str = Form(...)
):
    """Deletes selected medicine record"""
    token = request.cookies.get('session_token')
    user_sub = cognito_client.get_current_user(token=token).get("user_sub")
    try:
        await dynamo_db_client.delete_medicine(user_sub, medicine_id)
        logger.info({"message": ".main(DynamoDBClient) - Medicine record deleted", "status_code": 200})
        return RedirectResponse(url="/medkit", status_code=status.HTTP_303_SEE_OTHER)
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


@app.post("/edit_medicine", response_class=HTMLResponse)
async def edit_medicine(
    request: Request,
    medicine_id: str = Form(...),
    medicine_name: str = Form(...),
    medicine_type: str = Form(...),
    quantity: int = Form(...),
    expiration_date: str = Form(...)
):
    """Handles edit medicine form submition"""

    token = request.cookies.get('session_token')
    user_sub = cognito_client.get_current_user(token=token).get("user_sub")
    try:
        update_medicine_input = UpdateMedicineInput(
            medicine_id=medicine_id,
            user_sub=user_sub,
            medicine_name=medicine_name,
            medicine_type=medicine_type,
            quantity=quantity,
            expiration_date=expiration_date
        )
        await dynamo_db_client.edit_medicine(update_medicine_input)
        logger.info({"message": ".main(DynamoDBClient) - Medicine data edited", "status_code": 200})
        return RedirectResponse(url="/medkit", status_code=status.HTTP_303_SEE_OTHER)
# TODO: Correct error handling
    except ValidationError as val_err:
        return templates.TemplateResponse(
            "medkit.html",
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
            "medkit.html",
            {"request": request, "error_message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
