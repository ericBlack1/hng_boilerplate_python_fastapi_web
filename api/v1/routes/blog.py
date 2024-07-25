from fastapi.encoders import jsonable_encoder
from api.v1.schemas.blog import BlogUpdateResponseModel, BlogRequest
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.v1.models.user import User
from api.utils.dependencies import get_current_user, get_super_admin
from api.v1.services.blog import BlogService
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from api.v1.models.blog import Blog
from api.v1.schemas.blog import BlogResponse, BlogCreate

blog = APIRouter(prefix="/blogs", tags=["Blog"])

@blog.post("/api/v1/blogs")
def create_blog(blog: BlogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_super_admin)):
    if not current_user:
        raise HTTPException(status_code=401, detail="You are not Authorized")
    blog_service = BlogService(db)
    new_blogpost = blog_service.create(db=db, schema=blog, author_id=current_user.id)

    return {
        "message": "Post Created Successfully!",
        "status_code": 200,
        "data": new_blogpost
}

@blog.get("/", response_model=List[BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).filter(Blog.is_deleted == False).all()
    if not blogs:
        return []
    return blogs

@blog.put("/{id}", response_model=BlogUpdateResponseModel)
async def update_blog(id: str, blogPost: BlogRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    blog_service = BlogService(db)
    try:
        updated_blog_post = blog_service.update(
            blog_id=id,
            title=blogPost.title,
            content=blogPost.content,
            current_user=current_user
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        # Catch any other exceptions and raise an HTTP 500 error
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    return {
        "status": "200",
        "message": "Blog post updated successfully",
        "data": {"post": jsonable_encoder(updated_blog_post)}
    }
