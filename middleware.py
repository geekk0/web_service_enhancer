import configparser

from fastapi import Request, status
from fastapi.responses import JSONResponse

config = configparser.ConfigParser()
config.read('config.ini')

WHITELISTED_IPS = config['NETWORK_SETTINGS']['WHITELISTED_IPS'].split(',')


async def validate_ip(request: Request, call_next):
    ip = str(request.client.host)

    if ip not in WHITELISTED_IPS:
        data = {
            'message': f'IP {ip} is not allowed to access this resource.'
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # Proceed if IP is allowed
    return await call_next(request)


