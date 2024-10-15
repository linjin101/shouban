# 首板网站
http://sanhu918.com:5555/

## 运行
cd C:\Python\project\shouban
python app.py

##  启动
nohup  python /www/stock/flask/app.py > /www/stock/flask/caiji.log 2>&1 &
nohup  /www/stock/flask/request_time_service.sh > /www/stock/flask/request_time_service.log 2>&1 &
## 关闭
/www/stock/flask/killcaiji.sh

## 日志
tail -f /www/stock/flask/caiji.log



## 定时

在 CentOS 系统上，你可以使用 `cron` 和 `while` 循环结合 `sleep` 命令来实现每 5 秒钟执行一次某个任务的需求。不过需要注意的是，`cron` 本身的最小时间间隔是 1 分钟。为了实现更短的时间间隔，我们可以利用 `cron` 来启动一个脚本，然后在脚本中使用 `while` 循环和 `sleep` 命令来实现每 5 秒执行一次。

以下是如何实现周一到周五的 9:15 到 15:00 每 5 秒钟请求一次时间服务的步骤：

1. **编写脚本**：

   首先，编写一个脚本，比如 `request_time_service.sh`，这个脚本将会包含实际的请求时间服务的命令以及控制时间范围的逻辑。

```bash
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
        /usr/bin/python /www/stock/flask/test.py  
        # 等待 3 秒  
        sleep 3  
        # 重新获取当前时间和秒数  
        current_date=$(date +"%Y-%m-%d %H:%M:%S")  
        current_epoch_seconds=$(date -d "$current_date" +%s)  
    done  
fi
```

2. **赋予脚本执行权限**：

```bash
chmod +x /www/stock/flask/request_time_service.sh
```

3. **配置 `cron`**：

使用 `cron` 每天在 9:14 启动这个脚本（因为脚本内部会检查时间范围并循环执行）。你可以使用 `crontab -e` 来编辑当前用户的 `cron` 任务。

```bash
* 14 9 * * 1-5 /www/stock/flask/request_time_service.sh
```

这行 `cron` 配置表示每周一到周五的 9:14 触发脚本。脚本会在 9:15 开始执行，并一直运行到 15:00，每 5 秒请求一次时间服务。

4. **注意事项**：

   - 确保你的脚本路径正确。
   - 确保 `curl` 或其他请求工具已安装并可用。
   - 如果系统时间发生变化（如系统时间被手动修改或 NTP 服务同步），脚本可能会受到影响。
   - 如果脚本需要长时间运行，考虑日志记录和错误处理机制。

通过以上步骤，你应该能够实现周一到周五的 9:15 到 15:00 每 5 秒钟请求一次时间服务的需求。
