from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from backend import database, hashing, token

router = APIRouter(
    prefix='/login',
    tags=['login']
)

templates = Jinja2Templates(directory='frontend')


@router.get('/')
async def login_page(request: Request):
    return templates.TemplateResponse('/login.html', {'request': request})

@router.post('/')
async def login(request: Request):
    requestJson = await request.json()

    user_email = requestJson.get('user_email')
    password = requestJson.get('password')
    
    errors = []
    if not user_email:
        errors.append('Please Enter Email')
    if not password:
        errors.append('Please Enter Password')
    # 이메일이 존재하는지 확인
    if not database.check_email(user_email):
        errors.append("Email not exists")

    if errors:
        return JSONResponse(content={'errors': errors}, status_code=400)

    # 유저 정보 가져오기
    user = database.get_user(user_email)
    
    # 비밀번호가 일치하는지 확인
    if not hashing.Hash.verify(user["password"], password):
        errors.append("Invalid Password")
        return JSONResponse(content={'errors': errors}, status_code=400)
    
    # 유저 이메일로 토큰 발급
    access_token = token.create_access_token(data={'sub': user["email"]})
    
    return JSONResponse(content={'access_token': access_token}, status_code=200)
