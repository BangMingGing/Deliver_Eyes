import asyncio

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse

from backend import database, utils, rabbitmq
from MFGModule import MFG

from configuration import RABBITMQ_CONFIG

router = APIRouter(
    prefix='/map',
    tags=['map']
)

templates = Jinja2Templates(directory='frontend')

@router.on_event('startup')
async def startup_event():
    global task_publisher
    global loop
    loop = asyncio.get_event_loop()
    task_publisher = rabbitmq.Publisher(RABBITMQ_CONFIG.TASK_EXCHANGE)
    await task_publisher.initialize()

@router.on_event("shutdown")
async def shutdown_event():
    global task_publisher
    await task_publisher.close()

@router.get('/')
async def map_page(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)
    
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
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)

    requestJson = await request.json()

    basecamp = requestJson.get('basecamp')
    destination = requestJson.get('destination')
    
    # 미션 파일 생성
    # MFG.generateMissionFile(basecamp, destination, user)

    # 경로 가져오기
    try:
        mission = database.getMissionByUser(user)
        route = utils.getRoute(mission)
        return JSONResponse(content={'route': route}, status_code=200)
    except:
        errors = 'Error occured while get route from DB'
        return JSONResponse(content={'errors': errors}, status_code=400)


@router.post('/deliverStart')
async def deliverStart(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)
    
    drone = database.getDroneByUser(user)
    
    if not drone:
        errors = 'Error occured while get drone from DB'
        return JSONResponse(content={'errors': errors}, status_code=400)

    message = {"header": "mission_start", "drone_name": drone, "contents": {'direction': 'forward'}}
    global task_publisher
    global loop
    task = loop.create_task(task_publisher.publish(message, RABBITMQ_CONFIG.TASK_QUEUE))
    await asyncio.gather(task)

    response = "Deliver Start Success"
    return JSONResponse(content={'response': response}, status_code=200)


@router.post("/gps_streaming")
async def gps_streaming(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)

    drone_name = database.getDroneByUser(user)

    return StreamingResponse(
        utils.gps_event_generator(drone_name),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )

    

    