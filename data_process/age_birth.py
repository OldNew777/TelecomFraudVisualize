import csv

reader = csv.reader(open("data/criminals_processed.csv", "r", encoding="utf-8"))

results = {
    "男": [0] * 20,
    "女": [0] * 20
}

for i, line in enumerate(reader):
    if i == 0:
        continue
    year = int(line[2].split("-")[0])
    age = 2021 - year
    age_bin = age // 5
    results[line[1].strip(" ")][age_bin] += 1
    print(line[1], age)
    # input()

import json
json.dump(results, open("data/age_birth.json", "w", encoding="utf-8"), ensure_ascii=False)
print(results)