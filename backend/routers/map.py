from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

from backend import database, utils

router = APIRouter(
    prefix='/map',
    tags=['map']
)

templates = Jinja2Templates(directory='frontend')


@router.get('/')
async def map_page(request: Request):
    return templates.TemplateResponse('/map.html', {'request': request})


@router.get('/getBasecamp')
async def getBasecamp():
    try:
        basecamp = database.getBaseCamp('bc1')
        # print(basecamp)
        return JSONResponse(content={'basecamp': basecamp}, status_code=200)
    except:
        errors = 'Error occured while get basecamp location from DB'
        return JSONResponse(content={'errors': errors}, status_code=400)
        

@router.get('/getNodes')
async def getNodes():
    try:
        nodes = database.getNodes()
        # print(nodes)
        return JSONResponse(content={'nodes': nodes}, status_code=200)
    except:
        errors = 'Error occured while get nodes location from DB'
        return JSONResponse(content={'errors': errors}, status_code=400)
        

@router.post('/generateMissionFile')
async def generateMissionFile(request: Request):
    requestJson = await request.json()

    basecamp = requestJson.get('basecamp')
    destination = requestJson.get('destination')
    user = utils.getUserFromCookies(request.cookies)
    
    missionFile = [basecamp, destination]

    route = missionFile

    return JSONResponse(content={'route': route}, status_code=200)