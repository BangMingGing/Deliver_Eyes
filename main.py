import subprocess

fastapi_process = subprocess.Popen(['python3', '-m','uvicorn', 'app:app', '--reload', '--host=0.0.0.0', '--port=8889'])

fastapi_process.wait()

