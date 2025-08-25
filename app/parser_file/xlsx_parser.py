from config import HandlingProcess
from state_manager import SystemState, ConfigState
import openpyxl
import re

def fileRead(p: HandlingProcess, state: SystemState, config: ConfigState) -> str:
    try:
        # Загружаем книгу
        wb = openpyxl.load_workbook(p.path, read_only=True, data_only=True)
        text_parts = []

        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if cell is not None:
                        text_parts.append(str(cell))

        raw_text = " ".join(text_parts)

        # Очистка текста
        clean_text = re.sub(r"[^\w\sа-яА-ЯёЁ\-.,!?]", "", raw_text, flags=re.UNICODE)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        return clean_text

    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении XLSX-файла: {e}")
