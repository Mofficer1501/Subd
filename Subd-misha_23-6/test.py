import sqlite3
import pandas as pd
db_name = 'Subd2.db'


def get_table(table_name, db_name):
    conn = sqlite3.connect(db_name)
    data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return data



def prepare_dates(df):
    """ Подготовка и преобразование дат в DataFrame """
    month_translation = {
        "Янв": "Jan", "Фев": "Feb", "Мар": "Mar", "Апр": "Apr",
        "Май": "May", "Июн": "Jun", "Июл": "Jul", "Авг": "Aug",
        "Сен": "Sep", "Окт": "Oct", "Ноя": "Nov", "Дек": "Dec"
    }

    # Замена русских названий месяцев на английские
    for column in df.columns:
        if 'start_date' in column.lower():
            df[column] = df[column].replace(month_translation, regex=True)

    # Преобразование строк в формат даты
    for column in df.columns:
        if 'start_date' in column.lower():
            df[column] = pd.to_datetime(df[column], format='%d-%b-%y', errors='coerce')

    return df


# def prepare_dates(df):
# #     """ Подготовка и преобразование дат в DataFrame """
# #     month_translation = {
# #         "Янв": "Jan", "Фев": "Feb", "Мар": "Mar", "Апр": "Apr",
# #         "Май": "May", "Июн": "Jun", "Июл": "Jul", "Авг": "Aug",
# #         "Сен": "Sep", "Окт": "Oct", "Ноя": "Nov", "Дек": "Dec"
# #     }
# #
# #     # Замена русских названий месяцев на английские и преобразование в datetime для start_date
# #     if 'start_date' in df.columns:
# #         try:
# #             df['start_date'] = df['start_date'].replace(month_translation, regex=False) # regex=False для точности
# #             df['start_date'] = pd.to_datetime(df['start_date'], format='%d-%b-%y', errors='coerce')
# #         except (KeyError, ValueError, TypeError) as e:
# #             print(f"Ошибка при обработке столбца 'start_date': {e}")
# #             #Здесь нужно добавить обработку ошибки, например,  заполнение NaN или пропуск столбца
# #
# #     return df

#
#
# def process_data():
#     # 1. Получение и обработка данных
#     df = get_table('stat', 'Subd2.db')
#
#     # 2. Обработка дат
#     df = prepare_dates(df)
#
#     return df


data = get_table('stat', 'Subd2.db')

data = prepare_dates(data)

data.to_csv('output.csv', index=False, encoding='utf-8')


