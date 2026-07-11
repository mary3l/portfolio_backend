from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import projects

app = FastAPI(title="Project API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)


@app.get("/")
def root():
    return {"message": "API is running"}
