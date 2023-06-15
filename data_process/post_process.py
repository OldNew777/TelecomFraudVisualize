import os
import pandas
import json
import re
from datetime import datetime


chinese_character_pattern = r"[\u4e00-\u9fa5]"
name_pattern = re.compile(r"[\u4e00-\u9fa5\*xX]+[0-9]*")

domain_name_translator = {
    "姓名": "name",
    "性别": "gender",
    "出生日期": "birthday",
    "文化程度": "education",
}

name_pattern_drop_0 = [
    re.compile(r"于[\d]+年"),
    re.compile(r"（"),
    re.compile(r"\("),
]
name_pattern_drop_1 = [
    re.compile(r"化名"),
    re.compile(r"绰号"),
    re.compile(r"代号"),
    re.compile(r"外号"),

    re.compile(r"曾用名"),
    re.compile(r"又名"),
    re.compile(r"别名"),
    re.compile(r"小名"),
    re.compile(r"乳名"),
    re.compile(r"英文名"),

    re.compile(r"原审"),
    re.compile(r"自报"),
]

education_pattern_drop = [
    '文化程度',
    '文化',
]
education_dict = {
    '文盲': '文盲',
    '小学': '小学',

    '初中': '初中',
    '中学': '初中',
    '国中': '初中',
    '初': '初中',

    '高中': '高中',
    '中专': '中专',
    '大专': '大专',
    '本科': '本科',
    '硕士': '硕士',
    '博士': '博士',

    '大学专科': '大专',
    '职高': '大专',
    '高职': '大专',
    '专科': '中专',
    '职中': '中专',
    '技工': '中专',
    '中等专科': '中专',
    '中技': '中专',
    '大学': '本科',
    '研究生': '硕士',
}


def process_name(name):
    name_bak = name
    name = str(name)
    if name == 'nan':
        name = '未知'
    name = name.replace('被告人', '')
    for pattern in name_pattern_drop_0:
        index = pattern.search(name)
        if index:
            name = name[:index.start()]
    for pattern in name_pattern_drop_1:
        index = pattern.search(name)
        if index and not re.match(chinese_character_pattern, name[index.start()-1]):
            name = name[:index.start() - 1]
    name_list = name_pattern.findall(name)
    if len(name_list) == 1:
        name = name_list[0]
    else:
        name = "未知"
    return name


def date_process(birthday):
    if '-' not in birthday:
        # format 2017年12月1日 to 2017-12-01
        birthday = birthday.replace(
            '年', '-').replace('月', '-').replace('日', '').strip(' ')
        
    y, m, d = birthday.split('-')
    if len(y) == 3:
        if y[0] == '0':
            y = f'2{y}'
        else:
            y = f'1{y}'
    elif len(y) == 2:
        if int(y) > 23:
            y = f'19{y}'
        else:
            y = f'20{y}'
    if len(m) == 1:
        m = f'0{m}'
    if len(d) == 1:
        d = f'0{d}'
    birthday = f'{y}-{m}-{d}'

    try:
        birthday = datetime.strptime(birthday, '%Y-%m-%d').strftime('%Y-%m-%d')
    except Exception as e:
        if m == '02' and d == '29':
            birthday = f'{y}-02-28'
            birthday = datetime.strptime(birthday, '%Y-%m-%d').strftime('%Y-%m-%d')
        else:
            print(f'birthday error: {birthday}')
            raise e
    return birthday


def process_criminals(csv_path, output_path):
    # read csv by pandas
    df = pandas.read_csv(csv_path, encoding="utf-8", index_col=False)
    print(df.head())

    # rename columns to remove spaces
    rename_dict = {}
    for column in df.columns:
        rename_dict[column] = domain_name_translator[column.strip()]
    df.rename(columns=rename_dict, inplace=True)

    df["name"] = df["name"].apply(process_name)

    # filter empty rows
    df = df[(~df["gender"].isnull()) & (
        ~df["birthday"].isnull()) & (~df["education"].isnull())]

    education_set = set()

    def education_level_process(education_level):
        education_level_bak = education_level

        for pattern in education_pattern_drop:
            education_level = education_level.replace(pattern, '')

        downgraded = False
        if '肄业' in education_level:
            downgraded = True

        for key, value in education_dict.items():
            if key in education_level:
                education_level = value

        if downgraded:
            education_level += '肄业'

        if education_level.strip() == '':
            education_level = '未知'

        education_set.add(education_level)

        return education_level
    df["education"] = df["education"].apply(education_level_process)
    print(education_set)

    df["birthday"] = df["birthday"].apply(date_process)

    # save to csv
    df.to_csv(output_path, index=False, encoding="utf-8")


def days_to_ymd(days):
    y = days // 365
    m = (days % 365) // 30
    d = (days % 365) % 30
    return y, m, d


def date_to_utf8(date: str):
    for i in range(65296, 65306):
        date = date.replace(chr(i), str(i - 65296))
    return date_process(date)


def process_date_range(input_path, output_path):
    data = json.load(open(input_path, encoding="utf-8"))
    date_range_dict = {}
    for item in data:
        id = item['文书ID']
        end_time = datetime.strptime(item["裁判日期"], "%Y-%m-%d")
        record = item["诉讼记录"]
        # match xxxx年x月x日
        start_time = re.search(r"[\d]{4}年[\d]{1,2}月[\d]{1,2}日", record)
        if start_time:
            # transform from unicode to utf-8 string
            start_time = start_time.group()
            start_time = date_to_utf8(start_time)
            start_time = datetime.strptime(start_time, "%Y-%m-%d")
            date_range = end_time - start_time
        else:
            print(f"no start time found for {id}")
            continue
        date_range_dict[id] = {"判罚经过天数": date_range.days}
    
    json.dump(date_range_dict, open(output_path, "w", encoding="utf-8"), ensure_ascii=False)


if __name__ == "__main__":
    # process_criminals("data/criminals.csv", "data/criminals_processed.csv")
    process_date_range("data/data - slice.json", "data/data - slice_processed.json")

    # date = '2016-0５-20'
    # print(ord('５'))
    # print(chr(65296))
    # print(date_to_utf8(date))
