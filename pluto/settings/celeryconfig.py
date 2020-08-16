from django.conf import settings

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'

broker_url = REDIS_URL
broker_transport_options = {'visibility_timeout': 3600} 
result_backend = REDIS_URL
task_serializer = 'json'
