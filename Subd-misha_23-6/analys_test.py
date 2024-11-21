import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt
import pandas as pd
import numpy as np
import sqlite3
import pandas as pd
import numpy as np
from dateutil import parser
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QDate,QLocale
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QTableView, QMessageBox, QTableWidgetItem,QLabel
from PyQt6.QtGui import QStandardItemModel, QStandardItem,QIntValidator, QDoubleValidator, QAction



class AnalysisWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализ фьючерсов")
        self.initUI()
        db_name = 'Subd2.db'
        self.dfConvertDate = self.prepare_dates(self.get_table('stat', db_name))

    def prepare_dates(self, df):
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

    def get_table(self, table_name, db_name):
        try:
            conn = sqlite3.connect(db_name)
            data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            if data.empty:
                print("Нет данных в таблице!")
                return pd.DataFrame()
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return pd.DataFrame()  # Возвращаем пустой DataFrame в случае ошибки
        finally:
            conn.close()
        return data

    def initUI(self):
        layout = QVBoxLayout()

        # Поле для ввода даты
        self.date_input = QLineEdit(self)
        self.date_input.setPlaceholderText("Введите дату (например, 05-05-96)")
        layout.addWidget(self.date_input)

        # Кнопка для запуска анализа
        self.calculate_button = QPushButton("Рассчитать", self)
        self.calculate_button.clicked.connect(self.calculate_statistics)
        layout.addWidget(self.calculate_button)

        # Таблица для отображения результатов
        self.results_table = QTableView(self)
        layout.addWidget(self.results_table)

        self.setLayout(layout)


    def validate_date(self, date_str):
        try:
            parsed_date = parser.parse(date_str)
            return True  # Дата корректна
        except (ValueError, OverflowError) as e:
            print(f"Ошибка при парсинге даты '{date_str}': {e}")  # Дополнительная отладочная информация
            return False  # Ошибка при парсинге?
    def display_results(self, result_rk, result_xk):
        model = QStandardItemModel()

        # Установка заголовков
        model.setHorizontalHeaderLabels(
            ["Фьючерс"] + [f"День {i}" for i in range(1, max(len(result_xk), len(result_rk)) + 1)])

        # Наполнение модели данными
        for future_name, rk_values in result_rk.items():
            row = [QStandardItem(future_name)]
            # Добавляем значение rk для текущего фьючерса
            row.append(QStandardItem(str(rk_values)))  # Если вы хотите показать rk
            # Теперь добавим значения xk
            if future_name in result_xk:
                for value in result_xk[future_name]:
                    row.append(QStandardItem(str(value) if value is not None else ""))
            # Добавляем строку в модель
            model.appendRow(row)

        # Установка модели в QTableView
        self.results_table.setModel(model)

    def perform_calculations(self, selected_date):
        try:
            df = self.get_data_before_date(selected_date)
            print(f"Данные загружены: \n{df}")  # Выводим данные для проверки
            if df is None or df.empty:
                QMessageBox.warning(self, "Ошибка", "Данные не загружены!")
                return None, None  # Возвращаем None, None, если данных нет

            unique_futures = df["name"].unique()
            r_k_values = {}
            x_k_values = {}

            for future in unique_futures:
                future_data = df[df["name"] == future].sort_values(by="torg_date")
                if len(future_data) < 3:
                    print(f"Недостаточно данных для фьючерса {future}")  # Сообщение об ошибке
                    continue

                T_pk = future_data["day_end"].values[0]
                days_diff = (future_data["torg_date"].diff().dt.days).fillna(0)

                # Проверка на нулевые значения
                if (days_diff == 0).any():
                    print(f"Нулевое значение days_diff для фьючерса {future}")
                    continue

                r_k = np.log(future_data["quotation"] / 100) / days_diff
                r_k_values[future] = r_k.tolist()

                if len(r_k) >= 3:
                    x_k = np.log(r_k[2:] / r_k[:-2])
                    x_k_values[future] = x_k.tolist()

            return r_k_values, x_k_values
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Произошла ошибка: {e}")
            return None, None  # Возвращаем None, None при любой ошибке

    def calculate_statistics(self):
        input_date = self.date_input.text()
        print(f'Введенная дата: {input_date}')  # Отладка: вывод введенной даты
        if not self.validate_date(input_date):
            QMessageBox.warning(self, "Ошибка ввода", "Неверный формат даты. Используйте: ДД-МММ-ГГ.")
            return

        try:
            result_rk, result_xk = self.perform_calculations(input_date)
            if result_rk is None or result_xk is None:  # Проверка на None
                QMessageBox.warning(self, "Ошибка", "Расчеты не выполнены. Проверьте данные.")
                return  # Выходим, если произошла ошибка в perform_calculations

            self.display_results(result_rk, result_xk)  # Передаем результаты в display_results
        except Exception as e:
            QMessageBox.critical(self, "Критическая ошибка", f"Произошла ошибка: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalysisWindow()
    data=window.get_table('stat', 'Subd2.db')
    print(type(data['start_date']))
    window.show()
    sys.exit(app.exec())