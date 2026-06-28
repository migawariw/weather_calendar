from datetime import date, timedelta
import os
import requests
from bs4 import BeautifulSoup

PREC_NO = "44"
BLOCK_NO = "47662"

today = date.today()
month_str = today.strftime("%Y-%m")
year = today.year

out_dir = f"weather/{year}"
os.makedirs(out_dir, exist_ok=True)

out_file = f"{out_dir}/weather-{month_str}.ics"


def fetch_weather(d):
    url = "https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php"

    params = {
        "prec_no": PREC_NO,
        "block_no": BLOCK_NO,
        "year": d.year,
        "month": d.month,
        "day": d.day,
        "view": "p1"
    }

    r = requests.get(url, params=params, timeout=10)
    r.encoding = "utf-8"

    soup = BeautifulSoup(r.text, "lxml")
    table = soup.find("table", {"class": "data2_s"})
    if not table:
        return None

    rows = table.find_all("tr")

    # ヘッダ取得
    header_cells = rows[0].find_all("th")
    headers = [h.text.strip() for h in header_cells]

    def find_index(keyword):
        for i, h in enumerate(headers):
            if keyword in h:
                return i
        return None

    temp_i = find_index("平均気温")
    rain_i = find_index("降水量")

    if temp_i is None or rain_i is None:
        return None

    data_cells = rows[1].find_all("td")
    values = [c.text.strip() for c in data_cells]

    # 天気（ある場合だけ）
    condition = values[0] if len(values) > 0 else "-"

    avg_temp = values[temp_i] if temp_i < len(values) else "-"
    precip = values[rain_i] if rain_i < len(values) else "-"

    return {
        "condition": condition if condition else "-",
        "avg_temp": avg_temp if avg_temp else "-",
        "precip": precip if precip else "-"
    }


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
