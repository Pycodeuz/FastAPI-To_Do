import uvicorn
from fastapi import FastAPI
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from apps import models
from apps.routers.auth import auth
from apps.routers.todo import todo
from config import manager, templates
from database import get_db, engine

app = FastAPI()
manager.useRequest(app)


@manager.user_loader()
def load_user(email: str):
    db = next(get_db())
    user = db.query(models.Users).where(models.Users.email == email, models.Users.is_active).first()
    db.close()
    return user


class NotAuthenticatedException(Exception):
    pass


def exc_handler(request, exc):
    return RedirectResponse(url='/login')


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    if not request.state.user:
        return RedirectResponse('/login', status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse('errors/404.html', {"request": request}, status.HTTP_404_NOT_FOUND)


app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/media', StaticFiles(directory='media'), name='media')


@app.on_event("startup")
def startup():
    app.include_router(todo)
    app.include_router(auth)

    # models.Base.metadata.drop_all(engine)
    # models.Base.metadata.create_all(engine)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
