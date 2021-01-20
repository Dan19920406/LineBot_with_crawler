# LineBot_with_crawler
Crawling stock, weather, gas price information with line bot application
---
# How to use?
1. Need a Line Developers account
2. Need a Heroku account
3. Setting environment about above two steps (Can google if have any question.)
4. Line Bot token write into app.py
5. app.py deploy to Heroku

---
# Introduction
* Crawling weather info from weather station[weather website](https://www.cwb.gov.tw/V8/C/W/OBS_County.html?ID=10017)
* Crawling stock info from CMoney [stock website](https://www.cmoney.tw/finance/f00025.aspx?s=2330)
* Crawling gas price info from GoodLife [gas price webbsite](https://gas.goodlife.tw)
* weather and stock web use selenium with chromedriver because both webpage base on javascript develop 
* LineBot QRCode as below:
> ![](https://i.ibb.co/cvLYgrN/989vvfpc.png)
* Query format:
> 天氣查詢範例：
> * 天氣 (北,中,南) (縣市)
> * 天氣 北 新北市 
> ---
> 股價查詢範例：
> * 股價 (股票代碼)
> * 股價 2330
> ---
> 油價查詢範例：
> * 油價
