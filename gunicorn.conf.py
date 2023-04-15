from os import getenv
from multiprocessing import cpu_count


# HTTP Path
host = getenv("HOST", "localhost")
port = getenv("PORT", "8000")
bind = f"{host}:{port}"

# Worker Options
workers = cpu_count()
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = getenv("LOG_LEVEL", "info")
accesslog = getenv("ACCESS_LOG", "-")
errorlog = getenv("ERROR_LOG", "-")

timeout = int(getenv('TIMEOUT', '120'))
keepalive = int(getenv('KEEP_ALIVE', '5'))
