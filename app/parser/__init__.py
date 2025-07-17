from state_manager import ConfigState, SystemState
from config import HandlingProcess
from utils import breakWork, logErrorJson

#Импорт парсеров
from parser.pdf_parser import fileRead as rpdf
from parser.doc_parser import fileRead as rdoc
from parser.docx_parser import fileRead as rdocx
from parser.xlsx_parser import fileRead as rxlsx
from parser.picture_parser import fileRead as rpicture

import datetime

#Временная затычка
def systemNotValidExtetion(*args):
    return "handled"
    
ALLOWED_EXTENTION = {
    "pdf":rpdf,
    "docx":rdocx,
    "doc":rdoc,
    "xlsx":rxlsx,
    "jpg":rpicture,
    "png":rpicture
}

#Читаем текст из всех файлов
def readTextFromFiles(state: SystemState, config: ConfigState, listFiles: list[HandlingProcess]):
    for p in listFiles:
        try:
            #Пропускаем файлы с ошибками
            if p.status != "ok":
                continue
            
            p.text = ALLOWED_EXTENTION[p.extention](p, state, config)
            
            #Обновляем статус
            p.updateStatus(
                status="ok",
                date=datetime.datetime.now().isoformat(),
                stage="parser",
                comment="Извлекаем и фильтруем текст"
            )
        except Exception as error:
            #Логируем ошибку
            logErrorJson(
                p.path,
                "parser",
                str(error)
            )
            
            #Обновляем статус
            p.updateStatus(
                status="critical_error",
                date=datetime.datetime.now().isoformat(),
                stage="parser",
                error_msg=str(error),
                comment="Извлекаем и фильтруем текст"
            )
      
    #Завершаем работу если все файлы с ошибками     
    if "ok" not in [x.status for x in listFiles]:
        state.errors = "Не осталось файлов для обработки"
        breakWork(state)
        
    return listFiles