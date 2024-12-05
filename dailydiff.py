import datetime
from datetime import timedelta


def get_third_friday(year, month):
    # 获取指定月份的第一天
    first_day = datetime.date(year, month, 1)

    # 找到第一个星期五（或者如果1号是星期五，那就是它）
    first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)

    # 计算第三个星期五（第一个星期五加两周）
    third_friday = first_friday + timedelta(weeks=2)

    return third_friday


def days_to_next_third_friday(today):
    # 获取当前月份和年份
    current_month = today.month
    current_year = today.year

    # 获取本月的第三个星期五
    third_friday_this_month = get_third_friday(current_year, current_month)

    # 计算今天到本月第三个星期五的天数差
    days_diff_this_month = (third_friday_this_month - today).days

    # 如果天数差大于等于0，则返回结果
    if days_diff_this_month >= 0:
        return days_diff_this_month

    # 否则，我们需要计算下个月的第三个星期五
    # 下个月的年份和月份
    next_month = (current_month % 12) + 1 if current_month != 12 else 1
    next_year = current_year if next_month != 1 else current_year + 1

    # 获取下个月的第三个星期五
    third_friday_next_month = get_third_friday(next_year, next_month)

    # 计算今天到下月第三个星期五的天数差
    days_diff_next_month = (third_friday_next_month - today).days

    # 返回结果
    return days_diff_next_month


# 获取当前日期
# today = datetime.date.fromisoformat('2024-12-31')
# today = datetime.date.today()
#
# # 计算天数差并打印结果
# days_diff = days_to_next_third_friday(today)
# print(f"距离股指期货下一个第三个星期五还有 {days_diff} 天")