from state_manager import ConfigState, SystemState
from config import STATUS_CHECK, HandlingProcess
from utils import findPathFromPattern, checkAgainHandling, breakWork, logNotProcessed
import os
import datetime

#Рекурсивная функция для поиска файлов
def walkOnDir(dirPath: str, findedFiles: list, config: ConfigState, debt: str, credit: str) -> str:
    if not os.path.isdir(dirPath):
        #Получаем расширение
        extentionFile = dirPath.split('.')[-1].lower()
        
        #Проверка на повторную обработку
        if not checkAgainHandling(dirPath):
            #Проверяем расширение
            if extentionFile in config.formats:
                #Проверяем размер
                if os.path.getsize(dirPath) > 0:
                    p = HandlingProcess(
                        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        path=dirPath,
                        extention=extentionFile,
                        debt=debt,
                        credit=credit,
                        text="",
                        ai={},
                        status = "ok",
                        exportName="",
                        direction = ""
                    )
                    #Обновляем статус
                    p.updateStatus(
                        status="ok",
                        date=datetime.datetime.now().isoformat(),
                        stage="filewalker",
                        comment="Отбираем файлы для обработки"
                    )
                    
                    #Добавляем в общий список
                    findedFiles.append(p)
                else:
                    #Записываем лог
                    logNotProcessed(
                        file_path=dirPath, 
                        reason="Размер файла 0", 
                        ext=extentionFile,
                        creditor=credit,
                        debtor=debt
                    )
            else:
                #Записываем в лог
                logNotProcessed(
                    file_path=dirPath, 
                    reason="Недопустимое расширение", 
                    ext=extentionFile,
                    creditor=credit,
                    debtor=debt
                )
        else:
            #Повторная обработка
            logNotProcessed(
                file_path=dirPath, 
                reason="Повторная обработка", 
                ext=extentionFile,
                creditor=credit,
                debtor=debt
            )
    else:
        for directory in os.listdir(dirPath):
            walkOnDir(dirPath+'/'+directory, findedFiles, config, debt, credit)

#Проходимся по всем путям, отбираем нужные файлы
def getNeedPath(state: SystemState, config: ConfigState) -> list[dict]:
    responseFiles = []
    filterPath = [config.creditorsToProcess[x]["link"] for x in config.creditorsToProcess if STATUS_CHECK[config.creditorsToProcess[x]["status"]]]
    criditors = [x for x in config.creditorsToProcess if STATUS_CHECK[config.creditorsToProcess[x]["status"]]]
    
    #Обрабатываем найденные пути
    for dirPath, creditor in zip(filterPath, criditors):
        try:
            pathToDir = findPathFromPattern(dirPath)
            
            #Перебираем должников
            for debtor in os.listdir(pathToDir):
                #Находим все файлы должника, записываем в responseFiles
                walkOnDir(pathToDir+'/'+debtor, responseFiles, config, debtor, creditor)   
                
        except RuntimeError:
            print("Пути нет")
            
    #Отпускаем файлы для обработки
    if len(responseFiles) == 0:
        state.errors = "Нет подходящих файлов для обработки"
        breakWork(state)
    return responseFiles
        