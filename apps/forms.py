import re
from enum import Enum

from fastapi import Form, File, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from apps import models
from apps.hashing import Hasher


class RegisterForm(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: str

    def is_valid(self, db: Session):
        errors = []
        if self.confirm_password != self.password:
            errors.append('Password did not match!')

        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, self.email):
            errors.append('Must be a valid email address')
        self.confirm_password = None
        q = db.query(models.Users).filter(models.Users.email == self.email)
        exists = db.query(q.exists()).first()[0]

        if exists:
            errors.append('Must be a unique email address')

        self.password = Hasher.get_password_hash(self.password)
        return errors

    @classmethod
    def as_form(
            cls,
            name: str = Form(...),
            email: str = Form(...),
            password: str = Form(...),
            confirm_password: str = Form(...)
    ):
        return cls(name=name, email=email, password=password, confirm_password=confirm_password)


class LoginForm(BaseModel):
    email: str
    password: str

    def is_valid(self, db: Session):
        errors = []

        user: models.Users = db.query(models.Users).filter(models.Users.email == self.email).first() # noqa
        if not user:
            errors.append('User not found!')
        elif not Hasher.verify_password(self.password, user.password):
            errors.append('Password does not match!')

        return errors, user

    @classmethod
    def as_form(
            cls,
            email: str = Form(...),
            password: str = Form(...),
    ):
        return cls(email=email, password=password)


class TodoForm(BaseModel):
    title: str
    complete: bool

    @classmethod
    def as_form(
            cls,
            title: str = Form(...),
            complete: bool = Form(...),

    ):
        return cls(title=title, complete=complete)


class UserForm(BaseModel):
    email: str
    username: str
    password: str
    is_active: bool
    role: Enum

    @classmethod
    def as_form(
            cls,
            email: str = Form(...),
            username: str = Form(...),
            password: str = Form(...),
            is_active: bool = Form(...),
            role: Enum = Form(...)
    ):
        return cls(email=email, username=username, password=password, is_active=is_active, role=role)
