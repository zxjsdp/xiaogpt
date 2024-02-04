"""Qwen bot"""

from __future__ import annotations

import json
import logging
from http import HTTPStatus
from typing import Any

from rich import print

from xiaogpt.bot.base_bot import BaseBot, ChatHistoryMixin
from xiaogpt.config import LOGGING_FILENAME


class QwenBot(ChatHistoryMixin, BaseBot):
    name = "阿里通义千问 AI"

    def __init__(self, qwen_key: str) -> None:
        import dashscope
        from dashscope.api_entities.dashscope_response import Role

        self.history = []
        dashscope.api_key = qwen_key

        logging.basicConfig(
            filename=LOGGING_FILENAME,
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            level=logging.INFO)
        # 避免 logger 写入的文件中显示大量 miservice 的日志
        logging.getLogger('miservice').setLevel(logging.WARNING)
        self.logger = logging.getLogger('qwen_bot')

    @classmethod
    def from_config(cls, config):
        return cls(qwen_key=config.qwen_key)

    async def ask(self, query, **options):
        from dashscope import Generation
        from dashscope.api_entities.dashscope_response import Role

        # from https://help.aliyun.com/zh/dashscope/developer-reference/api-details
        self.history.append({"role": Role.USER, "content": query})

        self.logger.info('[user]: ' + query)
        self.logger.info('[传入LLM的会话历史]: ' + json.dumps(self.history, ensure_ascii=False))

        response = Generation.call(
            Generation.Models.qwen_max,
            messages=self.history,
            result_format="message",  # set the result to be "message" format.
        )
        if response.status_code == HTTPStatus.OK:
            # append result to messages.
            content = response.output.choices[0]["message"]["content"]
            self.history.append(
                {
                    "role": response.output.choices[0]["message"]["role"],
                    "content": content,
                }
            )
            # keep last five
            first_history = self.history.pop(0)
            self.history = [first_history] + self.history[-5:]
            print(content)
            self.logger.info('[' + response.output.choices[0]["message"]["role"] + ']: ' + content)
            return content
        else:
            resp_info = "Request id: {}, Status code: {}, error code: {}, \
                error message: {}".format(
                response.request_id,
                response.status_code,
                response.code,
                response.message
            )

            print(resp_info)
            self.logger.info(resp_info)

            # we need to pop the wrong history
            print(f"Will pop the wrong question {query}")
            self.history.pop()
            return "没有返回"

    async def ask_stream(self, query: str, **options: Any):
        from dashscope import Generation
        from dashscope.api_entities.dashscope_response import Role

        self.history.append({"role": Role.USER, "content": query})
        responses = Generation.call(
            Generation.Models.qwen_max,
            messages=self.history,
            result_format="message",  # set the result to be "message" format.
            stream=True,
            incremental_output=True,  # get streaming output incrementally
        )
        full_content = ""  # with incrementally we need to merge output.
        role = None
        for response in responses:
            if response.status_code == HTTPStatus.OK:
                content = response.output.choices[0]["message"]["content"]
                full_content += content
                if not role:
                    role = response.output.choices[0]["message"]["role"]
                print(content, end="")
                self.logger.info('[' + response.output.choices[0]
                              ["message"]["role"] + ']: ' + content)
                yield content
            else:
                resp_info = "Request id: {}, Status code: {}, error code: {}, \
                    error message: {}".format(
                    response.request_id,
                    response.status_code,
                    response.code,
                    response.message,
                )
                print(resp_info)
                self.logger.info(resp_info)

        self.history.append({"role": role, "content": full_content})
        first_history = self.history.pop(0)
        self.history = [first_history] + self.history[-5:]
