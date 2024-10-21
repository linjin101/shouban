#!/bin/bash

# 获取当前日期和时间  
current_date=$(date +"%Y-%m-%d %H:%M:%S")  
start_time="09:15:00"  
end_time="15:00:00"  
weekday=$(date +"%u") # 周一到周日，分别对应 1 到 7  
  
# 将时间转换为从当天午夜开始的秒数  
current_epoch_seconds=$(date -d "$current_date" +%s)  
start_epoch_seconds=$(date -d "$(date +%Y-%m-%d) $start_time" +%s)  
end_epoch_seconds=$(date -d "$(date +%Y-%m-%d) $end_time" +%s)  
  
# 检查当前时间是否在指定范围内且是周一到周五  
if (( current_epoch_seconds >= start_epoch_seconds && current_epoch_seconds <= end_epoch_seconds && weekday >= 1 && weekday <= 5 )); then
    while (( current_epoch_seconds >= start_epoch_seconds && current_epoch_seconds <= end_epoch_seconds )); do

        # 请求时间服务（这里假设使用 curl，你可以根据实际情况替换）  
        python /www/stock/flask/test.py  
        # 等待 2 秒  
        sleep 2  
        # 重新获取当前时间和秒数  
        current_date=$(date +"%Y-%m-%d %H:%M:%S")  
        current_epoch_seconds=$(date -d "$current_date" +%s)  
    done  
fi



