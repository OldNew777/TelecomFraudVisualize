import os
import pandas
import re


chinese_character_pattern = r"[\u4e00-\u9fa5]"
name_pattern = re.compile(r"[\u4e00-\u9fa5\*xX]+")

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

def post_process(csv_path, output_path):
    # read csv by pandas
    df = pandas.read_csv(csv_path, encoding="gbk", index_col=False)
    print(df.head())

    # rename columns to remove spaces
    rename_dict = {}
    for column in df.columns:
        rename_dict[column] = domain_name_translator[column.strip()]
    df.rename(columns=rename_dict, inplace=True)

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

    # save to csv
    df.to_csv(output_path, index=False, encoding="gbk")


if __name__ == "__main__":
    post_process("data/criminals.csv", "data/criminals_processed.csv")
