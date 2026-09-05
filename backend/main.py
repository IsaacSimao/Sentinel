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

    resultado["total_quedas"] = 0
    resultado["total_recuperacoes"] = 0
    resultado["tempo_total_offline"] = 0
    resultado["inicio_monitoramento"] = datetime.now()

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

def formatar_duracao(segundos):

    segundos = int(segundos)

    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segundos_restantes = segundos % 60

    if horas > 0:
        return f"{horas}h {minutos}m {segundos_restantes}s"

    if minutos > 0:
        return f"{minutos}m {segundos_restantes}s"

    return f"{segundos_restantes}s"

def atualizar_UrlListadas():

    for monitor in urls_monitoradas:

        status_anterior = monitor["status"]
        resultado = check_url(monitor["url"])

        agora = datetime.now()
        tempo_monitorado = (agora - monitor["inicio_monitoramento"]).total_seconds()

        tempo_online = max(
        0,
        tempo_monitorado - monitor["tempo_total_offline"]
                        )
        uptime = 0

        if tempo_monitorado > 0:
          uptime = (tempo_online / tempo_monitorado) * 100
          uptime = round(uptime, 2)
        monitor["tempo_monitorado"] = tempo_monitorado

        monitor["tempo_online"] = tempo_online
        monitor["uptime"] = uptime
        tempo_monitorado_formatado = formatar_duracao(tempo_monitorado)
        tempo_online_formatado = formatar_duracao(tempo_online)
        tempo_offline_formatado = formatar_duracao(monitor["tempo_total_offline"])

        print("Anterior:", status_anterior)
        print("Atual:", resultado["status"])
        print("Tempo monitorado:", tempo_monitorado_formatado)
        print("Tempo online:", tempo_online_formatado)
        print("Tempo offline:", tempo_offline_formatado)
        print("Uptime:", uptime)

        if status_anterior != resultado["status"]:

            timestamp_evento = datetime.now()

            if resultado["status"] == "OFFLINE":
                tipo_evento = "DOWN"
                monitor["total_quedas"] += 1

            elif resultado["status"] == "ONLINE":
                tipo_evento = "RECOVERY"
                monitor["total_recuperacoes"] += 1

            else:
                tipo_evento = "STATUS_CHANGE"

            duracao = None

            if tipo_evento == "RECOVERY":

                for evento_anterior in reversed(historico_eventos):

                    if (
                        evento_anterior["url"] == monitor["url"]
                        and evento_anterior["tipo"] == "DOWN"
                    ):
                        duracao = timestamp_evento - evento_anterior["timestamp"]

                        monitor["tempo_total_offline"] += duracao.total_seconds()

                        break

            evento = {
                "url": monitor["url"],
                "status_anterior": status_anterior,
                "status_atual": resultado["status"],
                "tipo": tipo_evento,
                "timestamp": timestamp_evento,
                "duracao": duracao
            }

            historico_eventos.append(evento)

            print("O status do sistema mudou!")

        monitor.update(resultado)

@app.get("/events")
def listarEventos():

    return {
        "eventos": historico_eventos
    }        