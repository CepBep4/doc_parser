#Вспомогательные функции
from utils import checkSystemBeforeStart, breakWork, checkPause

#Структура для хранения состояний
from state_manager import SystemState

#Функция для загрузки конфига
from config import loadConfigs

#Перебор файлов
from filewalker import getNeedPath

#Чтение текста из файлов
from parser_file import readTextFromFiles

#Модль для работы с нейросетью
from ai_client import neuroHandler

#Модуль для валидации файла
from validator import validateFiles

#Моудль для экспорта
from exporter import exportFiles

#Модуль для отправки в 1c
from fpt_client import sendTo1cFtp

#Инициализация состояний
state = SystemState()

#Проверка перед запуском
with state.timeManager("Проверка системы"):
    if not checkPause(state): checkSystemBeforeStart(state)

#Читаем справочники, загружаем конфиги
with state.timeManager("Проверка и чтение справочников"):
    if not checkPause(state): config = loadConfigs(state)

#Обходим нужные папки, filewalker
with state.timeManager("Сбор подходящих файлов"):
    if not checkPause(state): listFiles = getNeedPath(state, config)

#Вытягиваем текст из всех файлов, parser
with state.timeManager("Чтение текста из файлов"):
    if not checkPause(state): listFiles = readTextFromFiles(state, config, listFiles)

#Передаём в нейросеть, ai_client
with state.timeManager("Обработка нейросетью"):
    if not checkPause(state): listFiles = neuroHandler(state, config, listFiles)
    
#Валидируем обработку нейросетью, validator
# ! *Временно не используем* !
# with state.timeManager("Валидация обработки нейросетью"):
#     if not checkPause(state): listFiles = validateFiles(state, config, listFiles)
    
#Экспортируем
with state.timeManager("Экспорт данных"):
    if not checkPause(state): listFiles = exportFiles(state, config, listFiles)
    
#Отправляем в 1C (Временно закоментировано)
# with state.timeManager("Отправляем в 1с"):
#     if not checkPause(state): listFiles = sendTo1cFtp(state, config, listFiles)
    
#Завершаем работу
breakWork(state)