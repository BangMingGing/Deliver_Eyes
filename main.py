import subprocess

app_process = subprocess.Popen(['python3', '-m','uvicorn', 'app:app', '--reload', '--host=0.0.0.0', '--port=8889'])
log_process = subprocess.Popen(['python3', 'MonitoringModule/loggingConsumer.py'])
taskManager_process = subprocess.Popen(['python3', 'TaskManageModule/consumer.py'])

app_process.wait()
log_process.wait()
taskManager_process.wait()