from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schema, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schema.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), Limit: int = 5, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts """)
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).order_by(models.Post.id.desc()).limit(Limit).offset(skip).all()

    #Label for models.Vote.post_id must match the label in the schema. [schema.PostOut]
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).order_by(models.Post.id.desc()).limit(Limit).offset(skip).all()
    return results

@router.get("/{id}", response_model=schema.PostOut)
def get_posts_by_id(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Convert id to STR because that needs a string, and not an integer
    post = None
    # try:
    #     cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    #     post = cursor.fetchone()
    # except (Exception, psycopg2.DatabaseError) as error:
    #     print(error)
    #
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    #
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= f"Post with id: {id} was not found")
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Post)
def create_posts(post: schema.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # try:
    #     cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    #     new_post = cursor.fetchone()
    #     conn.commit()
    # except (Exception, psycopg2.DatabaseError) as error:
    #     print(f"Postgres Error -> {error}")
    #######
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    #######
    ### If the schema has fifty fields, then we are in quandry. Since, the model is Pydantic, and therefore
    ### follows the schema, it is easier to unpack the dict. **post.dict()
    #
    # print(current_user.email)
    #
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    #
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # deleted_post = None
    # try:
    #     cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    #     deleted_post = cursor.fetchone()
    #     conn.commit()
    # except (Exception, psycopg2.DatabaseError) as error:
    #     print(error)
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f"Post with id: {id} doesn't exist.")
    #If post is not None then check if post id is equal to current_user id
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail =f"Not authorized to perform this action")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model= schema.Post, status_code=status.HTTP_205_RESET_CONTENT)
def update_posts(id: int, post: schema.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f"Post with id: {id} doesn't exist.")
    #If post is not None then check if post id is equal to current_user id
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail =f"Not authorized to perform this action")
    post_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()