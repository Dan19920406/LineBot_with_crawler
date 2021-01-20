from apscheduler.schedulers.blocking import BlockingScheduler
import requests

# 宣告一個排程
sched = BlockingScheduler()

# 定義排程 : 在周一至周日，每 20 分鐘就做一次 def scheduled_jog()
@sched.scheduled_job('cron', day_of_week='mon-sun', minute='*/5')
def scheduled_job():
    url = "https://qa-assistant.herokuapp.com/"
    r = requests.get(url)
    print(r.status_code)
    
sched.start()  # 啟動排程
