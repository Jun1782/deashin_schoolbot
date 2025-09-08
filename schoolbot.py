import os
import requests
import datetime

NEIS_API_KEY = os.getenv("NEIS_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# ===== 한국 시간 (KST) 기준 오늘 날짜 =====
today = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
today_str = today.strftime("%Y%m%d")

# ===== 학교 코드 설정 (예시: 서울특별시교육청, XX고등학교) =====
ATPT_OFCDC_SC_CODE = "B10"   # 교육청 코드 (지역별로 다름)
SD_SCHUL_CODE = "7010569"    # 학교 코드 (NEIS에서 확인)

# ===== 급식 API 요청 =====
meal_url = (
    f"https://open.neis.go.kr/hub/mealServiceDietInfo?"
    f"KEY={NEIS_API_KEY}&Type=json&pIndex=1&pSize=100"
    f"&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
    f"&SD_SCHUL_CODE={SD_SCHUL_CODE}"
    f"&MLSV_YMD={today_str}"
)

meal_res = requests.get(meal_url).json()

meal_text = "급식 정보를 불러올 수 없습니다."
if "mealServiceDietInfo" in meal_res:
    rows = meal_res["mealServiceDietInfo"][1]["row"]
    meal_text = "\n".join(rows[0]["DDISH_NM"].split("<br/>"))

# ===== 시간표 API 요청 =====
timetable_url = (
    f"https://open.neis.go.kr/hub/hisTimetable?"
    f"KEY={NEIS_API_KEY}&Type=json&pIndex=1&pSize=100"
    f"&ATPT_OFCDC_SC_CODE={ATPT_OFCDC_SC_CODE}"
    f"&SD_SCHUL_CODE={SD_SCHUL_CODE}"
    f"&ALL_TI_YMD={today_str}&GRADE=2&CLASS_NM=2"
)

timetable_res = requests.get(timetable_url).json()

timetable_text = "시간표 정보를 불러올 수 없습니다."
if "hisTimetable" in timetable_res:
    rows = timetable_res["hisTimetable"][1]["row"]
    timetable_text = "\n".join(
        [f"{row['PERIO']}교시: {row['ITRT_CNTNT']}" for row in rows]
    )

# ===== 디스코드 전송 =====
message = f"===== {today.strftime('%Y%m%d %A')} =====\n\n급식:\n{meal_text}\n\n시간표:\n{timetable_text}"

requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
