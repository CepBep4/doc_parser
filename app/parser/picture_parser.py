from config import HandlingProcess
from state_manager import SystemState, ConfigState
from PIL import Image
import pytesseract
import re

def fileRead(p: HandlingProcess, state: SystemState, config: ConfigState) -> str:
    try:
        # Загружаем изображение
        image = Image.open(p.path)

        # Распознаём текст
        text = pytesseract.image_to_string(image, lang='rus+eng')  # Поддержка русского и английского

        # Очистка текста
        clean_text = re.sub(r"[^\w\sа-яА-ЯёЁ\-.,!?]", "", text, flags=re.UNICODE)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        return clean_text

    except Exception as e:
        raise RuntimeError(f"Ошибка при распознавании изображения: {e}")

