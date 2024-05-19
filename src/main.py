"""Main entrypoint for the app"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

from src.modules.models.inputs.app_inputs import LoginInput, RegisterInput


@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=W0613, W0621
    """Manages the startup and shutdown of the FastAPI application."""
    print("Application has started")
    yield
    print("Application is shutting down")


app = FastAPI(lifespan=lifespan, docs_url="/")
templates = Jinja2Templates(directory="src/frontend/templates")
app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")


@app.get("/login", response_class=HTMLResponse)
async def read_login(request: Request):
    """Displays the login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def read_register(request: Request):
    """Displays the registration page."""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/submit-login", response_class=HTMLResponse)
async def submit_login(
    request: Request, email: str = Form(...), password: str = Form(...)
):
    """Handles login submission."""
    login_data = LoginInput(email=email, password=password)
    # TODO: Incorporate try-except block. Invoke congito auth method
    if login_data.password == "aaa":
        # Redirect to dashboard after successful login
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": "Incorrect password"},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@app.post("/submit-register", response_class=HTMLResponse)
async def submit_register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    """Handles login submission."""
    register_data = RegisterInput(
        email=email, password=password, confirm_password=confirm_password
    )
    print(register_data)
    if register_data.password != register_data.confirm_password:
        # TODO: Incorporate try-except block. Invoke congito auth method
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": "Passwords do not match"},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    else:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


def main():
    """Entry point to run the FastAPI application using Uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
