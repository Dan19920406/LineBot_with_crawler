from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from concurrent.futures import ThreadPoolExecutor, as_completed
from linebot.models import *
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import json
import twstock
import time

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('Token')
# Channel Secret
handler = WebhookHandler('Secert_key')

#個地區ＩＤ對照dict
area = {"北":{
            "基隆市":"10017",
            "台北市":"63",
            "新北市":"65",
            "桃園市":"68",
            "新竹市":"10018",
            "新竹縣":"10004"
            },
        "中":{
            "苗栗縣":"10005",
            "台中市":"66",
            "彰化縣":"10007",
            "南投縣":"10008",
            "雲林縣":"10009",
            "嘉義市":"10020",
            "嘉義縣":"10010"
            },
        "南":{
            "台南市":"67",
            "高雄市":"64",
            "屏東縣":"10013"
            },
        "東":{
            "宜蘭縣":"10002",
            "花蓮縣":"10015",
            "台東縣":"10014"
            },
        "外島":{
            "澎湖縣":"10016",
            "金門縣":"09020",
            "連江縣":"09007"
            }
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

def getWeather(z, a):
    #全臺測站分區 - 臺北市測站列表
    url = 'https://www.cwb.gov.tw/V8/C/W/OBS_County.html?ID=' + area[z][a]
    with ThreadPoolExecutor() as executor:
        future = executor.submit(crawler_from_chromedriver, url)
    soup = future.result()
    #<tbody id='stations'>
    tbody = soup.find('tbody',{'id':'stations'})
    #print(tbody)
    #<tbody>内所有<tr>標籤
    trs = tbody.find_all('tr')
    result = []
    #對list中的每一項 <tr>
    for tr in trs:
        try:
            tmp = {}
            tmp['zone'] = tr.th.text
            alltd = tr.find_all('td')
            #print(f'{alltd}\n\n')
            tmp['time'] = alltd[0].text
            tmp['temp'] = alltd[1].text
            tmp['stat'] = alltd[2].img.get('title')
            tmp['hum'] = alltd[7].text
            result.append(tmp)
        except:
            pass
    return result
    
def getStock(num):
    tmp = ''
    try:
        url = 'https://www.cmoney.tw/finance/f00025.aspx?s='+str(num)
        with ThreadPoolExecutor() as executor:
            future = executor.submit(crawler_from_chromedriver, url)
        soup = future.result()
        name = soup.find('h1', class_="page-title").text
        tmp += f"股價名稱:{name}\n"
        stockInfo = soup.find('ul', class_="s-infor-list")
        if stockInfo.find_all('li', class_='up') != []:
            info = stockInfo.find_all('li', class_='up')
        elif stockInfo.find_all('li', class_='down') != [] and stockInfo.find_all('li', class_='up') == []:
            info = stockInfo.find_all('li', class_='down')
        else:
            info = stockInfo.find_all('li', class_='undefined')
        price = info[0].text.replace('\n','')
        change = info[1].text.replace('\n','')
        rise = info[2].text.replace('\n','')
        tmp += f"{price[:2]}:{price[2:]}元\n"
        tmp += f"{change[:2]}:{change[2:]}\n"
        tmp += f"{rise[:2]}:{rise[2:]}"
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
            try:
                tmpItem = []
                for a in area:
                    tmpItem.append(QuickReplyButton(action=MessageAction(label=a, text=f"天氣 {a}")))
                message = TextSendMessage(text="選擇您想查詢的地區!",quick_reply=QuickReply(items=tmpItem))
            except:
                message = TextSendMessage(text="沒有您想查詢的地區!")
            line_bot_api.reply_message(event.reply_token, message)
        elif len(msg.split(' ')) == 2:
            try:
                tmpItem = []
                zone = msg.split(' ')[1]
                for a in area[msg.split(' ')[1]]:
                    tmpItem.append(QuickReplyButton(action=MessageAction(label=a, text=f"天氣 {zone} {a}")))
                message = TextSendMessage(text="選擇您想查詢的地區!",quick_reply=QuickReply(items=tmpItem))
            except:
                message = TextSendMessage(text="沒有您想查詢的地區!")
            line_bot_api.reply_message(event.reply_token, message)
            
        elif len(msg.split(' ')) == 3:
            zone = msg.split(' ')
            tmptxt = ""
            #{'zone': '新屋', 'time': '14:00', 'temp': '29.6', 'stat': '晴', 'hum': '74'}
            #try:
            #print(zone[2])
            r = getWeather(zone[1],zone[2])
            #print(r)
            for i in r:
                tmptxt+=i['zone'] + ',' + i['temp'] + '度C,天氣' + i['stat'] + '\n'
            message = TextSendMessage(text=tmptxt)
            #except:
                #message = TextSendMessage(text="沒有您想查詢的地區!")
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
        tmpurl = "https://linebotqaservice.azurewebsites.net/qnamaker/knowledgebases/6bb3d1d6-33c6-4948-8665-ff57baf5d9cb/generateAnswer"
        
        r = requests.post(tmpurl,json.dumps({'question': msg}),
                   headers={
                       'Content-Type': 'application/json',
                       'Authorization': 'EndpointKey 9c743d8a-7488-484b-8038-5f20ec1df7cf'
                   })
        data = r.json()
        
        if len(data['answers'][0]['questions']) != 0:
            message = TextSendMessage(text=data['answers'][0]['answer'])
            line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
