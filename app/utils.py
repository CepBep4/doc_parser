import os
from state_manager import SystemState, logger
import pandas as pd
import yaml
from pathlib import Path
import json
import datetime


#Проверка pause.flag
def checkPause(state: SystemState) -> bool:
    if os.path.exists('logs/pause.flag'):
        state.pause = True
    return state.pause

#Загружаем csv
def load_csv(path: str) -> list[list]:
    try:
        df = pd.read_csv(path, skiprows=1, header=None, encoding="utf-8")
        if df.empty:
            raise ValueError("Пустой справочник")
        return df.values.tolist()
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке CSV-файла: {e}")
    
#Загружаем yaml
def load_yaml(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # if not isinstance(data, dict):
        #     raise BaseException("YAML-файл должен содержать словарь (dict) на верхнем уровне")

        return data

    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке YAML-файла: {e}")

#Проверка на повторную обработку
def checkAgainHandling(path: str) -> bool:
    log_path = "logs/process_log.json"

    if not os.path.exists(log_path):
        return False  # Логов нет — точно не обрабатывался

    with open(log_path, "r", encoding="utf-8") as f:
        try:
            js = json.loads(f.read())
        except json.JSONDecodeError:
            return False
    
    for j in js:
        if j["file"] == path:
            return True

    return False

#Записываем файл в при его несоответствии требованиям
def logNotProcessed(file_path, reason, ext, creditor, debtor):
    log_path = "logs/not_processed.json"

    entry = {
        "datetime": datetime.datetime.now().isoformat(),
        "file": file_path,
        "reason": reason
    }
    
    entry["ext"] = ext
    entry["creditor"] = creditor
    entry["debtor"] = debtor

    # Загрузка существующего массива или создание нового
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
    except:
        data = []
        
    data.append(entry)

    # Перезапись всего массива
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
#Ошибки в error_log.json
def logErrorJson(file_path, stage, error_msg):
    log_path = "logs/error_log.json"

    entry = {
        "datetime": datetime.datetime.now().isoformat(),
        "file": file_path,
        "stage": stage,
        "status": "error",
        "error_msg": error_msg
    }

    # Загрузка существующего массива или создание нового
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.loads(f.read())
    except:
        data = []
        
    data.append(entry)

    # Перезапись всего массива
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

#Проверка перед стартом
def checkSystemBeforeStart(state: SystemState) -> bool | str:
    for directory in [True if os.path.exists(x) else x for x in ['configs','data','exports','logs']]:
        if directory != True:
            state.errors = f"Нарушена структура -> директория {directory} отсутсвует"
            breakWork(state)

#Проверяем структуру yaml файлов
def checkStructYaml(dictObject: dict, filename: str) -> str:
    if filename == "config":
        ...
        
    elif filename == "validators":
        if "date" in dictObject:
            if "regex" not in dictObject["date"] or "description" not in dictObject["date"]:
                raise BaseException
            
        if "number_ip" in dictObject:
            if "regex" not in dictObject["number_ip"] or "description" not in dictObject["number_ip"]:
                raise BaseException
            
        if "event" in dictObject:
            if "must_be_in" not in dictObject["event"] or "description" not in dictObject["event"]:
                raise BaseException
            
        if "adresat" in dictObject:
            if "must_be_in" not in dictObject["adresat"] or "description" not in dictObject["adresat"]:
                raise BaseException
            
    return dictObject
                

#Проверяем структуру csv файлов
def checkStructCsv(data: list[list], filename: str) -> dict:
    #Для форматс
    if filename == 'formats':
        if len(data[0]) == 3:
            response = {}
            for d in data:
                response[d[0]] = {
                    "description": d[1],
                    "parser":d[2]
                }
            return response
        else:
            raise BaseException("Нарушена структура")
    
    #Для адресатов
    elif filename == "adresat" or filename == "events":
        if len(data[0]) == 3:
            response = []
            for d in data:
                response.append(list(d))
            return response
        else:
            raise BaseException("Нарушена структура")  
          
    elif filename == "responsible":
        if len(data[0]) == 4:
            response = []
            for d in data:
                response.append({
                    "name": d[0],
                    "surname":d[1],
                    "patronymic":d[2],
                    "position":d[3],
                })
            return response
        else:
            raise BaseException("Нарушена структура") 
             
    elif filename == "creditors_to_process":
        if len(data[0]) == 4:
            response = {}
            for d in data:
                response[d[0]] = {
                    "link":d[1],
                    "status":d[2],
                    "comments":d[3],
                }
            return response
        else:
            raise BaseException("Нарушена структура")      

#Поиск пути
def findPathFromPattern(rawPath: str) -> str:
    try:
        path = Path(rawPath).expanduser().resolve(strict=False)
        if not path.exists():
            raise FileNotFoundError(f"Путь не существует: {rawPath}")
        return path.as_posix()
    except Exception as e:
        raise RuntimeError(f"Ошибка при обработке пути '{rawPath}': {e}")

#Завершаем работу
def breakWork(state: SystemState):
    #Действия перед завершением
    print(f"\n")
    if state.errors:
        logger.critical(f"Ошибки: {state.errors}")
    if state.pause:
        logger.info(f"Ручная остановка: {state.pause}")
    logger.info(f"Работа програмы завершена, время работы: {round(state.workTime, 3)}сек\nВремя работы по процессам\n"+"\n".join([f'Процесс |{x["name_process"]}| время: {round(x["time_process"], 3)}сек' for x in state.journalProcess]))
    
    #Завершаем работу
    exit()
    