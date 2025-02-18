import os

from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.controllers import admin, authentication, checks, users

app = FastAPI(title='Checkbox Application', version=os.getenv('APP_VERSION', '0.1.0'))
add_pagination(app)


@app.get('/health', include_in_schema=False)
async def health() -> dict[str, str]:
    '''
    Basic health check implementation
    '''
    return {'status': 'ok'}


app.include_router(authentication.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(checks.router)
