import functools
import traceback
from typing import Optional, Callable, Any
from .email_sender import email_sender
from .i18n import I18n
from .stats import stats_manager


def email_on_error(
    task_name: Optional[str] = None,
    subject: Optional[str] = None,
    time_interval: Optional[int] = None,
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
                email_sender.send(
                    type="error",
                    message=I18n.get_message(
                        "error_occurred", func.__name__, error_info
                    ),
                    task_name=(task_name or func.__name__),
                    subject=subject,
                    time_interval=time_interval,
                )
                raise e  # 重新抛出异常

        return wrapper

    return decorator


def track_stats(
    task_name: Optional[str] = None,
    subject: Optional[str] = None,
    time_interval: int = 3600,
    success_condition: Optional[Callable] = None,
    ignore_success_condition_failed: bool = False,
):
    """
    函数执行统计装饰器

    Args:
        task_name: 可选的任务名称
        subject: 可选的邮件主题
        time_interval: 时间间隔，单位为秒
        success_condition: 成功条件，为True时记录成功，为False时记录失败
        ignore_success_condition_failed: 是否忽略成功条件失败，如果为True，则不记录这种失败, 即只认为报错才是失败，其他不算失败

    跟踪记录函数的执行情况，包括：
    - 总调用次数
    - 成功次数
    - 失败次数
    - 失败率

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
                # 此处成功条件要反复检查，是因为不能对原程序造成干扰
                if success_condition:
                    try:
                        if success_condition(result):
                            stats_manager.record_execution(func.__name__, True)
                        else:
                            # 失败了，且不忽略失败，则记录失败
                            # 适用场景：虽然失败了，但是不计入失败次数，只有报错时记录失败
                            if not ignore_success_condition_failed:
                                stats_manager.record_execution(func.__name__, False)
                    except Exception as e:
                        traceback.print_exc()
                        print(f"[pymail] track_stats success condition error: {e}")
                        stats_manager.record_execution(func.__name__, False)
                        raise e
                else:
                    stats_manager.record_execution(func.__name__, True)
                return result
            except Exception as e:
                stats_manager.record_execution(func.__name__, False)
                raise e
            finally:
                stats = stats_manager.get_stats(func.__name__)
                email_sender.send(
                    type="stats",
                    subject=subject,
                    task_name=(task_name or func.__name__),
                    message=I18n.get_message(
                        "format_stats_summary",
                        func.__name__,
                        stats.total_count,
                        stats.success_count,
                        stats.failure_count,
                        stats.failure_rate,
                    ),
                    time_interval=time_interval,
                )

        return wrapper

    return decorator
