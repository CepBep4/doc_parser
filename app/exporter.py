from state_manager import ConfigState, SystemState
from config import HandlingProcess
from utils import breakWork, logErrorJson
import json
import os
from datetime import datetime

def append_to_json_array(file_path: str, record: dict):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Если файла нет — создаём с одной записью
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([record], f, ensure_ascii=False, indent=2)
        return

    # Если есть — загружаем, добавляем, сохраняем
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
        except json.JSONDecodeError:
            data = []

    data.append(record)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def exportToJson(p: HandlingProcess):
    status = p.ai["Status"]

    if status == "ok":
        path = f"exports/выгрузка_{datetime.now().strftime('%Y%m%d')}.json"
        p.exportName = path
        append_to_json_array(path, p.ai)

    elif status == "incomplete":
        append_to_json_array("logs/incomplete.json", p.ai)

    elif status == "duplicate":
        append_to_json_array("logs/duplicates_log.json", p.ai)

    else:
        error_entry = {
            "datetime": datetime.now().isoformat(),
            "file": p.ai.get("Файл", "unknown"),
            "stage": "export",
            "status": status,
            "error": "Неизвестный статус записи"
        }
        append_to_json_array("logs/error_log.json", error_entry)
        
    return p
        
def exportFiles(state: SystemState, config: ConfigState, listFiles: list[HandlingProcess]):
    for p in listFiles:
        try:
            #Пропускаем файлы с ошибками
            if p.status != "ok":
                continue
            
            p = exportToJson(p)
            
            #Обновляем статус
            p.updateStatus(
                status="ok",
                date=datetime.now().isoformat(),
                stage="export",
                comment="Экспортируем данные"
            )
            
        except Exception as error:
            #Записываем в log
            logErrorJson(
                p.path,
                "export",
                str(error)
            )
            
            #Обновляем статус
            p.updateStatus(
                status="critical_error",
                date=datetime.datetime.now().isoformat(),
                stage="export",
                error_msg=str(error),
                comment="Экспортируем данные"
            )
            
    #Завершаем работу если все файлы с ошибками     
    if "ok" not in [x.status for x in listFiles]:
        state.errors = "Не осталось файлов для обработки"
        breakWork(state)
            
    return listFiles