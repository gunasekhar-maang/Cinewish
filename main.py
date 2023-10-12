from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
import auth, movies

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

# Add the CORS middleware to allow all origins

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)


