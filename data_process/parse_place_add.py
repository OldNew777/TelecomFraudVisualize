import json
import re
from geopy.geocoders import Nominatim
from tqdm import tqdm
import os

def parse_place(data):
    geo = Nominatim(user_agent="sb")
    info = json.load(open("data/place.json", "r", encoding="utf-8"))
    for d in data:
        if d["文书ID"] in info.keys():
            info[d["文书ID"]]["keywords"] = d["关键字"]
            info[d["文书ID"]]["title"] = d["案件名称"]
    json.dump(info, open("data/place2.json", "w", encoding="utf-8"), ensure_ascii=False)

    return info

def parse(path):
    data = json.load(open(path, "r", encoding="utf-8"))
    print(f"{len(data)} items loaded.")
    info = parse_place(data)
    print(f"{len(info)} items parsed.")

if __name__ == "__main__":
    info = parse("data/data.json")