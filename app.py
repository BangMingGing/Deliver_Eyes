from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routers import signup, login, menu


app = FastAPI()
      
# 정적 파일 서비스를 위한 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(menu.router)