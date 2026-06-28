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
    table = {
        0: "快晴",
        1: "晴れ",
        2: "くもり",
        3: "曇り",
        45: "霧",
        61: "雨",
        80: "にわか雨"
    }
    return table.get(code, "不明")


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
