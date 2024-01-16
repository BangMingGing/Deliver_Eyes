import subprocess

from configuration import WEB_CONFIG

app_process = subprocess.Popen(['python3', '-m','uvicorn', 'app:app', '--reload', '--host=0.0.0.0', f'--port={WEB_CONFIG.WEB_PORT}'])

app_process.wait()
