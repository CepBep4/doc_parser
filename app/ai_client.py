from state_manager import ConfigState, SystemState
from config import HandlingProcess, build_structured_prompt
from utils import breakWork, logErrorJson
import datetime
import openai
import json

def requestGPT(prompt: str) -> dict:    
    openai.api_key = API_KEY

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # можно заменить на "gpt-3.5-turbo", если нужно
            messages=[
                {"role": "system", "content": "Ты опытный аналитик документов. Отвечай строго в JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000
        )

        raw_text = response.choices[0].message.content.strip()

        # Пытаемся выделить JSON из текста (на случай, если вернулся с обёрткой)
        try:
            # Прямая попытка
            return json.loads(raw_text)
        except json.JSONDecodeError:
            # Попытка вырезать JSON вручную
            start = raw_text.find('{')
            end = raw_text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(raw_text[start:end+1])
            raise ValueError("Ответ не содержит валидного JSON.")

    except Exception as e:
        raise RuntimeError(f"Ошибка запроса к GPT: {e}")

def neuroHandler(state: SystemState, config: ConfigState, listFiles: list[HandlingProcess]):
    for p in listFiles:
        try:
            #Пропускаем файлы с ошибками
            if p.status != "ok":
                continue
            
            p.ai = requestGPT(build_structured_prompt(p.text))
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