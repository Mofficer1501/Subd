import pandas as pd

# Загрузка данных
try:
    df_Zb = pd.read_csv('Zb.csv')
    df_f_zb = pd.read_csv('f_zb.csv')
except FileNotFoundError as e:
    print(f"Ошибка: {e}")
    exit()

def text_to_date(df_table, column_name):
    month_translation = {
        'Jan': 'Янв', 'Feb': 'Фев', 'Mar': 'Мар', 'Apr': 'Апр',
        'May': 'Май', 'Jun': 'Июн', 'Jul': 'Июл', 'Aug': 'Авг',
        'Sep': 'Сен', 'Oct': 'Окт', 'Nov': 'Ноя', 'Dec': 'Дек'
    }
    if df_table[column_name].str.contains(r'\b(Янв|Фев|Мар|Апр|Май|Июн|Июл|Авг|Сен|Окт|Ноя|Дек)\b').any():
        print(f"Столбец '{column_name}' уже содержит преобразованные данные.")
        return

    df_table[column_name] = df_table[column_name].astype(str)

    # Разбиваем даты на части
    split_dates = df_table[column_name].str.split('-', expand=True)
    if split_dates.shape[1] != 3:
        print(f"Ошибка: Неверный формат даты в столбце '{column_name}'.")
        return

    day = split_dates[0]
    month_abbr = split_dates[1]
    year = split_dates[2]

    month_rus = month_abbr.map(month_translation)

    # Собираем обратно в нужный формат
    df_table[column_name] = day + '-' + month_rus + '-' + year
def text_to_float(df_table, column_names):
    for column_name in column_names:
        if column_name not in df_table.columns:
            print(f"Ошибка: Столбец '{column_name}' не найден в DataFrame.")
            continue
        df_table[column_name] = pd.to_numeric(df_table[column_name], errors='coerce').round(2)
def text_to_int(df_table, column_names):
    for column_name in column_names:
        if column_name not in df_table.columns:
            print(f"Ошибка: Столбец '{column_name}' не найден в DataFrame.")
            continue
        df_table[column_name] = pd.to_int(df_table[column_name])

text_to_date(df_Zb, 'exec_date')
df_Zb.to_csv('Zb.csv', index=False)

text_to_date(df_f_zb, 'torg_date')
text_to_date(df_f_zb, 'day_end')
text_to_float(df_f_zb, ['quotation', 'min_quot', 'max_quot'])
text_to_int(df_f_zb, 'num_contr')
df_f_zb.to_csv('f_zb.csv', index=False)