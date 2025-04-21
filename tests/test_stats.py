import random
import time
from pymail import track_stats, stats_manager, email_on_error


# 使用统计装饰器
@track_stats(task_name="your_function", time_interval=10)
def your_function():
    p = random.random()
    if p > 0.8:
        raise Exception("随机异常")


# 同时使用错误通知和统计
@track_stats(time_interval=10, success_condition=lambda x: x == "abcd")
@email_on_error()
def your_important_function():
    try:
        p = random.random()
        # if p < 0.3:
        #     raise Exception("随机异常")
        return p
    except Exception as e:
        raise e


def test_stats():

    while True:
        try:
            your_important_function()
        except Exception as e:
            pass
        time.sleep(2)

        # 获取所有函数的统计信息
        all_stats = stats_manager.get_all_stats()
        for func_name, stats in all_stats.items():
            print(f"{func_name}:\n {stats}")
            print("-" * 30)


if __name__ == "__main__":
    test_stats()
