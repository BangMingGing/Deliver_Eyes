from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse


router = APIRouter(
    prefix='/menu',
    tags=['menu']
)

templates = Jinja2Templates(directory='frontend')

@router.get('/')
async def menu_page(request: Request):
    return templates.TemplateResponse('/menu.html', {'request': request})
