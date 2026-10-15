from fastapi import FastAPI

app = FastAPI(
    title='SpendWise API',
    description='An API for tracking personal finances',
    version='0.1.0'

)

@app.get('/')
def root():
    return {'message': 'Welcome to SpendWise API!'}

@app.get('/health')
def health():
    return {'status': 'ok'}