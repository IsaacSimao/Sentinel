from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Sentinel está rodando"}

@app.get("/health")
def status():
    return {
    "status do sistema": "Servidor Online",
    "service": "Sentinel"
}
