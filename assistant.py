# assistant.py
import json
from logger import get_logger

logger = get_logger("assistant")
from dialog_logger import DialogLogger

class Assistant:
    def __init__(self, client, model, instructions, tools=None, functions=None):
        self.client = client
        self.model = model
        self.instructions = instructions
        self.tools = tools or []
        self.functions = functions or {}
        self.dialog_logger = DialogLogger()

        self.messages = [
            {"role": "system", "content": instructions}
        ]
        self.dialog_logger.log_message(self.messages[0])
        logger.info(f"Assistant initialized with model: {model}")

    def __call__(self, user_text):
        self.messages.append({"role": "user", "content": str(user_text)})
        logger.info(f"Запрос пользователя: {str(user_text)}")
        step = 1
        while True:
            logger.info(f"Шаг {step}:")
            params = {
                "model": self.model,
                "messages": self.messages,
                "temperature": 0.1,
                "top_p": 0.3,
              #  "max_tokens": 4096,
            }

            if self.tools:
                params["tools"] = self.tools
                params["tool_choice"] = "auto"
                logger.debug(f"Подключены инструменты: {self.tools}")
            res = self.client.chat.completions.create(**params)
            msg = res.choices[0].message

            if msg.tool_calls:
                self.messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                })
                self.dialog_logger.log_message(self.messages[-1])
                for tc in msg.tool_calls:
                    func_name = tc.function.name
                    func = self.functions.get(func_name)

                    if func is None:
                        result = f"Функция {func_name} не зарегистрирована"
                    else:
                        try:
                            args = json.loads(tc.function.arguments or "{}")
                            logger.info(f"Вызов функции {func_name} с аргументами: {args}")
                            result = func(**args)
                            logger.info(f"Функции {func_name} вызвана ")
                            logger.debug(f"Результат функции {func_name}: {result}")

                        except Exception as e:
                            logger.warning(f"Ошибка при вызове функции {func_name} с аргументами: {args}\n: {e}")
                            result = f"Ошибка: {e}"

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result)
                    })
                    self.dialog_logger.log_message(self.messages[-1])
                step += 1
                continue

            reply = msg.content or ""
            self.messages.append({
                "role": "assistant",
                "content": reply
            })
            self.dialog_logger.log_message(self.messages[-1])
            # for m in self.messages:
            #     print(m)
            return reply