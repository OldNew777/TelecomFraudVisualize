import json
import re
from tqdm import tqdm


def parse_criminal(data):
    all_criminals = []
    for item in tqdm(data):
        content = item["全文"]
        pattern = r"被告人([^,，]*).*([男女]).*?(\d+年\d+月\d+日)出生.*[,，](.*?文化|文化程度.*?|.*?文化程度)[,，]"
        # TODO: 不一定有文化程度
        results = re.findall(pattern, content)
        for item in results:
            all_criminals.append(item)
    return all_criminals


def parse(path):
    data = json.load(open(path, "r", encoding="utf-8"))
    print(f"{len(data)} items loaded.")
    all_criminals = parse_criminal(data)
    print(f"{len(all_criminals)} criminals parsed.")
    return all_criminals


if __name__ == "__main__":
    all_criminals = parse("data/data.json")
    with open("data/criminals.csv", "w", encoding="utf-8") as f:
        f.write("姓名, 性别, 出生日期, 文化程度\n")
        for item in all_criminals:
            f.write(", ".join(item))
            f.write("\n")
