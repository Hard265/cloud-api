from fastapi import Request, Depends
from app.core.auth import get_current_user_from_request
from app.database import get_db
from sqlalchemy.orm import Session


async def get_context(
    request: Request,
    user=Depends(get_current_user_from_request),
    db: Session = Depends(get_db),
):
    if request and user and db:
        return {"request": request, "user": user, "db": db}
    return {}
