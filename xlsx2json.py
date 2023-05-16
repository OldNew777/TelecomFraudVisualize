import json
import pandas as pd
import sys
import os


def xlsx2json(xlsx_file):
    json_file = xlsx_file.replace('.xlsx', '.json')

    print(f'Loading {xlsx_file}...')
    df = pd.read_excel(xlsx_file)
    print(df.keys())

    remove_key = []
    for i in range(len(df.keys())):
        # find if the column is empty
        if df[df.keys()[i]].isnull().all():
            remove_key.append(df.keys()[i])
    print(f'Columns {remove_key} are empty, removing...')
    for key in remove_key:
        # remove the empty column
        df.drop(key, axis=1, inplace=True)
    print(df.keys())

    def convert_to_dict(df):
        dict = []
        # convert dataframe to dictionary
        for i in range(len(df)):
            d = df.iloc[i].to_dict()
            for key in d.keys():
                if type(d[key]) is float and pd.isna(d[key]):
                    d[key] = ''
                value = d[key].replace('\'', '"')

                try:
                    d[key] = json.loads(value)
                except:
                    pass
            dict.append(d)
        return dict

    dict = convert_to_dict(df)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    xlsx2json('data/data.xlsx')
