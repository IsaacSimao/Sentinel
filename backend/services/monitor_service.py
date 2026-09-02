import httpx
import time


def check_url(url):

    start_time = time.perf_counter()
    tempo_Limite = 5.0


    try:
        response = httpx.get( url, timeout = tempo_Limite)
        
        status_code = response.status_code 

        if status_code == 200:
            status = "ONLINE"
            message = "Sistema online"

        elif status_code == 404:
            status = "ERROR"
            message = "Recurso não encontrado"

        elif status_code == 500:
            status = "ERROR"
            message = "Erro interno do servidor"

        else:
            status = "ERROR"
            message = "Status de Erro Indefinido"

    except httpx.ConnectError:
        status = "OFFLINE"
        status_code = None
        message = "Sistema offline"

    except httpx.TimeoutException:
        status = "TIMEOUT"
        status_code = None
        message = "Tempo de Resposta Excedido"

    except httpx.HTTPError:
        status = "ERROR"
        message = "Erro na comunicação com o servidor"
        status_code = None
       

    end_time = time.perf_counter()

    response_time = end_time - start_time

    return {
    "url": url,
    "status": status,
    "message": message,
    "status_code": status_code,
    "response_time": response_time
    }