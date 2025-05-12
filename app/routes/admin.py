from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.models import User, Word, GameSetting
from app.auth_utils import get_admin_user, get_db
from app.templates import templates

router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, current_admin: User = Depends(get_admin_user),
                    db: Session = Depends(get_db)):
    # Получаем данные для админ-панели
    users = db.query(User).all()
    words = db.query(Word).all()
    settings = db.query(GameSetting).all()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "admin_user": current_admin,
        "users": users,
        "words": words,
        "settings": settings
    })

@router.post("/admin/users/{user_id}/delete")
def delete_user(user_id: int, current_admin: User = Depends(get_admin_user),
                db: Session = Depends(get_db)):
    # Удаление пользователя (доступно только админу)
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)

# Аналогично могут быть реализованы маршруты для управления словами и настройками, 
# например, добавление/удаление слов, изменение настроек и т.д.