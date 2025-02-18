import os

environment = os.getenv('ENVIRONMENT')
is_dev = environment == 'dev'

bind = '0.0.0.0:80'
reload = is_dev
worker_class = 'uvicorn.workers.UvicornWorker'
workers = 1 if is_dev else 4
max_requests = 2048
max_requests_jitter = 256

accesslog = '-' if is_dev else None
