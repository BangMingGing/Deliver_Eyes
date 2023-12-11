from fastapi import APIRouter, Request, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse

from backend import utils
from FaceRecogModule import face_data_generator

router = APIRouter(
    prefix='/face',
    tags=['face']
)

templates = Jinja2Templates(directory='frontend')

@router.get('/')
async def login_page(request: Request):
    return templates.TemplateResponse('/face.html', {'request': request})

@router.post('/generateFaceData')
async def generateFaceData(request: Request, videoFile: UploadFile = File(...)):
    user = utils.getUserFromCookies(request.cookies)
    if not user:
        return RedirectResponse(url="/login/", status_code=302)

    with open(f"/home/bmk/repos/etri/Deliver_Eyes/FaceRecogModule/train_datas/{user}", "wb") as video:
        video.write(videoFile.file.read())

    await face_data_generator.train(user)

    try:
        message = "Video uploaded successfully"
        return JSONResponse(content={'message': message}, status_code=200)
    except:
        errors = 'Generate Mission File Failed'
        return JSONResponse(content={'errors': errors}, status_code=400)
