from fastapi import FastAPI

from taskManager import TaskManager

consume_app = FastAPI(
    prefix='/taskManager',
    tags=['Task Manager']
)

task_manager = TaskManager()

@consume_app.post('/start')
async def start(request: Request):
    payload = await request.form()
    drone = payload.get('drone')

    task_manager.start(drone)

    response = "[Task Manager Response] Deliver Started"
    return JSONResponse(content={'response': response}, status_code=200)


@consume_app.post('/run')
async def run(request: Request):
    payload = await request.form()
    drone = payload.get('drone')

    task_manager.run(drone)

    response = "[Task Manager Response] Task Start"
    return JSONResponse(content={'response': response}, status_code=200)