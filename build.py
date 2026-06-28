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


# 気象庁から1日分取得
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

    r = requests.get(url, params=params)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "lxml")

    table = soup.find("table", {"class": "data2_s"})
    if not table:
        return None

    rows = table.find_all("tr")

    def get_cell(label_index, col_index):
        try:
            return rows[label_index].find_all("td")[col_index].text.strip()
        except:
            return "-"

    # 気象庁の列構造（変わる可能性あり）
    condition = get_cell(0, 0)   # 天気（簡易）
    avg_temp = get_cell(6, 1)    # 平均気温
    precip = get_cell(3, 1)      # 降水量

    return {
        "condition": condition,
        "avg_temp": avg_temp,
        "precip": precip
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


# 今月分を再生成
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
