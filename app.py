from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import signup, login, menu, map, admin


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to the actual origin of your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
async def map_page(request: Request):
    return RedirectResponse(url="/login/", status_code=302)

      
# 정적 파일 서비스를 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(menu.router)
app.include_router(map.router)
app.include_router(admin.router)