# LineBot_with_crawler
> Information from line bot application
> 1. Stock
> 2. Weather
> 3. gas price
---
# How to use?
1. Need a Line Developers account
> Line Developers API [Document](https://developers.line.biz/zh-hant/docs/messaging-api/getting-started/)
2. Need a Heroku account
3. Setting environment about above two steps (You can google if have any question or refer link as below)
> Setting Heroku with line developers please refrence [快速掌握LINE Bot部署至Heroku雲端平台的重點](https://www.learncodewithmike.com/2020/07/python-line-bot-deploy-to-heroku.html)
4. Line Bot token write into app.py
5. app.py deploy to Heroku

---
# Introduction
* Crawling weather info from weather station[weather website](https://www.cwb.gov.tw/V8/C/W/OBS_County.html?ID=10017)
* Crawling stock info from yahoo finance [stock website](https://finance.yahoo.com)
* Crawling gas price info from GoodLife [gas price webbsite](https://gas.goodlife.tw)
* weather and stock web use selenium with chromedriver because both webpage base on javascript develop 
* LineBot QRCode as below:
> ![](https://i.ibb.co/cvLYgrN/989vvfpc.png)
* Query format:
> 天氣查詢範例：
> * 天氣 (縣市) (區)
> * 天氣 新北 石碇
> ---
> 股價查詢範例：
> * 股價 (股票代碼)
> * 股價 2330
> ---
> 油價查詢範例：
> * 油價
* clock.py ping heroku web keep it awake(because use it for free)
