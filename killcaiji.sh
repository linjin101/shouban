#!/bin/bash
 
# 设置要关闭的Local Address
local_address="127.0.0.1:5000"
 
# 使用netstat和grep找到监听在指定Local Address的进程ID
pid=$(netstat -tulnp | grep "$local_address" | awk '{print $7}' | cut -d'/' -f1)
 
# 如果找到了进程ID，杀死该进程
if [ -n "$pid" ]; then
  kill $pid
fi
