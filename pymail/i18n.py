import os
from typing import Dict
from .config import ConfigManager


class I18n:
    """国际化支持类"""

    MESSAGES: Dict[str, Dict[str, str]] = {
        "connecting_ssl": {
            "zh": "正在连接到SMTP服务器: {}:{} (SSL)",
            "en": "Connecting to SMTP server: {}:{} (SSL)",
        },
        "connecting_starttls": {
            "zh": "正在连接到SMTP服务器: {}:{} (STARTTLS)",
            "en": "Connecting to SMTP server: {}:{} (STARTTLS)",
        },
        "ssl_failed": {
            "zh": "SSL连接失败，尝试STARTTLS: {}",
            "en": "SSL connection failed, trying STARTTLS: {}",
        },
        "email_sent": {"zh": "邮件发送成功！", "en": "Email sent successfully!"},
        "email_error": {
            "zh": "发送邮件时发生错误: {}",
            "en": "Error occurred while sending email: {}",
        },
        "smtp_info": {"zh": "SMTP服务器: {}", "en": "SMTP server: {}"},
        "port_info": {"zh": "端口: {}", "en": "Port: {}"},
        "sender_info": {"zh": "发件人: {}", "en": "Sender: {}"},
        "recipients_info": {"zh": "收件人: {}", "en": "Recipients: {}"},
        "error_occurred": {
            "zh": "函数 {} 执行时发生错误:\n\n{}",
            "en": "Error occurred in function {}:\n\n{}",
        },
        "timeout_warning": {
            "zh": "由于发送频率限制，此错误通知已被跳过（{}秒内只发送一次）",
            "en": "This error notification was skipped due to rate limiting (only send once within {} seconds)",
        },
        "notification_subject": {
            "zh": "[PyMail] {} 任务:[{}] 程序错误通知",  # 机器ID 和 任务名称
            "en": "[PyMail] {} Task:[{}] Program Error Notification",
        },
        "notification_body": {
            "zh": "发生时间: {}\n\n错误信息:\n{}",
            "en": "Occurred Time: {}\n\nError Information:\n{}",
        },
    }

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
        lang = os.getenv("LANGUAGE", "zh")
        if lang not in ["zh", "en"]:
            lang = "zh"

        message = cls.MESSAGES.get(key, {}).get(lang, f"Message not found: {key}")
        if args:
            try:
                return message.format(*args)
            except Exception:
                return message
        return message
