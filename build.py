from datetime import date, timedelta
import os
import requests

today = date.today()
month_str = today.strftime("%Y-%m")
year = today.year

out_dir = f"weather/{year}"
os.makedirs(out_dir, exist_ok=True)

out_file = f"{out_dir}/weather-{month_str}.ics"


# 東京（固定）
LAT = 35.6762
LON = 139.6503


import time
import requests

def fetch_weather(d):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": 35.6762,
        "longitude": 139.6503,
        "start_date": d.isoformat(),
        "end_date": d.isoformat(),
        "daily": "weathercode,temperature_2m_mean,precipitation_sum",
        "timezone": "Asia/Tokyo"
    }

    for i in range(3):  # リトライ3回
        try:
            r = requests.get(url, params=params, timeout=30)
            data = r.json()

            daily = data["daily"]

            code = daily["weathercode"][0]
            temp = daily["temperature_2m_mean"][0]
            rain = daily["precipitation_sum"][0]

            condition_map = {
                0: "快晴",
                1: "晴れ",
                2: "くもり",
                3: "曇り",
                45: "霧",
                61: "雨",
                80: "にわか雨"
            }

            return {
                "condition": condition_map.get(code, "不明"),
                "avg_temp": round(temp, 1) if temp is not None else "-",
                "precip": round(rain, 1) if rain is not None else "-"
            }

        except Exception:
            time.sleep(2)  # 少し待って再試行

    return None




def make_event(d, w):
    ymd = d.strftime("%Y%m%d")

    summary = f"{w['condition']} / 平均 {w['avg_temp']}℃"
    desc = f"降水量 {w['precip']}mm"

    return [
        "BEGIN:VEVENT",
        f"UID:{ymd}",
        f"DTSTART;VALUE=DATE:{ymd}",
        f"SUMMARY:{summary}",
        f"DESCRIPTION:{desc}",
        "END:VEVENT"
    ]


start = today.replace(day=1)

ics = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//weather calendar//JP//"
]

d = start
while d <= today:
    w = fetch_weather(d)
    if w:
        ics += make_event(d, w)
    d += timedelta(days=1)

ics.append("END:VCALENDAR")

with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ics))
