from state_manager import ConfigState, SystemState
from utils import breakWork, checkStructCsv, checkStructYaml, load_yaml, load_csv
from dataclasses import dataclass
from datetime import datetime
import json
import traceback
import os

@dataclass
class HandlingProcess:
    date: str
    path: str
    debt: str
    extention: str
    text: str
    ai: dict
    status: str
    credit: str
    exportName: str
    direction: str
    
    def updateStatus(self, stage: str, date, status=None, comment=None, error_msg=None, count=None):
        log_path = "logs/process_log.json"

        # Загружаем существующие записи
        records = []
        
        with open(log_path, "r", encoding="utf-8") as f:
            try:
                records = json.loads(f.read())
            except json.JSONDecodeError:
                pass

        # Обновляем или создаём запись
        updated = False
        for entry in records:
            if entry.get("file") == self.path:
                entry["datetime"] = date
                entry["stage"] = stage
                if status:
                    entry["status"] = status
                    self.status = status
                if comment: entry["comment"] = comment
                if error_msg: entry["error_msg"] = error_msg
                if count is not None: entry["count"] = count
                updated = True
                break

        if not updated:
            # Если запись не найдена — создаём новую
            new_entry = {
                "datetime": date,
                "stage": stage,
                "file": self.path
            }
            if status:
                new_entry["status"] = status
                self.status = status
            if comment: new_entry["comment"] = comment
            if error_msg: new_entry["error_msg"] = error_msg
            if count is not None: new_entry["count"] = count
            records.append(new_entry)

        # Перезаписываем весь файл
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(records, ensure_ascii=False) + "\n")

STATUS_CHECK = {
    "пропустить": False,
    "к обработке": True
}

#Загружаем конфиги из справочников
def loadConfigs(state: SystemState) -> ConfigState:
    config = ConfigState()
    
    #Загружаем formats.csv
    try:
        config.formats = checkStructCsv(load_csv('configs/formats.csv'), "formats")
    except BaseException:
        state.errors = "Нарушена структура файла formats.csv"
    except RuntimeError:
        state.errors = "Неудалось открыть файл formats.csv"
    except ValueError:
        state.errors = "Файл formats.csv пустой"
    finally:
        if state.errors != None:
            breakWork(state)
            
    #Загружаем adresat.csv
    try:
        config.adresat = checkStructCsv(load_csv('configs/adresat.csv'), "adresat")
    except BaseException:
        state.errors = "Нарушена структура файла adresat.csv"
    except RuntimeError:
        state.errors = "Неудалось открыть файл adresat.csv"
    except ValueError:
        state.errors = "Файл adresat.csv пустой"
    finally:
        if state.errors != None:
            breakWork(state)
            
    #Загружаем adresat.csv
    try:
        config.adresat = checkStructCsv(load_csv('configs/adresat.csv'), "adresat")
    except BaseException:
        state.errors = "Нарушена структура файла adresat.csv"
    except RuntimeError:
        state.errors = "Неудалось открыть файл adresat.csv"
    except ValueError:
        state.errors = "Файл adresat.csv пустой"
    finally:
        if state.errors != None:
            breakWork(state)
            
    #Загружаем responsible.csv
    try:
        config.responsible = checkStructCsv(load_csv('configs/responsible.csv'), "responsible")
    except BaseException: 
        state.errors = "Нарушена структура файла responsible.csv"
    except RuntimeError:
        state.errors = "Неудалось открыть файл responsible.csv"
    except ValueError:
        state.errors = "Файл responsible.csv пустой"
    finally:
        if state.errors != None:
            breakWork(state)
            
    #Загружаем events.csv
    try:
        config.events = checkStructCsv(load_csv('configs/events.csv'), "events")
    except BaseException: 
        state.errors = "Нарушена структура файла events.csv"
    except RuntimeError:
        state.errors = "Неудалось открыть файл events.csv"
    except ValueError:
        state.errors = "Файл events.csv пустой"
    finally:
        if state.errors != None:
            breakWork(state)
            
    #Загружаем validators.csv
    try:
        config.validators = checkStructYaml(load_yaml('configs/validators.yaml'), "validators")
    except RuntimeError:
        state.errors = "Неудалось открыть файл validators.csv"
    except BaseException:
        state.errors = "Нарушена структура файла validators.csv"
    except ValueError:
        state.errors = "Файл validators.csv пустой"
    finally:
        if state.errors != None:
            breakWork(state)
            
    #Загружаем config.yaml
    try:
        config.configureYaml = checkStructYaml(load_yaml('configs/config.yaml'), "config")
    except RuntimeError:
        state.errors = "Неудалось открыть файл config.yaml"
    except BaseException:
        state.errors = "Нарушена структура файла config.yaml"
    except ValueError:
        state.errors = "Файл config.yaml пустой"
    finally:
        if state.errors != None:
            breakWork(state)
            
    #Загружаем creditors_to_process.csv
    try:
        config.creditorsToProcess = checkStructCsv(load_csv('configs/creditors_to_process.csv'), "creditors_to_process")
    except BaseException: 
        state.errors = "Нарушена структура файла creditors_to_process.csv"
    except RuntimeError:
        state.errors = "Неудалось открыть файл creditors_to_process.csv"
    except ValueError:
        state.errors = "Файл creditors_to_process.csv пустой"
    finally:
        if state.errors != None:
            breakWork(state)
    
    return config
