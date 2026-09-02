from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def server_root():
    return {"message": "ED-E: Sistema de Teste Online"}