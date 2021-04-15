from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import requests
from bs4 import BeautifulSoup
import re
import json
import twstock
import time

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('luiQ79dNJtpnNPe1q5ATGTtCO1GRfu9Wi4BH59in/ndMO8LXINcMh3ORIQ2htwqs5SprRLWE3wLu8D1nJ1McHI0wF7zZIprzHBbv5fVBbQp0dB3rnx5WnihEqKgnZ707UZy8MCXdZmXUzE0mfhDz+AdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('ac47e0fd152f0e25cf9f47a9579d41bf')

#個地區ＩＤ對照dict
area = {"基隆":["10017"],
        "台北":["63"],
        "新北":["65"],
        "桃園":["68"],
        "新竹":["10018","10004"],
        "苗栗":["10005"],
        "台中":["66"],
        "彰化":["10007"],
        "南投":["10008"],
        "雲林":["10009"],
        "嘉義":["10020","10010"],
        "台南":["67"],
        "高雄":["64"],
        "屏東":["10013"],
        "宜蘭":["10002"],
        "花蓮":["10015"],
        "台東":["10014"],
        "澎湖":["10016"],
        "金門":["09020"],
        "連江":["09007"]
        }

def crawler_from_chromedriver(url):
    #啟動模擬瀏覽器
    #driver = webdriver.Chrome('/app/chromedriver')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless") #無頭模式
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    #取得網頁代馬
    driver.get(url)
    #指定 lxml 作為解析器
    soup = BeautifulSoup(driver.page_source, features='lxml')
    #關閉模擬瀏覽器
    driver.quit()
    return soup
       
def getGasPrice():
    r = requests.get("https://gas.goodlife.tw") #將此頁面的HTML GET下來
    r.encoding='utf-8'
    tmptxt = ''
    # 確認是否下載成功
    if r.status_code == requests.codes.ok:
        # 以 BeautifulSoup 解析 HTML 程式碼
        soup = BeautifulSoup(r.text, 'html.parser')
        #print(soup)
        lastUpdate = soup.find("p", attrs={'class':'update'})
        
        lastUpdateTime = re.sub('\(.+', '',lastUpdate.text)
        tmptxt += lastUpdateTime
        
        sel = soup.find("div", attrs={'id':'gas-price'})
        tmptxt += sel.text.replace(" ","").replace(":\n",":").replace("\n\n\n","\n").replace("\n\n","\n")
        
        name_box = soup.find_all('div', attrs={'id': 'cpc'})
        
        for i in name_box:
            tmptxt += i.text.replace(" ","").replace(" \n","").replace(":\n",":").replace("油價:",":").replace("\n\n\n","\n").replace("\n\n","\n")
    return tmptxt

def getWeather(d, z):
    #全臺測站分區 - 臺北市測站列表
    try:
        districtCode = area[d]
        for Code in districtCode:
            url = f'https://www.cwb.gov.tw/Data/js/Observe/County/{Code}.js?_=' + str(int(time.time()*1000))
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            tmp = json.loads(str(soup).split("ST = ")[1].replace(';','').split("var")[0].replace('\'a','a').replace('\'','\"'))
            for key, value in tmp[Code].items():
                #print(value)
                if value['StationName']['C'] == z:
                    #print(value)
                    T = value['Time'] #觀測時間
                    Weather = value["Weather"]['C'] #天氣
                    Temperature = value["Temperature"]['C']['C'] #溫度
                    Humidity = value['Humidity']['C'] #相對濕度
                    WindDir = value['WindDir']['C'] #風向
                    result = f'{z}\n觀測時間：{T}\n天氣：{Weather}\n溫度：{Temperature} degrees\n相對濕度：{Humidity}%\n風向：{WindDir}'
                    return result
    except Exception as e:
        print(e)
        pass
        
    result = '無此觀測站!'
    return result

def getStock(num):
    tmp = ''
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{num}.TW?region=US&lang=en-US&includePrePost=false&interval=2m&useYfid=true&range=1d&corsDomain=finance.yahoo.com&.tsrc=finance"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        tmpr = json.loads(str(soup))
        stockName = tmpr["chart"]["result"][0]['meta']['symbol']
        regularMarketPrice = tmpr["chart"]["result"][0]['meta']['regularMarketPrice'] #["quote"][0]['low']
        previousClose = tmpr["chart"]["result"][0]['meta']['previousClose']
        changed = (regularMarketPrice-previousClose)/regularMarketPrice*100
        tmp += f'Stock : {stockName}\nCurrent price = ${regularMarketPrice}\nChanged = {changed:.2f}%'
    except Exception as e:
        print(f'Error : {e}')
        tmp += 'Something wrong, we\'ll fix it!'

    return tmp

# 監聽所有來自 / 的 Post Request
@app.route('/')
def index():
    return "Hello, this is QA-Assistant webhook!"

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    print(msg.split(' '))
    print(f'Get msg : {msg}')
    if msg in ["油價", "油", "油價資訊", "油資訊"]:
        message = TextSendMessage(text=getGasPrice())
        line_bot_api.reply_message(event.reply_token, message)
    elif msg.split(' ')[0] in ["天氣","氣象"]:
        if len(msg.split(' ')) == 1:
            message = TextSendMessage(text=f"請輸入行政區與區域!\nEx : 天氣 新北 石碇")
            line_bot_api.reply_message(event.reply_token, message)
            
        elif len(msg.split(' ')) == 2:
            tmpData = msg.split(' ')[1]
            if tmpData in area:
                message = TextSendMessage(text=f"請輸入欲查哪個區域!")
            else:
                message = TextSendMessage(text=f"查詢不到{tmpData}!")
            line_bot_api.reply_message(event.reply_token, message)
            
        elif len(msg.split(' ')) == 3:
            zone = msg.split(' ')
            tmptxt = getWeather(zone[1],zone[2])
            message = TextSendMessage(text=tmptxt)
            line_bot_api.reply_message(event.reply_token, message)
        else:
            pass
            
    elif msg.split(' ')[0] in ["股票","股價"]:
        try:
            msg = getStock(msg.split(' ')[1])
            message = TextSendMessage(text=msg)
            line_bot_api.reply_message(event.reply_token, message)
        except Exception as e:
            print(f'Error : {e}')
    else:
        pass

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
