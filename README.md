# 首板网站
http://sanhu918.com:5555/

## 运行
cd C:\Python\project\shouban
python app.py

##  启动
nohup  python /www/stock/flask/app.py > /www/stock/flask/caiji.log 2>&1 &

## 关闭
/www/stock/flask/killcaiji.sh

## 日志
tail -f /www/stock/flask/caiji.log
