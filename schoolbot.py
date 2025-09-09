import requests
import datetime
import os
import pytz


API_KEY = os.getenv("NEIS_API_KEY")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

ATPT_OFCDC_SC_CODE = "B10"
SD_SCHUL_CODE = "7010140"
GRADE = "1"
CLASS_NM = "3"


kst = pytz.timezone("Asia/Seoul")
today = datetime.datetime.now(kst)
today_str = today.strftime("%Y%m%d")


weekdays = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]
weekday_str = weekdays[today.weekday()]

def get_meal(date_str: str) -> str:
    url = (
        f"https://open.neis.go.kr/hub/mealServiceDietInfo?"
        f"KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
        f"&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={date_str}"
    )
    res = requests.get(url).json()
    try:
        meal = res['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
        return meal.replace("<br/>", "\n")
    except (KeyError, IndexError):
        return None

def get_timetable(date_str: str) -> str:
    url = (
        f"https://open.neis.go.kr/hub/hisTimetable?"
        f"KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
        f"&SD_SCHUL_CODE={SD_SCHUL_CODE}&ALL_TI_YMD={date_str}"
        f"&GRADE={GRADE}&CLASS_NM={CLASS_NM}"
    )
    res = requests.get(url).json()
    try:
        rows = res['hisTimetable'][1]['row']
        return "\n".join([f"{row['PERIO']}교시: {row['ITRT_CNTNT']}" for row in rows])
    except (KeyError, IndexError):
        return None

meal = get_meal(today_str)
timetable = get_timetable(today_str)


if meal is None and timetable is None:
    tomorrow = today + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y%m%d")
    weekday_str = weekdays[tomorrow.weekday()]
    meal = get_meal(tomorrow_str) or "급식 정보가 없습니다."
    timetable = get_timetable(tomorrow_str) or "시간표 정보가 없습니다."
    date_label = tomorrow_str
else:
    meal = meal or "급식 정보가 없습니다."
    timetable = timetable or "시간표 정보가 없습니다."
    date_label = today_str

data = {
    "content": f"====={date_label} {weekday_str}=====\n\n급식:\n{meal}\n\n시간표:\n{timetable}"
}
response = requests.post(WEBHOOK_URL, json=data)

if response.status_code == 204:
    print("오늘 급식, 시간표가 디스코드로 전송되었습니다!")
else:
    print("전송 실패:", response.text)
