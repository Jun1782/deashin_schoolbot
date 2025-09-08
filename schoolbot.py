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

# 오늘 날짜
today = datetime.datetime.now()
today_str = today.strftime("%Y%m%d")

# 요일 변환
weekdays = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]
weekday_str = weekdays[today.weekday()]

# ✅ 급식 가져오기 함수
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

# ✅ 시간표 가져오기 함수
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

# 🔹 오늘 데이터 가져오기
meal = get_meal(today_str)
timetable = get_timetable(today_str)

# 🔹 없으면 내일 데이터로 대체
if meal is None and timetable is None:
    tomorrow = today + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y%m%d")
    weekday_str = weekdays[tomorrow.weekday()]  # 요일도 내일 기준으로
    meal = get_meal(tomorrow_str) or "급식 정보가 없습니다."
    timetable = get_timetable(tomorrow_str) or "시간표 정보가 없습니다."
    date_label = tomorrow_str
else:
    meal = meal or "급식 정보가 없습니다."
    timetable = timetable or "시간표 정보가 없습니다."
    date_label = today_str

# 🔹 디스코드 전송
data = {
    "content": f"====={date_label} {weekday_str}=====\n\n급식:\n{meal}\n\n시간표:\n{timetable}"
}
response = requests.post(WEBHOOK_URL, json=data)

if response.status_code == 204:
    print("✅ 오늘 급식, 시간표가 디스코드로 전송되었습니다!")
else:
    print("❌ 전송 실패:", response.text)
