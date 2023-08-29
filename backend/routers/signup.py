from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from backend import schemas, hashing, database

router = APIRouter(
    prefix='/signup',
    tags=['signup']
)

templates = Jinja2Templates(directory='templates')

@router.get('/')
async def signup_page(request: Request):
    return templates.TemplateResponse('/signup.html', {'request': request})

@router.post('/')
async def signup(request: Request):
    form = await request.form()

    user_email = form.get('user_email')
    password = form.get('password')

    errors = []
    if not user_email:
        errors.append('Please Enter Email')
        return templates.TemplateResponse("/signup.html", {"request": request, "errors": errors})
    if not password:
        errors.append("Please Enter Password ")
        return templates.TemplateResponse("/signup.html", {"request": request, "errors": errors})

    # 패스워드 해시 처리
    hashed_password = hashing.Hash.bcrypt(password)
    
    # 추가할 유저
    new_user = schemas.User(email=user_email, password=hashed_password)

    # 이메일 중복 체크
    if database.check_email(new_user.email):
        errors.append('Email already exists')
        return templates.TemplateResponse("/signup.html", {"request": request, "errors": errors})
    else:
        database.insert_user(new_user)
        return RedirectResponse('/login', status_code=302)
        