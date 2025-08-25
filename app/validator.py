from state_manager import ConfigState, SystemState
from config import HandlingProcess
from datetime import datetime 
from utils import breakWork
import re

def normalize_ip_number(ip_number: str | None) -> str:
    if not ip_number:
        return "no_ip"
    return re.sub(r"[^\w\-]", "-", ip_number.strip())

import re

def validate_ai_record(record: dict, validators: dict, config: ConfigState) -> list[str]:
    errors = []

    # Дата
    if not re.match(validators["date"]["regex"], record.get("Дата", "")):
        errors.append("Некорректная дата")

    # Номер ИП
    if not re.match(validators["number_ip"]["regex"], record.get("Серия ИП", "")):
        errors.append("Некорректный номер ИП")

    # Адресат
    if record.get("Адресат мероприятия") not in config.adresat:
        errors.append("Недопустимый адресат")

    # Тип мероприятия
    if record.get("Тип мероприятия") not in config.events:
        errors.append("Недопустимый тип мероприятия")

    return errors


def generate_unique_filename(ip_number: str | None, index: int, ext: str = ".pdf") -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    norm_ip = normalize_ip_number(ip_number)
    return f"{date_str}_{norm_ip}_{index:03}{ext}"

def validateFiles(state: SystemState, config: ConfigState, listFiles: list[HandlingProcess]):
    #Обработанные ключи
    seenKeys = set()

    #Валидируем каждый файл
    for index, p in enumerate(listFiles, start=1):
        #Пропускаем файлы с ошибками
        if p.status != "ok":
            continue
        
        required = ["Серия ИП", "Дата", "Тип мероприятия", "Адресат мероприятия", "Цель мероприятия"]
        
        # Проверка обязательных полей
        is_complete = all(p.ai.get(f) for f in required)
        p.ai["Status"] = "ok" if is_complete else "incomplete"
        
        # Если предварительно ок — запускаем валидацию
        if p.ai["Status"] == "ok":
            validation_errors = validate_ai_record(p.ai, config.validators, config)
            if validation_errors:
                p.ai["Status"] = "ok"
        
        # Проверка на дубликат
        key = (p.ai.get("Серия ИП"), p.ai.get("Дата"), p.ai.get("Тип мероприятия"))
        if p.ai["Status"] == "ok" and key in seenKeys:
            p.ai["Status"] = "duplicate"
        elif p.ai["Status"] == "ok":
            seenKeys.add(key)
        
        # Имя файла
        ip_number = p.ai.get("Серия ИП")
        p.ai["Файл"] = generate_unique_filename(ip_number, index)
        
        # Служебные поля
        p.ai["Оригинал"] = p.path
        p.ai["Обработано"] = datetime.now().isoformat()
        
        #Обновляем статус
        p.updateStatus(
            status="ok",
            date=datetime.now().isoformat(),
            stage="validator",
            comment="Валидируем данные"
        )
        
    #Завершаем работу если все файлы с ошибками     
    if "ok" not in [x.status for x in listFiles]:
        state.errors = "Не осталось файлов для обработки"
        breakWork(state)

    return listFiles