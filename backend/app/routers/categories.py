from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.routers.auth import get_current_user
from app.models.user import User
from pydantic import BaseModel

router = APIRouter()

class CategoryNode(BaseModel):
    id: int
    name_fr: str
    name_ar: Optional[str]
    icon_slug: str
    is_essential: bool
    children: List["CategoryNode"] = []

    class Config:
        from_attributes = True

@router.get("/", response_model=List[CategoryNode])
def get_categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    parents = db.query(Category).filter(Category.parent_id == None).all()
    return parents
