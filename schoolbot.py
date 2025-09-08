import requests
import datetime
import os

# 🔹 환경 변수에서 불러오기 (Secrets)
API_KEY = os.getenv("NEIS_API_KEY")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

ATPT_OFCDC_SC_CODE = "B10"   # 시도교육청 코드
SD_SCHUL_CODE = "7010140"    # 학교 코드
GRADE = "1"                  # 학년
CLASS_NM = "3"               # 반

today = datetime.datetime.now()
target_date = today + datetime.timedelta(days=1)
today_str = target_date.strftime("%Y%m%d")

# 요일 변환
weekdays = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]
weekday_str = weekdays[today.weekday()]

# 🔹 급식 API
meal_url = (
    f"https://open.neis.go.kr/hub/mealServiceDietInfo?"
    f"KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
    f"&SD_SCHUL_CODE={SD_SCHUL_CODE}&MLSV_YMD={today_str}"
)
meal_res = requests.get(meal_url).json()
try:
    meal = meal_res['mealServiceDietInfo'][1]['row'][0]['DDISH_NM']
    meal = meal.replace("<br/>", "\n")
except (KeyError, IndexError):
    meal = "오늘은 급식 정보가 없습니다."

# 🔹 시간표 API
timetable_url = (
    f"https://open.neis.go.kr/hub/hisTimetable?"
    f"KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
    f"&SD_SCHUL_CODE={SD_SCHUL_CODE}&ALL_TI_YMD={today_str}"
    f"&GRADE={GRADE}&CLASS_NM={CLASS_NM}"
)
tt_res = requests.get(timetable_url).json()
try:
    rows = tt_res['hisTimetable'][1]['row']
    timetable = "\n".join([f"{row['PERIO']}교시: {row['ITRT_CNTNT']}" for row in rows])
except (KeyError, IndexError):
    timetable = "오늘은 시간표 정보가 없습니다."

# 🔹 디스코드 전송
data = {
    "content": f"====={today_str} {weekday_str}=====\n\n급식:\n{meal}\n\n시간표:\n{timetable}"
}
response = requests.post(WEBHOOK_URL, json=data)
if response.status_code == 204:
    print("✅ 오늘 급식, 시간표가 디스코드로 전송되었습니다!")
else:
    print("❌ 전송 실패:", response.text)
