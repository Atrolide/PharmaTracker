"""Main entrypoint for the app"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn



@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Manages the startup and shutdown of the FastAPI application. """
    print("Application has started")
    yield

    print("Application is shutting down")


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory='src/frontend/templates')


@app.get(
        "/",
          response_class=HTMLResponse
          )
async def read_root(
    request: Request
    ):
    """ Returns a simple message indicating the root endpoint is working. """
    return templates.TemplateResponse("index.html", {"request": request})



def main():
    """ Entry point to run the FastAPI application using Uvicorn. """
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
