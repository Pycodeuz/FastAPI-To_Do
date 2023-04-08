from fastapi import Depends, Request, Form, status, APIRouter

from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from apps import models
from config import templates, manager
from database import engine, get_db

todo = APIRouter()
models.Base.metadata.create_all(bind=engine)


@todo.get("/", name='home')
def home(request: Request, current_user=Depends(manager), db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()

    users = db.query(models.Users).filter(models.Users.id == request.state.user.id).first()
    return templates.TemplateResponse("index.html",
                                      {"request": request, "todo_list": todos, 'user': users})


@todo.post("/add", name='add')
def add(title: str = Form(...), db: Session = Depends(get_db)):
    new_todo = models.Todo(title=title)  # noqa
    db.add(new_todo)
    db.commit()
    url = todo.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@todo.get("/update/{todo_id}", name='update')
def update(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()  # noqa
    todo.complete = not todo.complete
    db.commit()
    return RedirectResponse(url='/')


@todo.get("/delete/{todo_id}", name='delete')
def delete(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return RedirectResponse(url='/')
