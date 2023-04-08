from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from starlette.background import BackgroundTasks
from starlette.responses import RedirectResponse

from apps import forms, models
from apps.utilis.send_email import send_verification_email, decode_data
from apps.utilis.token import check_token
from config import manager, templates
from database import get_db

auth = APIRouter()


@auth.get('/login', name='login')
def auth_login(request: Request):
    context = {
        'request': request
    }
    return templates.TemplateResponse('auth/signin.html', context)


@auth.get('/logout', name='logout')
def auth_logout(request: Request, current_user=Depends(manager)):
    responce = templates.TemplateResponse('auth/signin.html', {'request': request})
    responce.delete_cookie('access-token')
    return responce


@auth.get('/activate/{uid}/{token}', name='activate_user')
def auth_logout(uid: str, token: str, db: Session = Depends(get_db)):
    pk = decode_data(uid)
    user = db.query(models.Users).where(models.Users.id == pk).first()

    if check_token(user, token):
        db.query(models.Users).where(models.Users.id == user.id).update({'is_active': True})
        db.commit()
        return RedirectResponse('/login', status.HTTP_302_FOUND)
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND)


@auth.post('/login', name='login')
def auth_login(
        request: Request,
        form: forms.LoginForm = Depends(forms.LoginForm.as_form),
        db: Session = Depends(get_db)
):
    errors, user = form.is_valid(db)
    if errors:
        context = {
            'request': request,
            'errors': errors
        }
        return templates.TemplateResponse('auth/signin.html', context)
    else:
        if not user:
            return RedirectResponse("/login", status.HTTP_302_FOUND)

        access_token = manager.create_access_token(
            data={"sub": user.email}
        )
        resp = RedirectResponse("/", status.HTTP_302_FOUND)
        manager.set_cookie(resp, access_token)
        return resp


@auth.get('/register', name='register')
def register_page(request: Request):
    context = {
        'request': request
    }
    return templates.TemplateResponse('auth/signup.html', context)


@auth.post('/register', name='register')
def register_page(
        request: Request,
        background_task: BackgroundTasks,
        form: forms.RegisterForm = Depends(forms.RegisterForm.as_form),
        db: Session = Depends(get_db),
):
    if errors := form.is_valid(db):
        context = {
            'errors': errors,
            'request': request
        }
        return templates.TemplateResponse('auth/signup.html', context)
    else:
        data = form.dict(exclude_none=True)
        user = models.Users(**data)
        db.add(user)
        host = f'{request.url.scheme}://{request.url.netloc}/activate/'
        background_task.add_task(send_verification_email, user, host)
        db.commit()
        return templates.TemplateResponse('auth/signin.html', {'request': request})


@auth.get('/logout', name='logout')
def auth_logout(request: Request, current_user=Depends(manager)):
    responce = templates.TemplateResponse('auth/login.html', {'request': request})
    responce.delete_cookie('access-token')
    return responce

