def get_time_duration(time_duration: int) -> str:
    days, time_duration = divmod(time_duration, 24 * 3600)
    hours, time_duration = divmod(time_duration, 3600)
    minutes, seconds = divmod(time_duration, 60)
    return f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}"


# if __name__ == "__main__":
#     print(get_time_duration(123))
