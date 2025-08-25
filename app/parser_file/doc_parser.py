from config import HandlingProcess
from state_manager import SystemState, ConfigState
import subprocess
import re
import tempfile
from pathlib import Path
from docx import Document

def fileRead(p: "HandlingProcess", state: "SystemState", config: "ConfigState") -> str:
    try:
        # Создаём временную директорию для .docx
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(p.path).resolve()
            output_dir = Path(tmpdir)

            # Конвертация .doc в .docx с помощью LibreOffice
            subprocess.run([
                "soffice", "--headless", "--convert-to", "docx",
                "--outdir", str(output_dir), str(input_path)
            ], check=True)

            # Получаем имя выходного файла
            output_file = output_dir / (input_path.stem + ".docx")
            if not output_file.exists():
                raise FileNotFoundError(f"Конвертация .doc не удалась: {output_file} не найден")

            # Читаем .docx с помощью python-docx
            doc = Document(output_file)
            text = "\n".join([para.text for para in doc.paragraphs])

            # Очистка текста
            clean_text = re.sub(r"[^\w\sа-яА-ЯёЁ\-.,!?]", "", text, flags=re.UNICODE)
            clean_text = re.sub(r"\s+", " ", clean_text).strip()

            return clean_text

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка LibreOffice при конвертации .doc: {e}")
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении .doc файла через LibreOffice: {e}")





