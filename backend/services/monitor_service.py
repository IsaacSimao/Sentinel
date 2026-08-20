import httpx
import time


def check_url(url):

    start_time = time.perf_counter()
    tempo_Limite = 5.0


    try:
        response = httpx.get( url, timeout = tempo_Limite)
        
        status = "Sistema online"
        status_code = response.status_code 

        if status_code == 200:
            status = "Sistema online"

        elif status_code == 404:
            status = "Recurso não encontrado"

        elif status_code == 500:
            status = "Erro interno do servidor"

        else:
            status = "Status de Erro Indefinido"

    except httpx.ConnectError:
        
        status = "Sistema offline"
        status_code = None

    except httpx.TimeoutException:

        status = "Erro: Tempo de Resposta Excedido"
        status_code = None
       

    end_time = time.perf_counter()

    response_time = end_time - start_time

    return {
        "url": url,
        "status": status,
        "status_code": status_code,
        "response_time": response_time,
    }