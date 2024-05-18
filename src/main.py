"""Main entrypoint for the app"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette import status
import uvicorn

from modules.models.inputs.app_inputs import LoginInput


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    if login_data.password == "aaa":
        # Redirect to dashboard after successful login
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error_message": "Incorrect password"},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


def main():
    """Entry point to run the FastAPI application using Uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
