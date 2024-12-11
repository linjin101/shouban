from flask import Flask, render_template, jsonify, request
import datetime
from datetime import timedelta
import appconfig
import caiji3
import dailydiff
import dailydiff2

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

    today = datetime.date.today()
    # 计算离当前日期还剩几天
    days_to_futures = str( dailydiff.days_to_next_third_friday(today) )  + '天'
    days_to_options = str( dailydiff2.days_to_next_fourth_wednesday(today) ) + '天'
     
    return render_template('index.html',userconfig=userconfig,days_to_futures=days_to_futures,days_to_options=days_to_options)


@app.route('/pop')
def pop():
    return render_template('pop.html')


# @app.route('/process_input', methods=['POST'])
# def process_input():
#     input_text = request.form['input_text']
#     # 在这里对接收到的数据进行处理，例如输出到控制台或返回给前端页面
#     print("Received input text:", input_text)
#     return "Input text received: " + input_text

if __name__ == '__main__':
    app.run(debug=True)
