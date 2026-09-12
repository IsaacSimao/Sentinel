from fastapi import FastAPI
from services.monitor_service import check_url
from datetime import datetime
from contextlib import asynccontextmanager

import time
import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    iniciar_monitoramento()
    yield

app = FastAPI(lifespan=lifespan)

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

def calcular_metricas(monitor, status_atual, agora):

    tempo_monitorado = (
        agora - monitor["inicio_monitoramento"]
    ).total_seconds()

    tempo_offline_atual = 0

    if status_atual == "OFFLINE" and "inicio_offline" in monitor:

        tempo_offline_atual = (
            agora - monitor["inicio_offline"]
        ).total_seconds()

    tempo_offline_total = (
        monitor["tempo_total_offline"] + tempo_offline_atual
    )

    tempo_online = max(
        0,
        tempo_monitorado - tempo_offline_total
    )

    uptime = 0

    if tempo_monitorado > 0:

        uptime = (tempo_online / tempo_monitorado) * 100
        uptime = round(uptime, 2)

    return {
        "tempo_monitorado": tempo_monitorado,
        "tempo_online": tempo_online,
        "tempo_offline": tempo_offline_total,
        "uptime": uptime
    }

def atualizar_UrlListadas():
    for monitor in urls_monitoradas:
        status_anterior = monitor["status"]
        resultado = check_url(monitor["url"])

        agora = datetime.now()

        if status_anterior != resultado["status"] and resultado["status"] == "OFFLINE":
            monitor["inicio_offline"] = agora

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
                  if "inicio_offline" in monitor:
                    duracao = timestamp_evento - monitor["inicio_offline"]
                    monitor["tempo_total_offline"] += duracao.total_seconds()
                    monitor.pop("inicio_offline", None)

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

        metricas = calcular_metricas(
            monitor,
            resultado["status"],
            agora
        )
        monitor.update(metricas)

        tempo_monitorado_formatado = formatar_duracao(
            metricas["tempo_monitorado"]
        )
        tempo_online_formatado = formatar_duracao(
            metricas["tempo_online"]
        )
        tempo_offline_formatado = formatar_duracao(
            metricas["tempo_offline"]
        )

        print("Anterior:", status_anterior)
        print("Atual:", resultado["status"])
        print("Tempo monitorado:", tempo_monitorado_formatado)
        print("Tempo online:", tempo_online_formatado)
        print("Tempo offline:", tempo_offline_formatado)
        print("Uptime:", metricas["uptime"])

        monitor.update(resultado)

def monitoramento_automatico():

    while True:
        atualizar_UrlListadas()
        time.sleep(10)


def iniciar_monitoramento():

    thread_monitoramento = threading.Thread(
        target=monitoramento_automatico,
        daemon=True
    )

    thread_monitoramento.start()


@app.get("/events")
def listarEventos():

    return {
        "eventos": historico_eventos
    }        