import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import threading
import time

from .config import ConfigManager, EmailConfig, MachineConfig
from .i18n import I18n

import logging

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self._email_config: EmailConfig = ConfigManager().email_config
        self._machine_config: MachineConfig = ConfigManager().machine_config
        self._last_sent_time = 0
        self._lock = threading.Lock()

    def send_message(
        self,
        message: str,
        task_name: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> bool:
        """
        发送错误信息到配置的收件人列表

        Args:
            error_message: 错误信息
            task_name: 任务名称, 用于默认主题
            subject: 邮件主题，如果为None则使用默认主题

        Returns:
            bool: 发送是否成功
        """
        if not self._machine_config.service_enabled:
            logger.info("Service is disabled, skipping email sending.")
            return False

        current_time = time.time()

        with self._lock:
            # 检查是否在超时时间内
            if current_time - self._last_sent_time < self._email_config.timeout_seconds:
                logger.info(
                    I18n.get_message(
                        "timeout_warning", self._email_config.timeout_seconds
                    )
                )
                return False

            try:
                msg = MIMEMultipart()
                msg["From"] = self._email_config.sender_email
                msg["To"] = ", ".join(self._email_config.recipients)
                str_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg["Subject"] = subject or I18n.get_message(
                    "notification_subject",
                    self._machine_config.id,
                    task_name,
                )
                body = I18n.get_message(
                    "notification_body",
                    str_time,
                    message,
                )

                msg.attach(MIMEText(body, "plain"))

                # 创建安全的SSL上下文
                context = ssl.create_default_context()

                try:
                    # 首先尝试使用SSL连接
                    with smtplib.SMTP_SSL(
                        self._email_config.smtp_server,
                        self._email_config.smtp_port,
                        context=context,
                    ) as server:
                        logger.info(
                            I18n.get_message(
                                "connecting_ssl",
                                self._email_config.smtp_server,
                                self._email_config.smtp_port,
                            )
                        )
                        server.login(
                            self._email_config.sender_email, self._email_config.password
                        )
                        server.send_message(msg)
                except Exception as ssl_error:
                    logger.error(I18n.get_message("ssl_failed", str(ssl_error)))
                    # 如果SSL失败，尝试STARTTLS
                    with smtplib.SMTP(
                        self._email_config.smtp_server, self._email_config.smtp_port
                    ) as server:
                        logger.info(
                            I18n.get_message(
                                "connecting_starttls",
                                self._email_config.smtp_server,
                                self._email_config.smtp_port,
                            )
                        )
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(
                            self._email_config.sender_email, self._email_config.password
                        )
                        server.send_message(msg)

                self._last_sent_time = current_time
                logger.info(I18n.get_message("email_sent"))
                return True

            except Exception as e:
                logger.error(I18n.get_message("email_error", str(e)))
                logger.info(
                    I18n.get_message("smtp_info", self._email_config.smtp_server)
                )
                logger.info(I18n.get_message("port_info", self._email_config.smtp_port))
                logger.info(
                    I18n.get_message("sender_info", self._email_config.sender_email)
                )
                logger.info(
                    I18n.get_message("recipients_info", self._email_config.recipients)
                )
                return False


# 全局单例
email_sender = EmailSender()
