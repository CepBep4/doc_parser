from config import HandlingProcess
from state_manager import SystemState, ConfigState
import fitz  # PyMuPDF
import re

#Читаем пдф
def fileRead(p: HandlingProcess, state: SystemState, config: ConfigState) -> str:
    try:
        # Открытие PDF-файла
        doc = fitz.open(p.path)
        text = ""

        # Считываем текст постранично
        for page in doc:
            text += page.get_text()

        doc.close()

        # Очистка текста:
        # - убираем спецсимволы
        # - заменяем множественные пробелы на один
        # - удаляем управляющие символы
        clean_text = re.sub(r"[^\w\sа-яА-ЯёЁ\-.,!?]", "", text, flags=re.UNICODE)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        
        return clean_text

    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении PDF-файла: {e}")