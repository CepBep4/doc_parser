from state_manager import ConfigState, SystemState
from config import HandlingProcess, build_structured_prompt
from utils import breakWork, logErrorJson
import datetime
import requests
import json
  
def requestGPT(prompt: str) -> dict:   
    # 🔑 API-ключ для YandexGPT
    API_KEY = "AQVNyQJhwi8hKd4HQqSaQrliecSmTEwj5JQnKZXj"

    # 📂 Folder ID для YandexGPT
    FOLDER_ID = "b1g8tsvuq53o5os9bviv"

    # URL для обращения к YandexGPT
    YANDEX_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    # Формируем тело запроса для YandexGPT
    data = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.2,
            "maxTokens": "1000"
        },
        "messages": [
            {"role": "system", "text": "Ты опытный аналитик документов. Отвечай строго в JSON."},
            {"role": "user", "text": prompt}
        ]
    }

    # Заголовки для запроса
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {API_KEY}"
    }

    try:
        # Делаем запрос к YandexGPT
        response = requests.post(YANDEX_URL, headers=headers, json=data)
        response.raise_for_status()  # Проверяем статус ответа
        
        response_data = response.json()
        
        # Пытаемся извлечь текст из ответа YandexGPT
        raw_text = ""
        if "result" in response_data and "alternatives" in response_data["result"]:
            alternatives = response_data["result"]["alternatives"]
            if alternatives and "message" in alternatives[0]:
                raw_text = alternatives[0]["message"].get("text", "").strip()
        
        if not raw_text:
            # Попробуем другие возможные пути в ответе
            if "text" in response_data:
                raw_text = response_data["text"].strip()
            elif "message" in response_data:
                raw_text = response_data["message"].strip()
            else:
                # Выведем весь ответ для анализа
                raw_text = str(response_data)
        
        if not raw_text or raw_text == "None":
            raise ValueError("Пустой ответ от YandexGPT")

        # Очищаем текст от markdown обрамления
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith('```') and cleaned_text.endswith('```'):
            # Убираем markdown блок
            cleaned_text = cleaned_text[3:-3].strip()
            # Убираем возможные языковые метки (json, python и т.д.)
            if '\n' in cleaned_text:
                first_line = cleaned_text.split('\n')[0].strip()
                if first_line in ['json', 'python', 'javascript']:
                    cleaned_text = '\n'.join(cleaned_text.split('\n')[1:]).strip()
        
        # Пытаемся выделить JSON из текста
        try:
            # Прямая попытка
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Попытка вырезать JSON вручную
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}')
            if start != -1 and end != -1:
                json_text = cleaned_text[start:end+1]
                return json.loads(json_text)
            
            # Попробуем найти JSON массив
            start = cleaned_text.find('[')
            end = cleaned_text.rfind(']')
            if start != -1 and end != -1:
                json_text = cleaned_text[start:end+1]
                return json.loads(json_text)
            
            # Если JSON не найден, попробуем создать простую структуру
            return {"raw_response": cleaned_text, "parsed": False}

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка сетевого запроса к YandexGPT: {e}")
    except Exception as e:
        raise RuntimeError(f"Ошибка запроса к YandexGPT: {e}")

def neuroHandler(state: SystemState, config: ConfigState, listFiles: list[HandlingProcess]):
    for p in listFiles:
        try:
            #Пропускаем файлы с ошибками
            if p.status != "ok":
                continue
            
            p.ai = requestGPT(build_structured_prompt(p.text, p.direction))
            if p.ai is None:
                raise BaseException("Пустой dict после запроса к нейросети")
            
            #Обновляем статус
            p.updateStatus(
                status="ok",
                date=datetime.datetime.now().isoformat(),
                stage="ai_client",
                comment="Обрабатываем нейросетью"
            )
            
        except Exception as error:
            #Записываем в log
            logErrorJson(
                p.path,
                "ai_client",
                str(error)
            )
            
            #Обновляем статус
            p.updateStatus(
                status="critical_error",
                date=datetime.datetime.now().isoformat(),
                stage="ai_client",
                error_msg=str(error),
                comment="Обрабатываем нейросетью"
            )
            
    #Завершаем работу если все файлы с ошибками     
    if "ok" not in [x.status for x in listFiles]:
        state.errors = "Не осталось файлов для обработки"
        breakWork(state)
            
    return listFiles