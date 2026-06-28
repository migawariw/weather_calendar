from datetime import date
import os
import requests

LAT = 35.6762
LON = 139.6503

today = date.today()
month_str = today.strftime("%Y-%m")
year = today.year

out_dir = f"weather/{year}"
os.makedirs(out_dir, exist_ok=True)

out_file = f"{out_dir}/weather-{month_str}.ics"


def fetch_month():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LAT,
        "longitude": LON,
        "start_date": today.replace(day=1).isoformat(),
        "end_date": today.isoformat(),
        "daily": "weathercode,temperature_2m_mean,precipitation_sum",
        "timezone": "Asia/Tokyo"
    }

    r = requests.get(url, params=params, timeout=30)
    data = r.json()
    return data["daily"]


def condition(code):
    if code is None:
        return "不明"

    code = int(code)

    # 晴れ系
    if code == 0:
        return "快晴"
    if code in [1]:
        return "晴れ"
    if code in [2]:
        return "晴れ時々くもり"
    if code == 3:
        return "曇り"

    # 霧
    if code in [45, 48]:
        return "霧"

    # 霧雨・小雨系
    if 51 <= code <= 57:
        return "霧雨"

    # 雨
    if 61 <= code <= 67:
        return "雨"

    # 雪
    if 71 <= code <= 77:
        return "雪"

    # にわか雨・にわか雪
    if 80 <= code <= 82:
        return "にわか雨"
    if 85 <= code <= 86:
        return "にわか雪"

    # 雷雨
    if code == 95:
        return "雷雨"
    if code in [96, 99]:
        return "激しい雷雨"

    # ここで全部吸収（重要）
    return f"不明({code})"

daily = fetch_month()

dates = daily["time"]
codes = daily["weathercode"]
temps = daily["temperature_2m_mean"]
rains = daily["precipitation_sum"]


ics = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//weather calendar//JP//"
]

for i in range(len(dates)):
    ymd = dates[i].replace("-", "")

    w_condition = condition(codes[i])
    temp = temps[i] if temps[i] is not None else "-"
    rain = rains[i] if rains[i] is not None else "-"

    ics += [
        "BEGIN:VEVENT",
        f"UID:{ymd}",
        f"DTSTART;VALUE=DATE:{ymd}",
        f"SUMMARY:{w_condition} / 平均 {temp}℃",
        f"DESCRIPTION:降水量 {rain}mm",
        "END:VEVENT"
    ]

ics.append("END:VCALENDAR")

with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(ics))
