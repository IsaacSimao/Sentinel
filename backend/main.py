from fastapi import FastAPI
from services.monitor_service import check_url
from datetime import datetime

app = FastAPI()

urls_monitoradas = []
historico_eventos = []

@app.get("/")
def root():
    return {"message": "Sentinel está rodando"}

@app.get("/health")
def status():
    return {
        "status do sistema": "Servidor Online",
        "service": "Sentinel"
    }

@app.get("/monitor")
def chamarHttp(url):
    return check_url(url)

@app.post("/monitor")
def monitorarUrl(url):

    for monitor in urls_monitoradas:

        if monitor["url"] == url:
            return {
                "status": "URL já cadastrada no Sentinel"
            }

    resultado = check_url(url)

    urls_monitoradas.append(resultado)

    return {
        "url": url,
        "status": "Nova URL cadastrada no Sentinel"
    }

@app.get("/monitors")
def Url_Listadas():
    return {
        "urls": urls_monitoradas
    }

@app.post("/monitors/update")
def atualizarMonitores():

    atualizar_UrlListadas()

    return { "status": "Monitoramentos de Urls atualizadas com sucesso" }  

def atualizar_UrlListadas():

    for monitor in urls_monitoradas:

        status_anterior = monitor["status"]
        resultado = check_url(monitor["url"])

        print("Anterior:", status_anterior)
        print("Atual:", resultado["status"])

        if status_anterior != resultado["status"]:

            if resultado["status"] == "OFFLINE":
                tipo_evento = "DOWN"

            elif resultado["status"] == "ONLINE":
                tipo_evento = "RECOVERY"

            else:
                tipo_evento = "STATUS_CHANGE"

            evento = {
                "url": monitor["url"],
                "status_anterior": status_anterior,
                "status_atual": resultado["status"],
                "tipo": tipo_evento,
                "timestamp": datetime.now()
            }

            historico_eventos.append(evento)

            print("O status do sistema mudou!")

        monitor.update(resultado)

@app.get("/events")
def listarEventos():

    return {
        "eventos": historico_eventos
    }        