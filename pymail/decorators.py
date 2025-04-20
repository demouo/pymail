import functools
import traceback
from typing import Optional, Callable
from .email_sender import email_sender
from .i18n import I18n


def email_on_error(
    task_name: Optional[str] = None,
    subject: Optional[str] = None,
):
    """
    装饰器：当函数发生异常时发送邮件通知

    Args:
        subject: 可选的邮件主题
        task_name: 可选的任务名称
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = traceback.format_exc()
                email_sender.send_message(
                    message=I18n.get_message(
                        "error_occurred", func.__name__, error_info
                    ),
                    task_name=task_name,
                    subject=subject,
                )
                raise e  # 重新抛出异常

        return wrapper

    return decorator
