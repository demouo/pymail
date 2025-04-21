import os
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import yaml
from .i18n import I18n


@dataclass
class EmailConfig:
    smtp_server: str
    smtp_port: int
    sender_email: str
    password: str
    recipients: List[str]
    time_interval: Optional[int] = None


@dataclass
class MachineConfig:
    machine_id: str = "Specific-Id-Of-PyMail"
    project_id: str = "pymail"
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
        load_dotenv(dotenv_path=f"{os.getcwd()}/.env")

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
            time_interval=int(
                os.getenv("EMAIL_TIME_INTERVAL", config.get("time_interval", 300))
            ),
        )

        # 创建MachineConfig实例，优先使用环境变量
        self._machine_config = MachineConfig(
            machine_id=os.getenv(
                "MACHINE_ID", config.get("machine_id", "Specific-Id-Of-PyMail")
            ),
            project_id=os.getenv("PROJECT_ID", config.get("project_id", "pymail")),
            service_enabled=str(
                os.getenv(
                    "MACHINE_SERVICE_ENABLED",
                    config.get("machine_service_enabled", "True"),
                )
            ).lower()
            != "false",
        )

        # 发现没有配置文件，则输出提示信息
        if (
            self._email_config.sender_email == ""
            and self._email_config.password == ""
            and self._email_config.recipients == []
        ):
            raise ValueError(
                "No pymail configuration found, please configure the following in the .env file:\nSMTP_SERVER=your_smtp_server\nSMTP_PORT=your_smtp_port\nSENDER_EMAIL=your_sender_email\nEMAIL_PASSWORD=your_email_password\nEMAIL_RECIPIENTS=your_email_recipients_separated_by_comma\nOther configurations please refer to the pymail_config.yaml.example file in https://github.com/demouo/pymail/blob/main/pymail_config.yaml.example"
            )

    @property
    def email_config(self) -> EmailConfig:
        return self._email_config

    @property
    def machine_config(self) -> MachineConfig:
        return self._machine_config
