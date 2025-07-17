from state_manager import ConfigState, SystemState
from config import HandlingProcess
from utils import logErrorJson
import json
import requests
from datetime import datetime
import os

def sendTo1cApi(state: SystemState, config: ConfigState, listFiles: list[HandlingProcess]) -> tuple[bool, str]:
    #Собираем данные
    for p in listFiles:
        if p.exportName != "": 
            try:
                #Читаем файл выгрузки
                with open(p.exportName, encoding="utf-8") as f:
                    p.send1c = json.loads(f.read())
            except Exception as error:
                #Записываем в log
                logErrorJson(
                    p.path,
                    "1c_send",
                    str(error)
                )
                
                #Обновляем статус
                p.updateStatus(
                    status="critical_error",
                    date=datetime.datetime.now().isoformat(),
                    stage="1c_send",
                    error_msg=str(error),
                    comment="Ошибка при чтении выгрузка_XXXX.json"
                )

    #Отправляем в 1с
    api_url = config.configureYaml["url"]
    api_token = config.configureYaml["token"]
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    for p in listFiles:    
        try:
            if p.status == "ok":
                response = requests.post(api_url, json=p.send1c, headers=headers, timeout=20)
                if response.status_code in (200, 201):
                    p.updateStatus(
                        status="complete",
                        date=datetime.datetime.now().isoformat(),
                        stage="1c_send",
                        error_msg=str(error),
                        comment="Данные успешно приняты "
                    )

                else:
                    p.updateStatus(
                        status="critical_error",
                        date=datetime.datetime.now().isoformat(),
                        stage="1c_send",
                        error_msg=f"HTTP {response.status_code}: {response.text}",
                        comment="Сервер не принял данные"
                    )
        except Exception as error:
            #Логируем
            logErrorJson(
                p.path,
                "1c_send",
                str(error)
            )
            
            p.updateStatus(
                status="critical_error",
                date=datetime.datetime.now().isoformat(),
                stage="1c_send",
                error_msg=str(error),
                comment="Неудалось отправить запрос"
            )
            
    return listFiles
