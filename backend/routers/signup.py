from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from backend import schemas, hashing, database

router = APIRouter(
    prefix='/signup',
    tags=['signup']
)

templates = Jinja2Templates(directory='frontend')

@router.get('/')
async def signup_page(request: Request):
    return templates.TemplateResponse('/signup.html', {'request': request})

@router.post('/')
async def signup(request: Request):
    form = await request.json()

    user_email = form.get('user_email')
    password = form.get('password')

    errors = []
    if not user_email:
        errors.append('Please Enter Email')
    if not password:
        errors.append("Please Enter Password")
    # 중복 확인
    if database.check_email(user_email):
        errors.append('Email already exists')

    if errors:
        return JSONResponse(content={'errors': errors}, status_code=400)

    # 패스워드 해시 처리
    hashed_password = hashing.Hash.bcrypt(password)
    
    # 추가할 유저
    new_user = schemas.User(email=user_email, password=hashed_password)

    # 유저 DB에 추가
    database.insert_user(new_user)

    return JSONResponse(content={'message': 'Sign Up Success'}, status_code=200)
  