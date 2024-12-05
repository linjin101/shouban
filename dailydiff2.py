import datetime
from datetime import timedelta


def get_fourth_wednesday(year, month):
    # 获取指定月份的第一个星期三
    first_day = datetime.date(year, month, 1)
    first_wednesday = first_day + timedelta(days=(2 - first_day.weekday()) % 7)

    # 计算第四个星期三
    fourth_wednesday = first_wednesday + timedelta(weeks=3)
    return fourth_wednesday


def days_to_next_fourth_wednesday(today):
    # 获取当前月份和年份
    current_month = today.month
    current_year = today.year

    # 获取本月的第四个星期三
    fourth_wednesday_this_month = get_fourth_wednesday(current_year, current_month)

    # 计算今天到本月第四个星期三的天数差
    days_diff_this_month = (fourth_wednesday_this_month - today).days

    # 如果天数差大于等于0，则返回结果并退出
    if days_diff_this_month >= 0:
        return days_diff_this_month

    # 否则，计算下个月的第四个星期三
    next_month = current_month % 12 + 1 if current_month != 12 else 1
    next_year = current_year if next_month != 1 else current_year + 1

    fourth_wednesday_next_month = get_fourth_wednesday(next_year, next_month)

    # 计算今天到下月第四个星期三的天数差
    days_diff_next_month = (fourth_wednesday_next_month - today).days

    # 返回结果
    return days_diff_next_month

# today = datetime.date.today()
# days_diff = days_to_next_fourth_wednesday(today)
# print(f"距离股票期权下一个第四个星期三还有 {days_diff} 天")
# i  = 0
# while i < 50:
#     # 获取当前日期
#     # today = datetime.date.fromisoformat('2024-12-26') # datetime.date.today()  # 或者你可以指定一个日期进行测试
#     # 获取当前日期
#     today = datetime.date.today()
#     # 使用timedelta来往后移动一天
#     one_day_later = today + datetime.timedelta(days=i)
#     print(one_day_later)
#     # 计算天数差并打印结果
#     days_diff = days_to_next_fourth_wednesday(one_day_later)
#     print(f"距离股票期权下一个第四个星期三还有 {days_diff} 天")
#     i = i + 1