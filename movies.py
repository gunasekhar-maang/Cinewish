from typing_extensions import Annotated
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from models import Movies,Users
from database import SessionLocal
from auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix='/movies',
    tags=['Movie']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

class Movie_Base(BaseModel):
    title: str

class Edit_Movie(BaseModel):
    id: int
    title: str

class Edit_Movie_Status(BaseModel):
    id: int
    watched: bool

# @router.get('/user', status_code=status.HTTP_200_OK)
# async def get_user(user: user_dependency, db: db_dependency):
#     if user is None:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
#     return db.query(Users).filter(Users.id == user.get('id')).first()



@router.post("/post_movie" , status_code=status.HTTP_201_CREATED)
async def post_movie( user: user_dependency , db:db_dependency , Movie_Base:Movie_Base ):
    existing_movie = db.query(Movies).filter(
        and_(Movies.user_id == user.id, Movies.title == Movie_Base.title)
    ).first()

    if existing_movie:
        return {"message": "Movie already exists"}
    
    create_movie_model = Movies(
        user_id = user.id,
        title = Movie_Base.title,
    )
    db.add(create_movie_model)
    db.commit()
    return {"message": "Movie Posted Successfully", "status": 201}

@router.put("/edit_movie_title", status_code=status.HTTP_201_CREATED)
async def edit_movie_title(db:db_dependency, user:user_dependency , movie:Edit_Movie):
    model = db.query(Movies).filter(Movies.id == movie.id).filter(Movies.user_id == user.id).first()
    if not model:
        return {"message" : "No Movies Found of Yours"}
    model.title = movie.title
    db.add(model)
    db.commit()
    return {"message" : "Movie Title Updated" , "data" : movie.title}

@router.put("/edit_movie_status", status_code=status.HTTP_201_CREATED)
async def edit_movie_status(db:db_dependency, user:user_dependency , movie:Edit_Movie_Status):
    model = db.query(Movies).filter(Movies.id == movie.id).filter(Movies.user_id == user.id).first()
    if not model:
        return {"message" : "No Movies Found of Yours Enter Correct Id"}
    model.watched = movie.watched
    db.add(model)
    db.commit()
    return {"message" : "Movie Status Updated"}

@router.put("/delete_movie/{movie_id}", status_code=status.HTTP_200_OK)
async def delete_movie(user: user_dependency, db: db_dependency, movie_id: int):
    model = db.query(Movies).filter(Movies.id == movie_id).filter(Movies.user_id == user.id).first()
    if not model:
        return {"message" : "No Movies Found of Yours Enter Correct Id"}
    db.query(Movies).filter(Movies.id == movie_id).delete()
    db.commit()
    return {"message" : "Movie Deleted"}

@router.get("/watchlist" , status_code=status.HTTP_200_OK)
async def watchlist(db:db_dependency,user:user_dependency):
    model = db.query(Movies).filter(Movies.user_id == user.id).filter(Movies.watched == False).all()

    if len(model) == 0:
        return {"message" : "No Movies Found"}
    else:
        return {"message" : "successful" , "data" : model}
    
@router.get("/watchedlist" , status_code=status.HTTP_200_OK)
async def watchedlist(db:db_dependency,user:user_dependency):
    model = db.query(Movies).filter(Movies.user_id == user.id).filter(Movies.watched == True).all()

    if len(model) == 0:
        return {"message" : "No Movies Found"}
    else:
        return {"message" : "successful" , "data" : model}

@router.get("/get_user_movies" , status_code=status.HTTP_200_OK)
async def get_user_movies(db:db_dependency,user:user_dependency):
    user_movies = db.query(Movies).filter(Movies.user_id == user.id).all()
    if len(user_movies) == 0:
        return{"user_movies" : "No Movies Found" , "status" : 404}
    return{"user_movies" : user_movies , "status" : 200}

@router.get("/get_all_movies" , status_code=status.HTTP_200_OK)
async def get_all_movies(db:db_dependency):
    movies = db.query(Movies).all()
    return {"All Movies" : movies , "status" : 200}


@router.get("/user_dependency",status_code = status.HTTP_200_OK)
async def user_dependency(user:user_dependency):
    return {"user_id":user.id  ,"user_name":user.username }
