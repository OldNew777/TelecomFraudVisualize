import json
import re
from geopy.geocoders import Nominatim
from tqdm import tqdm
import os

def parse_place(data):
    geo = Nominatim(user_agent="sb")
    info = {}
    if os.path.exists("data/place.json"):
        info = json.load(open("data/place.json", "r", encoding="utf-8"))
    for item in tqdm(data):
        id = item["文书ID"]
        if id in info.keys():
            continue
        place = item["法院名称"]
        place_pattern = re.compile(r"^.*?[省市区县旗]")
        place_result = re.findall(place_pattern, place)
        if len(place_result) == 0:
            print(place)
            continue
        place_result = place_result[0]
        if "省" not in place_result and place_result not in ["北京市", "天津市", "上海市", "重庆市"]:
            try_cnt = 0
            place_geo = None
            while True:
                try:
                    try_cnt += 1
                    place_geo = geo.geocode(place_result)
                    break
                except KeyboardInterrupt as e:
                    raise e
                except:
                    if try_cnt > 5:
                        break
                    print(f"retry {try_cnt} {place_result}")
            if place_geo == None:
                continue

            place_geo = place_geo.__str__().split(", ")
            for item_place in place_geo[::-1]:
                if "省" in item_place:
                    place_geo = item_place
                    break
                elif item_place in ["北京市", "天津市", "上海市", "重庆市"]:
                    place_geo = item_place
                    break
                elif "自治区" in item_place:
                    item_place = item_place.split("自治区")[0] + "自治区"
                    place_geo = item_place
                    break
                else:
                    place_geo = None
            if place_geo == None:
                continue
            place_result = place_geo
        date = item["裁判日期"]
        criminals = item["当事人"]
        # print(place_result)
        print(place_result)
        info[id] = {
            "place": place_result,
            "date": date,
            "criminals": criminals,
        }
        json.dump(info, open("data/place.json", "w", encoding="utf-8"), ensure_ascii=False)

    return info

def parse(path):
    data = json.load(open(path, "r", encoding="utf-8"))
    print(f"{len(data)} items loaded.")
    info = parse_place(data)
    print(f"{len(info)} items parsed.")

if __name__ == "__main__":
    info = parse("data/data.json")