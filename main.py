import subprocess
import time

app_process = subprocess.Popen(['python3', '-m','uvicorn', 'app:app', '--reload', '--host=0.0.0.0', '--port=8889'])

app_process.wait()
