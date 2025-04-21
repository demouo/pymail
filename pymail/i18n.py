import os
from typing import Dict, Any
import yaml
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class I18n:
    """国际化支持类"""

    _instance = None
    _messages: Dict[str, Dict[str, str]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_messages()
        return cls._instance

    def _load_messages(self) -> None:
        """从 YAML 文件加载消息"""
        try:
            # 获取 i18n 目录的路径
            current_dir = Path(__file__).parent
            messages_file = current_dir / "i18n" / "messages.yaml"

            # 读取 YAML 文件
            with open(messages_file, "r", encoding="utf-8") as f:
                messages = yaml.safe_load(f)

            if not messages or not isinstance(messages, dict):
                logger.error("Invalid messages format in messages.yaml")
                return

            # 重组消息格式为 {message_key: {lang: message}}
            for lang, lang_messages in messages.items():
                for key, message in lang_messages.items():
                    if key not in self._messages:
                        self._messages[key] = {}
                    self._messages[key][lang] = message

        except FileNotFoundError:
            logger.error("Messages file not found: messages.yaml")
        except yaml.YAMLError as e:
            logger.error(f"Error parsing messages.yaml: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading messages: {e}")

    @classmethod
    def get_message(cls, key: str, *args) -> str:
        """
        获取指定语言的消息

        Args:
            key: 消息键
            *args: 格式化参数

        Returns:
            str: 格式化后的消息
        """
        # 确保实例已创建并加载消息
        if not cls._instance:
            cls._instance = cls()

        # 获取当前语言
        lang = os.getenv("LANGUAGE", "zh")
        if lang not in ["zh", "en"]:
            lang = "zh"

        # 获取消息
        message = cls._instance._messages.get(key, {}).get(
            lang, f"Message not found: {key}"
        )

        # 格式化消息
        if args:
            try:
                return message.format(*args)
            except Exception as e:
                logger.error(f"Error formatting message '{key}': {e}")
                return message
        return message


# 全局单例
i18n = I18n()
