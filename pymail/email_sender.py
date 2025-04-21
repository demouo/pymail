from collections import defaultdict
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
import threading
import time
import queue

from .config import ConfigManager, EmailConfig, MachineConfig
from .i18n import I18n

import logging

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self._email_config: EmailConfig = ConfigManager().email_config
        self._machine_config: MachineConfig = ConfigManager().machine_config
        self._last_sent_time = defaultdict(float)
        self._lock = threading.Lock()
        self._start_time = time.time()

        # 邮件队列
        self._mail_queue = queue.Queue()
        # 邮件发送线程
        self._mail_thread = threading.Thread(
            target=self._process_mail_queue, daemon=True
        )
        self._mail_thread.start()

    def _process_mail_queue(self):
        """处理邮件队列的后台线程"""
        while True:
            try:
                # 从队列中获取邮件
                msg = self._mail_queue.get()
                if msg is None:  # 停止信号
                    break

                # 发送邮件
                self._send_message_impl(msg)

                # 标记任务完成
                self._mail_queue.task_done()

                # 添加小延迟，避免发送太快
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error processing mail queue: {e}")
                continue

    def send(
        self,
        type: str,
        message: str,
        task_name: Optional[str],
        subject: Optional[str] = None,
        time_interval: Optional[int] = None,
    ):
        current_seconds = time.time()
        time_interval = time_interval or self._email_config.time_interval
        if current_seconds - self._last_sent_time[task_name] < time_interval:
            return
        time_duration = current_seconds - self._start_time
        time_duration = time.strftime("%H:%M:%S", time.gmtime(time_duration))

        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if type == "error":
            self.send_error(
                message=message,
                subject=subject,
                task_name=task_name,
                curr_time=curr_time,
                time_duration=time_duration,
            )
        elif type == "stats":
            self.send_stats(
                message=message,
                subject=subject,
                task_name=task_name,
                curr_time=curr_time,
                time_duration=time_duration,
            )
        else:
            raise ValueError(f"Invalid email type: {type}")

        self._last_sent_time[task_name] = current_seconds

    def send_error(
        self,
        message: str,
        task_name: Optional[str],
        subject: Optional[str] = None,
        curr_time: Optional[str] = None,
        time_duration: Optional[str] = None,
    ):
        msg = MIMEMultipart()
        msg["From"] = self._email_config.sender_email
        msg["To"] = ", ".join(self._email_config.recipients)
        msg["Subject"] = subject or I18n.get_message(
            "error_notification_subject",
            self._machine_config.machine_id,
            self._machine_config.project_id,
            task_name,
        )
        body = I18n.get_message(
            "error_notification_body",
            curr_time,
            message,
        )

        msg.attach(MIMEText(body, "plain"))
        self.send_message(msg)

    def send_stats(
        self,
        message: str = "",
        task_name: Optional[str] = None,
        subject: Optional[str] = None,
        curr_time: Optional[str] = None,
        time_duration: Optional[str] = None,
    ):
        msg = MIMEMultipart()
        msg["From"] = self._email_config.sender_email
        msg["To"] = ", ".join(self._email_config.recipients)
        msg["Subject"] = subject or I18n.get_message(
            "stats_notification_subject",
            self._machine_config.machine_id,
            self._machine_config.project_id,
            task_name,
        )
        body = I18n.get_message(
            "stats_notification_body",
            curr_time,
            time_duration,
            message,
        )
        msg.attach(MIMEText(body, "plain"))
        self.send_message(msg)

    def send_message(
        self,
        msg: MIMEMultipart,
    ) -> None:
        """
        将邮件加入发送队列
        """
        if not self._machine_config.service_enabled:
            logger.info("Service is disabled, skipping email sending.")
            return

        # 将邮件加入队列
        self._mail_queue.put(msg)

    def _send_message_impl(
        self,
        msg: MIMEMultipart,
    ) -> None:
        """
        实际的邮件发送实现
        """
        with self._lock:
            try:
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

                logger.info(I18n.get_message("email_sent"))

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

    def __del__(self):
        """清理资源"""
        # 发送停止信号
        if hasattr(self, "_mail_queue"):
            self._mail_queue.put(None)
        # 等待队列处理完成
        if hasattr(self, "_mail_thread"):
            self._mail_thread.join(timeout=1.0)


# 全局单例
email_sender = EmailSender()
