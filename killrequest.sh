#!/bin/bash  
  
# 查找包含request_time_service.sh的进程ID  
PID=$(ps aux | grep '[r]equest_time_service.sh' | awk '{print $2}')  
  
# 检查是否找到了进程ID  
if [ -z "$PID" ]; then  
  echo "未找到正在运行的./request_time_service.sh脚本。"  
else  
  # 终止进程  
  kill "$PID"  
  
  # 检查kill命令是否成功  
  if [ $? -eq 0 ]; then  
    echo "成功终止了进程ID为$PID的./request_time_service.sh脚本。"  
  else  
    echo "尝试终止进程ID为$PID的./request_time_service.sh脚本时出错。"  
    # 如果需要，可以尝试使用kill -9强制终止  
    kill -9 "$PID"  
    # 但请注意，这可能会导致脚本无法正常清理或保存状态  
  fi  
fi
