from flask import Flask, render_template, jsonify, request
import caiji3 
import appconfig
from datetime import datetime, timedelta  

app = Flask(__name__)
# 读取appconfig服务器配置
ipconfig = appconfig.ipconfig
ipconfigHtml = appconfig.ipconfigHtml

app.config['SERVER_NAME'] = ipconfig

@app.route('/getData')
def data():
    # 假设这是你要通过AJAX获取的数据
    # response_data = '假设这是你要通过AJAX获取的数据'
    response_data = caiji3.getStockListAll()
    # # return response_data
    # # response_data = {'key': 'dddd'}
    response_data_json = jsonify( response_data )    
    # print(response_data_json)
    return response_data_json

@app.route('/')
def index():
    userconfig = {'ipconfig': ipconfigHtml}  
    # 获取当前月份的交割日期  
    # 获取当前日期  
    today = datetime.today().date()  
    
    # 获取当前月份的年份和月份  
    current_year, current_month = today.year, today.month  
    
    # 获取交割日期  
    futures_delivery_date = get_third_friday_of_month(current_year, current_month)  
    options_delivery_date = get_fourth_wednesday_of_month(current_year, current_month)

    days_to_futures = '已过'
    days_to_options = '已过'
    # 计算离当前日期还剩几天  
    if futures_delivery_date >= today:
        days_to_futures = str((futures_delivery_date - today).days)+'天'  
    if options_delivery_date >= today:
        days_to_options = str((options_delivery_date - today).days)+'天' 
     
    return render_template('index.html',userconfig=userconfig,futures_delivery_date=futures_delivery_date,options_delivery_date=options_delivery_date,days_to_futures=days_to_futures,days_to_options=days_to_options)

def get_third_friday_of_month(year, month):  
    """  
    获取指定月份第三个星期五的日期（股指期货交割日期）  
    """  
    first_day = datetime(year, month, 1)  
    # 计算第一个星期五  
    first_friday = first_day + timedelta(days=(4 - first_day.weekday() + 7) % 7)  
    # 计算第三个星期五  
    # 如果第一个星期五不是1号且不在1号所在的那一周，则第三个星期五是第一个星期五加两周  
    # 如果第一个星期五是1号或在其所在周，则逻辑上不会进入这个if（因为这种情况不会发生），但为了代码的完整性还是保留  
    if first_friday.day != 1:  
        third_friday = first_friday + timedelta(weeks=2)  
    else:  
        # 实际上这种情况不会发生，因为1号不可能是第三个星期五  
        # 但为了代码的健壮性，我们仍然处理这种情况（虽然它不会改变结果）  
        third_friday = first_friday.replace(day=first_friday.day + 2*7 - (first_friday.day-1)%7) # 实际上这行代码不会执行，只是为了展示如何处理（尽管没必要）  
        # 或者更简单地，由于我们已经知道第一个星期五，直接加两周即可（如上面的if分支）  
    # 但由于上面的if-else结构是为了展示逻辑完整性，实际上可以直接使用下面的代码：  
    third_friday = first_friday + timedelta(weeks=2 if first_friday.day != 1 else 2) # 这里的else 2是多余的，但为了与上面的逻辑对应而保留  
    # 最终简化为（去掉不必要的判断）：  
    third_friday = first_friday + timedelta(weeks=2) # 因为first_friday永远不会是1号所在的星期五（根据逻辑）  
    return third_friday.date()  
  
def get_fourth_wednesday_of_month(year, month):  
    """  
    获取指定月份第四个星期三的日期（股票期权交割日期）  
    """  
    first_day = datetime(year, month, 1)  
    # 计算第一个星期三  
    first_wednesday = first_day - timedelta(days=first_day.weekday() % 7) # 如果1号是周三，则结果为1号；否则为上一个周三  
    # 调整到第一个完整的星期三（如果1号不是周三）  
    if first_wednesday.weekday() != 2: # 2代表星期三  
        first_wednesday += timedelta(days=(2 - first_wednesday.weekday() + 7) % 7)  
    # 计算第四个星期三  
    fourth_wednesday = first_wednesday + timedelta(weeks=3) # 从第一个星期三开始加三周得到第四个星期三  
    return fourth_wednesday.date()  
  

# @app.route('/process_input', methods=['POST'])
# def process_input():
#     input_text = request.form['input_text']
#     # 在这里对接收到的数据进行处理，例如输出到控制台或返回给前端页面
#     print("Received input text:", input_text)
#     return "Input text received: " + input_text

if __name__ == '__main__':
    app.run(debug=True)
