from typing import Dict, Tuple
from dataclasses import dataclass
from threading import Lock
import logging

logger = logging.getLogger(__name__)


@dataclass
class FunctionStats:
    """函数统计信息"""

    success_count: int = 0
    failure_count: int = 0

    @property
    def total_count(self) -> int:
        """总调用次数"""
        return self.success_count + self.failure_count

    @property
    def failure_rate(self) -> float:
        """失败率"""
        return 0.0 if self.total_count == 0 else self.failure_count / self.total_count

    def __str__(self) -> str:
        return (
            f"总调用次数: {self.total_count}, \n"
            f"成功次数: {self.success_count}, \n"
            f"失败次数: {self.failure_count}, \n"
            f"失败率: {self.failure_rate:.2%}"
        )


class StatsManager:
    """统计管理器"""

    _instance = None
    _lock = Lock()
    _stats: Dict[str, FunctionStats] = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def record_execution(self, func_name: str, success: bool) -> None:
        """记录函数执行结果"""
        with self._lock:
            if func_name not in self._stats:
                self._stats[func_name] = FunctionStats()

            stats = self._stats[func_name]
            if success:
                stats.success_count += 1
            else:
                stats.failure_count += 1

    def get_stats(self, func_name: str) -> FunctionStats:
        """获取函数统计信息"""
        with self._lock:
            return self._stats.get(func_name, FunctionStats())

    def get_all_stats(self) -> Dict[str, FunctionStats]:
        """获取所有统计信息"""
        with self._lock:
            return self._stats.copy()


# 全局单例
stats_manager = StatsManager()
