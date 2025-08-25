from config import HandlingProcess
from state_manager import SystemState, ConfigState
from docx import Document
import re
import traceback

def fileRead(p: HandlingProcess, state: SystemState, config: ConfigState) -> str:
    try:
        # Загружаем документ
        doc = Document(p.path)

        # Собираем текст из всех параграфов
        text = "\n".join([para.text for para in doc.paragraphs])

        # Очистка текста
        clean_text = re.sub(r"[^\w\sа-яА-ЯёЁ\-.,!?]", "", text, flags=re.UNICODE)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        
        print(clean_text, 'text')
        return clean_text

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Ошибка при чтении DOC/DOCX-файла: {e}")
