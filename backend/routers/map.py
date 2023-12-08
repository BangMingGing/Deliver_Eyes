from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse

from backend import database, utils, rabbitmq
from MFGModule import MFG

router = APIRouter(
    prefix='/map',
    tags=['map']
)

templates = Jinja2Templates(directory='frontend')

publisher = rabbitmq.Publisher()
publisher.declareExchange("TaskManager")

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
        

@router.post('/select_use_drone')
async def select_use_drone(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)

    requestJson = await request.json()
    payload = requestJson.get('payload')
    destination = requestJson.get('destination')
    goal_node = database.getNodeName(destination)
    # 드론 선정
    try:
        drone_path_data = MFG.drone_path_select(payload, goal_node)
        return JSONResponse(content={'drone_path_data': drone_path_data}, status_code=200)
    except:
        errors = 'Error occured select use_drone'
        return JSONResponse(content={'errors': errors}, status_code=400)

@router.post('/path4draw')
async def path4draw(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)

    requestJson = await request.json()
    path = requestJson.get('path')
    try:
        path_coor = utils.getpath_coor(path)
        return JSONResponse(content={'path_coor': path_coor}, status_code=200)
    except:
        errors = 'path4draw failed'
        return JSONResponse(content={'errors': errors}, status_code=400)





@router.post('/generateMissionFile')
async def generateMissionFile(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)

    requestJson = await request.json()

    use_drone = requestJson.get('use_drone')
    path = requestJson.get('path')
    
    # 미션 파일 생성
    MFG.generateMissionFile(use_drone, path, user)

    # 경로 가져오기
    try:
        route = database.getRoute(user)
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

    message = {"header": "start", "drone": drone}
    publisher.publish(
        message=message, 
        exchange_name="TaskManager", 
        target="TaskManager"
    )

    response = "Deliver Start Success"
    return JSONResponse(content={'response': response}, status_code=200)
