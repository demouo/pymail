import os
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import yaml


@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    sender_email: str
    password: str
    recipients: List[str]
    timeout_seconds: int = 300  # 默认5分钟超时


@dataclass
class MachineConfig:
    id: str = "Specific-Id-Of-PyMail"
    service_enabled: bool = True


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._email_config = None
            cls._instance._machine_config = None
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        # 首先尝试从环境变量加载
        load_dotenv()

        # 尝试从YAML文件加载配置
        config_path = os.getenv("PYMAIL_CONFIG_PATH", "pymail_config.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
        else:
            config = {}

        if config is None:
            config = {}

        # 创建EmailConfig实例，优先使用环境变量
        self._email_config = EmailConfig(
            smtp_server=os.getenv(
                "SMTP_SERVER", config.get("smtp_server", "smtp.gmail.com")
            ),
            smtp_port=int(os.getenv("SMTP_PORT", config.get("smtp_port", 587))),
            sender_email=os.getenv("SENDER_EMAIL", config.get("sender_email", "")),
            password=os.getenv("EMAIL_PASSWORD", config.get("password", "")),
            recipients=(
                os.getenv("EMAIL_RECIPIENTS", "").split(",")
                if os.getenv("EMAIL_RECIPIENTS")
                else config.get("recipients", [])
            ),
            timeout_seconds=int(
                os.getenv("EMAIL_TIMEOUT", config.get("timeout_seconds", 300))
            ),
        )

        # 创建MachineConfig实例，优先使用环境变量
        self._machine_config = MachineConfig(
            id=os.getenv(
                "MACHINE_ID", config.get("machine_id", "Specific-Id-Of-PyMail")
            ),
            service_enabled=str(
                os.getenv(
                    "MACHINE_SERVICE_ENABLED",
                    config.get("machine_service_enabled", "True"),
                )
            ).lower()
            != "false",
        )

    @property
    def email_config(self) -> EmailConfig:
        return self._email_config

    @property
    def machine_config(self) -> MachineConfig:
        return self._machine_config
