from fastapi import FastAPI
from app.api.router import router as api_router

app = FastAPI(
    title='SpendWise API',
    description='An API for tracking personal finances',
    version='0.1.0'

)

app.include_router(api_router)

@app.get('/')
def root():
    return {'message': 'Welcome to SpendWise API!'}

@app.get('/health')
def health():
    return {'status': 'ok'}