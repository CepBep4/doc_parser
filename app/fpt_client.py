from state_manager import ConfigState, SystemState
from config import HandlingProcess
from utils import logErrorJson
import json
from datetime import datetime
import os
from ftplib import FTP, error_perm

def sendTo1cFtp(state: SystemState, config: ConfigState, listFiles: list[HandlingProcess]) -> list[HandlingProcess]:
    ftp_host = "192.168.207.98"
    ftp_user = "parser_ftp"
    ftp_pass = "ftpparse"
    ftp_dir  = "./doc_parser/"

    # Собираем данные
    for p in listFiles:
        if p.exportName != "":
            try:
                with open(p.exportName, encoding="utf-8") as f:
                    p.send1c = json.loads(f.read())
            except Exception as error:
                logErrorJson(p.path, "1c_send", str(error))
                p.updateStatus(
                    status="critical_error",
                    date=datetime.now().isoformat(),
                    stage="1c_send",
                    error_msg=str(error),
                    comment="Ошибка при чтении выгрузка_XXXX.json"
                )

    # Соединение с FTP
    try:
        ftp = FTP(ftp_host, timeout=30)
        ftp.login(ftp_user, ftp_pass)
        ftp.cwd(ftp_dir)
    except Exception as error:
        for p in listFiles:
            p.updateStatus(
                status="critical_error",
                date=datetime.now().isoformat(),
                stage="1c_send",
                error_msg=str(error),
                comment="Не удалось подключиться к FTP"
            )
        return listFiles

    # Загрузка файлов
    for p in listFiles:
        try:
            if p.status == "ok":
                print(p)
                file_name = os.path.basename(p.exportName)
                with open(p.exportName, "rb") as f:
                    ftp.storbinary(f"STOR {file_name}", f)

                p.updateStatus(
                    status="complete",
                    date=datetime.now().isoformat(),
                    stage="1c_send",
                    error_msg="",
                    comment="Файл успешно загружен на FTP"
                )
        except Exception as error:
            logErrorJson(p.path, "1c_send", str(error))
            p.updateStatus(
                status="critical_error",
                date=datetime.now().isoformat(),
                stage="1c_send",
                error_msg=str(error),
                comment="Не удалось загрузить файл на FTP"
            )

    ftp.quit()
    return listFiles
