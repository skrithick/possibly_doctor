import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from possibly import doctor

class Query(BaseModel):
    question: str

app = FastAPI(title="possibly doctor")
app.mount('/static', StaticFiles(directory='client'), name='static')

@app.get('/')
def client():
    return FileResponse('client/index.html')

@app.get('/api/forget')
def forget():
    doctor.forget()
    print('Forgot previous memory')
    return 'Forgot previous memory'

@app.post('/api/chat')
def chat(req: Query):
    result = doctor.query(req.question)
    return result


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')