from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse

from backend import database, utils

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

templates = Jinja2Templates(directory='frontend')

@router.get('/')
async def admin_page(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)
    return templates.TemplateResponse('/admin.html', {'request': request})


@router.get('/getBasecamp')
async def getBasecamp():
    try:
        basecamps = database.getBCNodes()
        utils.build_graph_for_basecamps(basecamps)
        return JSONResponse(content={'basecamps': basecamps}, status_code=200)
    except:
        errors = 'Error occured while get basecamp location from DB'
        return JSONResponse(content={'errors': errors}, status_code=400)
        

@router.get('/getNodes')
async def getNodes():
    try:
        nodes = database.getNodes4node()
        return JSONResponse(content={'nodes': nodes}, status_code=200)
    except:
        errors = 'Error occured while get nodes location from DB'
        return JSONResponse(content={'errors': errors}, status_code=400)

@router.post('/insertnode')
async def insertnode(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)

    requestJson = await request.json()

    node_name = requestJson.get('selectedLocationName')
    node_coor = requestJson.get('selectedLocation')
    adj_node = requestJson.get('neighbor_node_list')

    database.insert_new_node(node_name, node_coor, adj_node)


@router.post('/addNewneighbor')
async def addNewneighbor(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)

    requestJson = await request.json()

    node_name = requestJson.get('selectedLocationName')
    adj_node = requestJson.get('neighbor_node_list')
    utils.add_new_neighbor(node_name, adj_node)

@router.post('/delete_node')
async def delete_node(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)
    try:
        requestJson = await request.json()
        node_name = requestJson.get('node_name')
        utils.delete_node(node_name)
        return JSONResponse(content={'node_name': node_name}, status_code=200)
    except:
        errors = 'Error occured while delete node'
        return JSONResponse(content={'errors': errors}, status_code=400)
    

@router.get('/drawGraph')
async def drawGraph(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)
    try:
        basecamps = database.getBCNodes()
        utils.revise_graph(basecamps)
        message = "successfully revise graph"
        return JSONResponse(content={'message': message}, status_code=200)
    except:
        errors = 'Error occured while delete node'
        return JSONResponse(content={'errors': errors}, status_code=400)

@router.get("/InitUI")
async def updateUI(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)
    try:
        dronedata = database.getInitialDataForMonitoring()
        return JSONResponse(content={'dronedata': dronedata}, status_code=200)
    except:
        errors = 'Error occured while get drone data in init UI'
        return JSONResponse(content={'errors': errors}, status_code=400)


@router.get("/updateUI")
async def updateUI(request: Request):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)
    
    return StreamingResponse(                                                                                                                                                        
        utils.get_all_gps_event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )