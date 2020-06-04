# -*-coding:utf-8-*-
import datetime
import time
import requests
import csv
from bs4 import BeautifulSoup
import json
import os
import re

# 常量
# csv文件名
CSV_FILE_NAME = "thefly.csv"
# csv标题
CSV_TITLE = ["Date", "Name", "Date Range", "Managers", "Location", "City", "State", "Country", "Comments"]
# 开始日期
BEGIN_DATE = "2015-05-26"
# 结束日期
END_DATE = "2018-12-31"
# 头部
HEADER = {
    "cookie": "__cfduid=d9e2fdc85b87f26760cd50ed8e39480831547692529; _ga=GA1.2.1856963450.1547692531; _jsuid=2779159458; __gads=ID=a58d5690a8f92cfe:T=1547692533:S=ALNI_MZh1ZrYj6e4KgfPrHvzw0FmKd8lMw; __qca=P0-1787202055-1547692534147; TheflyUsTr=70.127.114.201.1552019178766548; PHPSESSID=jfg8m6n90d3j1o14sf1rbmio73; _gid=GA1.2.699180146.1552019179; _pxvid=51fb7740-415b-11e9-9aea-0242ac120010; sidebarOpen=true; _px=ANAlZLRn05TxBFTcbS1pC2SZR31+9HMdCA5/Wozv+joaYGA3Lll53t9CVtVKnus6aUpcnG182+hLN/V3yB1z2g==:1000:pcvl7S5d/ap86L4qTxBa4hmISuDmxYMC2e4wB/HNBC9KkppTmeY8zlab2mRio/ajGs6hW+cZIDQ/4UWAm0q0q4Ug7VgLngljJmT0Wh5gL9G76h+zFSCl8VkKvJhua9rj9+Igr8YrpsLoaART3aOJnKb19I88jcRvzkrNlV8p4+tzREJ7mutvm9XeMU/ej0Ao8wR4UXgEFCBclAP8hgCLO8UY0kWy1pmNS87GSAdtunfVkR21pGWas5mYn4+cVP2koQssCq5bxsf0IyFI2pcNRQ==; GED_PLAYLIST_ACTIVITY=W3sidSI6Ik9JVjIiLCJ0c2wiOjE1NTIwNzAxMDUsIm52IjowLCJ1cHQiOjE1NTIwNjk1OTIsImx0IjoxNTUyMDcwMDk0fSx7InUiOiJ2ZGNaIiwidHNsIjoxNTUyMDY5NTkyLCJudiI6MSwidXB0IjoxNTUyMDY5NTg3LCJsdCI6MTU1MjA2OTU5Mn0seyJ1IjoiOUNCTSIsInRzbCI6MTU1MjA2OTU4NywibnYiOjEsInVwdCI6MTU1MjA2NTM3MCwibHQiOjE1NTIwNjk1ODd9XQ..; _gat_UAT5=1; _first_pageview=1; heatmaps_g2g_100767783=yes; _gat=1; IC_ViewCounter_thefly.com=4",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
}


def main():
    global CSV_FILE_NAME
    create_csv()
    print("采集开始")
    date = datetime.datetime.strptime(BEGIN_DATE, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(END_DATE, "%Y-%m-%d")
    while date <= end_date:
        lst_data = get_datas(date.strftime("%Y-%m-%d"))
        save_csv(lst_data)
        date += datetime.timedelta(days=1)
    print("程序处理完毕")


def get_datas(date):
    """
    获取数据
    :return:
    """
    if not date:
        return
    global CSV_TITLE
    # 组装url
    print("正在采集：%s" % date)
    url = "https://thefly.com/events.php?fecha=%s" % date
    # 最终返回的数据列表
    lst_all_data = []
    try:
        # 执行请求
        response = requests.get(url, headers=HEADER)
        text = response.text
    except Exception as e:
        # 出现异常，请求不到，可能是网站封锁了，先休息10秒，再继续
        time.sleep(10)
        return get_datas(date)
    soup = BeautifulSoup(text, "lxml")
    # lst_li = soup.find_all("li", class_="fpo_overlay C")
    # if lst_li:
    #     for li in lst_li:
    #         div = li.find("div", class_="muestraEvento eventoPagEventos")
    #         if div:
    #             id_div_evento = div.get("id")
    #             id = div.get("data-id")
    #             tipo_evento_id = div.get("data-tipoeventoid")
    #             lst_data = get_detail(date, id_div_evento, id, tipo_evento_id)
    #             if lst_data:
    #                 lst_all_data.append(lst_data)
    lst_li = soup.find_all('li', class_="fpo_overlay AM")
    if lst_li:
        for li in lst_li:
            div = li.find("div", class_="muestraEvento eventoPagEventos")
            if div:
                id_div_evento = div.get("id")
                id = div.get("data-id")
                tipo_evento_id = div.get("data-tipoeventoid")
                lst_data = get_detail(date, id_div_evento,id,tipo_evento_id)
                if lst_data:
                    lst_all_data.append(lst_data)
    return lst_all_data


def get_detail(date, id_div_evento, id, tipo_evento_id):
    """
    获取详细信息
    :param date:
    :param id_div_evento:
    :param id:
    :param tipo_evento_id:
    :return:
    """
    if not date or not id_div_evento or not id or not tipo_evento_id:
        return
    url = "https://thefly.com/ajax/getEventContent.php?id_div_evento=%s&id=%s&tipoEventoId=%s" \
          % (id_div_evento, id, tipo_evento_id)
    try:
        # 执行请求
        response = requests.get(url, headers=HEADER)
        text = response.text
    except Exception as e:
        time.sleep(2)
        return get_datas(date)
    data = json.loads(text)
    if not data:
        return
    data_evento = data.get("data_evento")
    if not data_evento:
        return
    soup = BeautifulSoup(data_evento, "lxml")
    lst_data = [""] * len(CSV_TITLE)
    # 查询日期写入第一列
    lst_data[0] = date
    # 名称写入第二列
    span_name = soup.find("span", class_="Nombre orange")
    if span_name:
        lst_data[1] = span_name.get_text(strip=True)
    # 日期范围写入第三列
    span_time = soup.find("span", class_="str_time")
    if span_time:
        lst_data[2] = span_time.get_text(strip=True)
    # div_tablita = soup.find("div", class_="tablita")
    # if div_tablita:
    #     div_tableDetalles = soup.find("div", class="tableDetalles")
    #     if div_tableDetalles:
    #         lst_data[3] = div_tableDetalles.get_text(strip=True).strip()
    # 下面部分是Manager Location这些，拿到Label之后索引到标题列，然后写入
    div_tablita = soup.find("div", class_="tablita")
    if div_tablita:
        lst_div = div_tablita.find_all("div", recursive=False) # 为什么递归是false？
        if lst_div:
            for div in lst_div:
                span = div.find("span")
                if span:
                    span_text = span.get_text(strip=True)
                    if span_text.rstrip(":") in CSV_TITLE:
                        lst_data[CSV_TITLE.index(span_text.rstrip(":"))] \
                            = div.get_text(strip=True).strip(span_text).strip()
    # 接下来是Program Day
    # lst_program_table = soup.find_all("table", class_="programTable")
    # if lst_program_table:
    #     # 定义所有天的字符串列表，每个之间将用;隔开
    #     lst_program_days_text = []
    #     for program_table in lst_program_table:
    #         lst_tr = program_table.find_all("tr")
    #         if lst_tr:
    #             # 定义某天的字符串列表，每个之间将用;隔开
    #             lst_program_day_text = []
    #             for tr in lst_tr:
    #                 lst_td = tr.find_all("td")
    #                 if lst_td and len(lst_td) >= 2:
    #                     lst_program_day_text.append(lst_td[1].get_text(strip=True))
    #             lst_program_days_text.append(" ".join(lst_program_day_text))
    #     lst_data[-1] = "||".join(lst_program_days_text)
    return lst_data


def create_csv():
    """
    创建csv
    :return:
    """
    global CSV_FILE_NAME, CSV_TITLE
    if os.path.exists(CSV_FILE_NAME):
        return
    with open(CSV_FILE_NAME, "w", encoding="utf-8", newline="") as file:
        csv_write = csv.writer(file)
        csv_write.writerow(CSV_TITLE)


def save_csv(lst_data):
    """
    保存数据
    :param lst_data:
    :return:
    """
    if not lst_data:
        return
    global CSV_FILE_NAME
    with open(CSV_FILE_NAME, "a", encoding="utf-8", newline="") as file:
        csv_write = csv.writer(file)
        for data in lst_data:
            csv_write.writerow(data)


def dispose_csv():
    """
    处理csv
    :return:
    """
    global CSV_FILE_NAME
    trip_f = open("thefly_trip.csv", "a", encoding="utf-8", newline="")
    csv_write_trip = csv.writer(trip_f)
    csv_write_trip.writerow(CSV_TITLE)
    tour_f = open("thefly_tour.csv", "a", encoding="utf-8", newline="")
    csv_write_tour = csv.writer(tour_f)
    csv_write_tour.writerow(CSV_TITLE)
    with open(CSV_FILE_NAME, "r", encoding="utf-8", newline="") as file:
        csv_reader = csv.reader(file)
        for i, data in enumerate(csv_reader):
            if i == 0:
                continue
            if "trip" in data[1]:
                csv_write_trip.writerow(data)
            elif "tour" in data[1]:
                csv_write_tour.writerow(data)
            elif "road show" in data[1]:
                csv_write_roadshow.writerow(data)
    trip_f.close()
    tour_f.close()


if __name__ == '__main__':
    main()
#dispose_csv()
