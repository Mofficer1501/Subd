import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий
import sqlite3
import pandas as pd
import numpy as np

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QDate,QLocale
from PyQt6.QtWidgets import QVBoxLayout, QLineEdit, QPushButton, QTableView, QMessageBox, QTableWidgetItem,QLabel
from PyQt6.QtGui import QStandardItemModel, QStandardItem,QIntValidator, QDoubleValidator, QAction

import MainForm  # Это наш конвертированный файл дизайна
class AnalysisWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализ фьючерсов")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Поле для ввода даты
        self.date_input = QLineEdit(self)
        self.date_input.setPlaceholderText("Введите дату (например, 05-Июн-96)")
        layout.addWidget(self.date_input)

        # Кнопка для запуска анализа
        self.calculate_button = QPushButton("Рассчитать", self)
        self.calculate_button.clicked.connect(self.calculate_statistics)
        layout.addWidget(self.calculate_button)

        # Таблица для отображения результатов
        self.results_table = QTableView(self)
        layout.addWidget(self.results_table)

        self.setLayout(layout)

    def calculate_statistics(self):
        input_date = self.date_input.text()
        if not self.validate_date(input_date):
            QMessageBox.warning(self, "Ошибка ввода", "Неверный формат даты. Используйте: ДД-МММ-ГГ.")
            return

        result = self.perform_calculations(input_date)

        # Отображение результатов в таблице
        self.display_results(result)

    def perform_calculations(self, selected_date):
        df = self.get_data_before_date(selected_date)

        if df.empty:
            QMessageBox.warning(self, "Нет данных", "Нет данных для анализа до данной даты.")
            return {}

        futures = df["name"].unique()
        results = {future: [] for future in futures}

        for future in futures:
            future_data = df[df["name"] == future].sort_values(by="torg_date")
            rk_values = self.calculate_rk(future_data)
            xk_values = self.calculate_xk(rk_values)

            results[future] = xk_values

        return results

    def calculate_rk(self, future_data):
        T_pm = future_data["day_end"].values[0]
        days_diff = future_data["torg_date"].diff().dt.days.fillna(0)

        rk = np.log(future_data["quotation"] / 100) / days_diff
        return rk.tolist()

    def calculate_xk(self, rk_values):
        if len(rk_values) < 3:
            return []  # Не достаточно данных для расчетов
        xk = np.log(np.array(rk_values[2:]) / np.array(rk_values[:-2]))
        return xk.tolist()

    def get_data_before_date(self, selected_date):
        conn = sqlite3.connect('Subd2.db')
        query = f"SELECT * FROM stat WHERE torg_date <= '{selected_date}'"
        df = pd.read_sql(query, conn)
        conn.close()
        df['torg_date'] = pd.to_datetime(df['torg_date'], format='%d-%b-%y')
        return df

    def validate_date(self, date_string):
        try:
            pd.to_datetime(date_string, format='%d-%b-%y')
            return True
        except ValueError:
            return False

    def display_results(self, results):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Фьючерс"] + [f"День {i}" for i in range(1, len(next(iter(results.values()))) + 1)])

        for future, xk_values in results.items():
            row = [QStandardItem(future)] + [QStandardItem(str(v)) if v is not None else QStandardItem("") for v in xk_values]
            model.appendRow(row)

        self.results_table.setModel(model)


'''class AnalysisWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализ фьючерсов")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Поле для ввода даты
        self.date_input = QLineEdit(self)
        self.date_input.setPlaceholderText("Введите дату (например, 05-Июн-96)")
        layout.addWidget(self.date_input)

        # Кнопка для запуска анализа
        self.calculate_button = QPushButton("Рассчитать", self)
        self.calculate_button.clicked.connect(self.calculate_statistics)
        layout.addWidget(self.calculate_button)

        # Таблица для отображения результатов
        self.results_table = QTableView(self)
        layout.addWidget(self.results_table)

        self.setLayout(layout)

    def calculate_statistics(self):
        input_date = self.date_input.text()
        if not self.validate_date(input_date):
            QMessageBox.warning(self, "Ошибка ввода", "Неверный формат даты. Используйте: ДД-МММ-ГГ.")
            return

        result_rk, result_xk = self.perform_calculations(input_date)

        # Отображение результатов в таблице
        self.display_results(result_rk, result_xk)

    def perform_calculations(self, selected_date):
        df = self.get_data_before_date(selected_date)
        r_k_values = {}
        x_k_values = {}

        unique_futures = df["name"].unique()

        for future in unique_futures:
            future_data = df[df["name"] == future].sort_values(by="torg_date")

            # Вычисление r_k
            T_pk = future_data["day_end"].values[0]  # Предполагается, что это дата погашения на первый день
            days_diff = (future_data["torg_date"].diff().dt.days).fillna(0)  # Разница в днях

            if len(future_data) < 3:
                continue  # Пропустить, если недостаточно данных

            r_k = np.log(future_data["quotation"] / 100) / days_diff
            r_k_values[future] = r_k.tolist()

            # Вычисление x_k
            if len(r_k) >= 3:  # Убедимся, что достаточно данных для вычисления x_k
                x_k = np.log(r_k[2:] / r_k[:-2])
                x_k_values[future] = x_k.tolist()

        return r_k_values, x_k_values

    def get_data_before_date(self, selected_date):
        # Подключение к базе данных и получение данных до выбранной даты
        conn = sqlite3.connect('Subd2.db')
        query = f"SELECT * FROM stat WHERE torg_date <= '{selected_date}'"
        df = pd.read_sql(query, conn)
        conn.close()

        # Преобразуем 'torg_date' в формат даты
        df['torg_date'] = pd.to_datetime(df['torg_date'], format='%d-%b-%y')

        return df

    def validate_date(self, date_string):
        try:
            pd.to_datetime(date_string, format='%d-%b-%y')
            return True
        except ValueError:
            return False

    def display_results(self, r_k, x_k):
        # Создаем модель для отображения данных
        from PyQt6.QtGui import QStandardItemModel, QStandardItem

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Фьючерс", "r_k", "x_k"])

        for future, rk_values in r_k.items():
            row = [QStandardItem(future)]
            row.append(QStandardItem(", ".join(map(str, rk_values))))  # Добавляем все r_k значения
            row.append(QStandardItem(", ".join(map(str, x_k.get(future, [])))))  # Добавляем x_k если есть
            model.appendRow(row)

        self.results_table.setModel(model)'''

class MainWindow(QtWidgets.QMainWindow, MainForm.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        db_name = 'Subd2.db'
        
        self.table_name = None

        '''-------------------Пропорциональное размещение виджетов-------------------------------------------'''
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.model = QStandardItemModel()
        self.tableView.setModel(self.model)
        self.tableView.hideColumn(0)
        '''-----------------------------------------------------------------------------------------'''

        # start_date, name, exec_date, price, min_price, max_price, contacts_quantity


        '''-------------------Привязка таблиц к виджету-------------------------------------------'''
        self.kontrakti_data = self.get_table('contractss', db_name)
        self.statistics_data = self.get_table('stat', db_name)

        self.Kontrakti.triggered.connect(lambda: self.load_table_from_db('contractss', db_name))
        self.Statistika.triggered.connect(lambda: self.load_table_from_db('stat', db_name))
        self.Union.triggered.connect(lambda: self.update_summary_table(db_name))
        '''-----------------------------------------------------------------------------------------'''
        
        


        '''-------------------Компоновка элементов главного окна-------------------------------------------'''
        # Создаем центральный виджет
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        # Создаем вертикальный layout и устанавливаем его в центральный виджет
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        # Создаем QTableView
        self.tableView = QtWidgets.QTableView()
        
        self.tableView.verticalHeader().setVisible(True)
        

        # Выделение всей строки при наведении 
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        self.tableView.setFocus()
        self.layout.addWidget(self.tableView)
        self.tableView.setSortingEnabled(True)

        # Кнопки
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.EditButton)
        self.button_layout.addWidget(self.AddButton)
        self.button_layout.addWidget(self.DeleteButton)
        self.DeleteButton.clicked.connect(self.confirmAndDeleteSelectedRows)
        self.EditButton.clicked.connect(self.editRecord)
        self.AddButton.clicked.connect(self.addRecord)
        self.layout.addLayout(self.button_layout)
        # self.layout.addWidget(self.formWidget)
        # self.layout.addWidget(self.formTypeLabel)
        '''-----------------------------------------------------------------------------------------'''

        #Конвертация дат(месяцев) в таблице стат в валидный для класса Анализис тип
        self.data = self.get_table('stat', 'Subd2.db')
        self.dfConvertDate = self.prepare_dates(self.data)
        self.data.to_csv('output.csv', index=False, encoding='utf-8')
        #####
        self.setupUi(self)
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()
        self.menu_analysis = menubar.addMenu("Анализ")

        # Создаем действие для открытия окна анализа
        self.action_open_analysis = QAction("Открыть анализ", self)
        self.action_open_analysis.triggered.connect(self.open_analysis_window)
        self.menu_analysis.addAction(self.action_open_analysis)

    def open_analysis_window(self):
        self.analysis_window = AnalysisWindow()  # Создаем экземпляр окна анализа
        self.analysis_window.show()
        # Кнопка в строке меню для запуска анализа данных
        """self.analyze_button = QtWidgets.QPushButton("Analyze Data", self)
        self.analyze_button.clicked.connect(self.process_data)
        self.setCentralWidget(self.analyze_button)"""

        '''self.setupUi(self)  # Вызываем setupUi из Ui_MainWindow
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        # Подключаем сигнал к слоту. Важно: это должно быть после setupUi!
        self.FuchersBar.triggered.connect(self.show_analysis_window)

    def show_analysis_window(self):
        self.analysis_window = AnalysisWindow()
        self.analysis_window.show()'''
##########################

    #     self.setupUi(self)  # Инициализация интерфейса
    #     # Другие инициализации...
    #
    #     # Создание пункта меню "Анализ"
    #     self.create_menu()
    #
    #
    # def create_menu(self):
    #     menubar = self.menuBar()  # Получаем меню
    #     self.menu_analysis = menubar.addMenu("Анализ")  # Создаем меню "Анализ"

        # # Создаем действие в меню для открытия окна анализа
        # self.action_open_analysis = QAction("Открыть анализ", self)
        # self.action_open_analysis.triggered.connect(self.open_analysis_window)  # Подключаем сигнал к методу
        # self.menu_analysis.addAction(self.action_open_analysis)  # Добавляем действие в меню


    # def open_analysis_window(self):
    #
    #     # Создаем экземпляр окна анализа
    #     self.analysis_window = AnalysisWindow()
    #     self.analysis_window.set_data(self.dfConvertDate)  # Передаем DataFrame в окно анализа
    #     self.analysis_window.show()


###################################



    # def process_data(self, df):
    #     # # 1. Получение и обработка данных
    #     # df = self.load_data_from_db('your_database.db', 'your_table')
    #     #
    #     # # 2. Обработка дат
    #     # df = self.prepare_dates(df)
    #
    #     # 3. Запуск окна анализа
    #     analysis_window = AnalysisWindow()
    #     analysis_window.run_analysis(df)  # Передаем DataFrame в анализ

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


    
    def editRecord(self): # ----------------
        self.open_popup("edit")
        print('table_name=',self.table_name)
        selectedIndexes = self.tableView.selectionModel().selectedRows()
        if not selectedIndexes:
            return
        index = selectedIndexes[0].row()

        if self.table_name == 'contractss':
            self.nameEdit.setText(self.model.item(index, 1).text())
            self.nameEdit.setReadOnly(True)
            self.codeEdit.setText(self.model.item(index, 2).text())
            self.dateEdit.setDate(QDate.fromString(self.model.item(index, 3).text(), "dd-MMM-yy"))
            self.idEdit.setText(self.model.item(index, 0).text()) 
        elif self.table_name == 'stat':
            # self.nameComboBox.setItemText(self.model.item(index, 1).text())
            self.nameEdit.setText(self.model.item(index, 1).text())
            # self.nameComboBox.setDisabled(True)
            self.nameEdit.setReadOnly(True)
            self.start_dateEdit.setDate(QDate.fromString(self.model.item(index, 2).text(), "dd-MMM-yy"))
            self.dateEdit.setDate(QDate.fromString(self.model.item(index, 3).text(), "dd-MMM-yy"))
            self.idEdit.setText(self.model.item(index, 0).text())
            self.priceEdit.setText(self.model.item(index, 4).text())
            self.min_priceEdit.setText(self.model.item(index, 5).text())
            self.max_priceEdit.setText(self.model.item(index, 6).text())
            self.quantEdit.setText(self.model.item(index, 7).text())
        else :
            return

        self.formWidget.show()
        # self.formTypeLabel.setText("Редактирование записи")
        # self.formTypeLabel.show()
        # self.toggleButtons(False)
        self.currentRow = index
    

    # Добавление записи
    def addRecord(self):
        self.open_popup("add")
        self.nameEdit.clear()
        self.nameEdit.setReadOnly(False)
        self.priceEdit.clear()
        self.start_dateEdit.clear()
        self.max_priceEdit.clear()
        self.min_priceEdit.clear()
        self.quantEdit.clear()
        self.codeEdit.clear()
        self.idEdit.clear()
        self.dateEdit.setDate(QDate.currentDate())
        self.start_dateEdit.setDate(QDate.currentDate())
        # self.formWidget.show()
        self.currentRow = None
    
    def saveRecord(self):
        table_name = self.table_name
        if self.validate_form(table_name):
            db_name = 'Subd2.db' # ----------------
            # self.open_popup()
            if table_name == 'contractss':
                name = self.nameEdit.text()
                code = self.codeEdit.text()
                # date = self.dateEdit.date().toString("dd-MMM-yy")
                date = self.dateEdit.text()
            elif table_name == 'stat':
                name = self.nameEdit.text()   
                start_date = self.start_dateEdit.text()
                day_end = self.dateEdit.text()
                price = self.priceEdit.text()
                min_price = self.min_priceEdit.text()
                max_price = self.max_priceEdit.text()
                quant = self.quantEdit.text()

            if self.currentRow != None:
                id = self.idEdit.text()


            # if not self.validateInput(name, code):
            #     QtWidgets.QMessageBox.warning(self, "Ошибка", "Некорректный ввод данных.")
            #     return

            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            if self.currentRow is None:
                if table_name == 'contractss':
                    cursor.execute(f"INSERT INTO {table_name} (name, base, exec_date) VALUES (?, ?, ?)", (name, code, date))
                    new_id = cursor.lastrowid
                    print("newId=",new_id)
                    self.model.insertRow(0, [
                        QStandardItem(str(new_id)),
                        QStandardItem(name),
                        QStandardItem(code),
                        QStandardItem(date)
                    ])
                elif table_name == 'stat':
                    cursor.execute(f"INSERT INTO {table_name} (name, start_date, day_end,price,min_price,max_price,contracts_quantity) VALUES (?, ?, ?, ?, ?, ?,?)", (name, start_date, day_end,price,min_price,max_price,quant))
                    new_id = cursor.lastrowid
                    print("newId=",new_id)
                    self.model.insertRow(0, [
                        QStandardItem(str(new_id)),
                        QStandardItem(name),
                        QStandardItem(start_date),
                        QStandardItem(day_end),
                        QStandardItem(price),
                        QStandardItem(min_price),
                        QStandardItem(max_price),
                        QStandardItem(quant)
                    ])
                    print('stat')   
                self.tableView.selectRow(0)
            else:
                if table_name == 'contractss':
                    cursor.execute(f"UPDATE {table_name} SET name=?, base=?, exec_date=? WHERE id=?", (name, code, date, id))
                    print(id)
                    self.model.setItem(self.currentRow, 0, QStandardItem(id))
                    self.model.setItem(self.currentRow, 1, QStandardItem(name))
                    self.model.setItem(self.currentRow, 2, QStandardItem(code))
                    self.model.setItem(self.currentRow, 3, QStandardItem(date))
                    self.tableView.selectRow(self.currentRow)
                elif table_name == 'stat':
                    cursor.execute(f"UPDATE {table_name} SET name=?, start_date=?, day_end=?, price=?, min_price=?, max_price=?,contracts_quantity=? WHERE id=?", (name, start_date, day_end,price,min_price,max_price,quant, id))
                    print(id)
                    self.model.setItem(self.currentRow, 0, QStandardItem(id))
                    self.model.setItem(self.currentRow, 1, QStandardItem(name))
                    self.model.setItem(self.currentRow, 2, QStandardItem(start_date))
                    self.model.setItem(self.currentRow, 3, QStandardItem(day_end))
                    self.model.setItem(self.currentRow, 4, QStandardItem(price))
                    self.model.setItem(self.currentRow, 5, QStandardItem(min_price))
                    self.model.setItem(self.currentRow, 6, QStandardItem(max_price))
                    self.model.setItem(self.currentRow, 7, QStandardItem(quant))
                    self.tableView.selectRow(self.currentRow)  
                
            conn.commit()
            conn.close()
            
            self.nameEdit.clear()
            self.priceEdit.clear()
            self.start_dateEdit.clear()
            self.max_priceEdit.clear()
            self.min_priceEdit.clear()
            self.quantEdit.clear()
            self.codeEdit.clear()
            self.idEdit.clear()
            self.dateEdit.clear()
            # self.formWidget.show()
            self.currentRow = None
            self.formWidget.reject()
            QtWidgets.QMessageBox.information(self, "Сохранено", "Запись успешно сохранена.")
            # self.formWidget.hide()
            # self.formTypeLabel.hide()
            self.toggleButtons(True)
            # self.formWidget.setParent(None)
            # self.layout.removeWidget(self.formWidget)

    def reject_and_show_btns(self):
        self.formWidget.reject()
        self.toggleButtons(True)

    def fill_combobox(self):
        conn = sqlite3.connect('Subd2.db')
        cursor = conn.cursor()  
        cursor.execute("SELECT name, exec_date FROM contractss")
        securities = cursor.fetchall()  
        return securities

    def update_exec_date(self):
        # Получение даты исполнения из данных QComboBox
        # exec_date = self.nameComboBox.currentData()

        exec_date_str = self.nameComboBox.currentData()
        name = self.nameComboBox.currentText()
        self.nameEdit.setText(name)
        # exec_date = QDate.fromString(exec_date_str, "yy-MMM-dd")
        # print(exec_date)
        self.dateShow.setText(exec_date_str)  

    def get_window_title(self,title):
        if title == "add":
            return "Добавление"
        else:
            return "Редактирование"
    
    def open_popup(self,move_type):
        self.toggleButtons(False)
        # self.saveButton = QtWidgets.QPushButton("Сохранить")
        # self.saveButton.clicked.connect(self.saveRecord)
        self.formLayout = QtWidgets.QFormLayout()
        self.nameEdit = QtWidgets.QLineEdit()
        self.nameEdit.setInputMask("00000-0000")
        self.priceEdit = QtWidgets.QLineEdit()
        self.priceEdit.setPlaceholderText("Цена фьючерса")
        self.min_priceEdit = QtWidgets.QLineEdit()
        self.min_priceEdit.setPlaceholderText("минимальная цена фьючерса")
        self.max_priceEdit = QtWidgets.QLineEdit()
        self.max_priceEdit.setPlaceholderText("максимальная цена фьючерса")
        self.quantEdit = QtWidgets.QLineEdit()
        
        self.codeEdit = QtWidgets.QLineEdit()
        self.codeEdit.setPlaceholderText("ABCD1234")
        self.idEdit = QtWidgets.QLineEdit()
        self.dateEdit = QtWidgets.QDateEdit(calendarPopup=True)
        self.dateEdit.setDisplayFormat("dd-MMM-yy")

        self.start_dateEdit = QtWidgets.QDateEdit(calendarPopup=True)
        self.start_dateEdit.setDisplayFormat("dd-MMM-yy")
        self.nameComboBox = QtWidgets.QComboBox()
        # Валидаторы

        self.priceEdit.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.min_priceEdit.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.max_priceEdit.setValidator(QDoubleValidator(0.0, 999999.99, 2))
        self.quantEdit.setValidator(QIntValidator(0, 999999))

        if self.table_name == 'contractss':
            self.formLayout.addRow("Название:", self.nameEdit)
            self.formLayout.addRow("Код:", self.codeEdit)
            self.formLayout.addRow("Дата исполнения:", self.dateEdit)   
            # self.formLayout.addRow(self.saveButton)
        elif self.table_name == 'stat':
            self.dateShow = QtWidgets.QLineEdit()
            self.dateShow.setReadOnly(True)
            
            if move_type == "add":
                data_for_combobox = self.fill_combobox()
                for name, exec_date in data_for_combobox:
                    self.nameComboBox.addItem(name, exec_date)
                self.update_exec_date()    
                self.nameComboBox.currentIndexChanged.connect(self.update_exec_date)
                self.formLayout.addRow("Название:", self.nameComboBox)
            else:
                self.formLayout.addRow("Название:", self.nameEdit)
             # тут select с названиями бумаг
            # self.formLayout.addRow("Название:", self.nameEdit) # тут select с названиями бумаг
            self.formLayout.addRow("Дата начала:", self.start_dateEdit)
            self.formLayout.addRow("Дата окончания торгов:", self.dateEdit)
            if move_type == 'add':
                self.formLayout.addRow("Дата исполнения:", self.dateShow) # тут подтянется дата исполнения
            self.formLayout.addRow("Цена:", self.priceEdit)
            self.formLayout.addRow("Минимальная цена:", self.min_priceEdit)
            self.formLayout.addRow("Максимальная цена:", self.max_priceEdit)
            self.formLayout.addRow("Объем торгов:", self.quantEdit)
            # self.formLayout.addRow(self.saveButton)
        self.formWidget = QtWidgets.QDialog()
        self.formWidget.setWindowTitle(self.get_window_title(move_type))
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        cancel_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_button.setText("Ок")
        cancel_button.setText("Отмена")
        self.formLayout.addRow(buttonBox)
        buttonBox.accepted.connect(self.saveRecord)
        # buttonBox.rejected.connect(self.formWidget.reject)
        buttonBox.rejected.connect(self.reject_and_show_btns)
        buttonBox
        # self.formWidget = QtWidgets.QWidget()
        

        self.formWidget.setLayout(self.formLayout)
        self.formWidget.open()
        # self.formWidget.hide()
        # self.layout.addWidget(self.formWidget)
        # return 
    # Валидация ввода
    # def validateInput(self, name, code):
    #     if not name or not code:
    #         return False
    #     if not name.split('-')[0].isdigit() or len(name.split('-')[0]) != 5:
    #         return False
    #     if not name.split('-')[1].isdigit() or len(name.split('-')[1]) != 4:
    #         return False
    #     return True     

    # def validate_form(self):
    #     valid = True
    #     error_messages = []

    #     # Проверка цены
    #     if not self.priceEdit.hasAcceptableInput():
    #         self.priceEdit.setStyleSheet("border: 1px solid red;")
    #         error_messages.append("Цена должна быть положительным числом.")
    #         valid = False
    #     else:
    #         self.priceEdit.setStyleSheet("")

    #     # Проверка минимальной и максимальной цены
    #     min_price = float(self.min_priceEdit.text())
    #     max_price = float(self.max_priceEdit.text())
    #     if min_price > max_price:
    #         self.min_priceEdit.setStyleSheet("border: 1px solid red;")
    #         self.max_priceEdit.setStyleSheet("border: 1px solid red;")
    #         error_messages.append("Минимальная цена не может быть больше максимальной.")
    #         valid = False
    #     else:
    #         self.min_priceEdit.setStyleSheet("")
    #         self.max_priceEdit.setStyleSheet("")

    #     # Проверка дат
    #     if self.start_dateEdit.date() > self.dateEdit.date():
    #         self.start_dateEdit.setStyleSheet("border: 1px solid red;")
    #         self.dateEdit.setStyleSheet("border: 1px solid red;")
    #         error_messages.append("Дата начала не может быть позже даты исполнения.")
    #         valid = False
    #     else:
    #         self.start_dateEdit.setStyleSheet("")
    #         self.dateEdit.setStyleSheet("")

    #     # Отображение ошибок
    #     if not valid:
    #         error_label = QLabel("\n".join(error_messages))
    #         self.formLayout.addRow(error_label)

    #     return valid

    def validate_form(self,table_name):
        self.formLayout.removeRow(9)
        valid = True
        if table_name != 'stat':
            return valid
        error_messages = []
        min_price = -1
        max_price = -1

        # Проверка на пустые поля
        if not self.priceEdit.text().strip():
            self.priceEdit.setStyleSheet("border: 1px solid red;")
            error_messages.append("Поле 'Цена' не может быть пустым.")
            valid = False

        else:
            self.priceEdit.setStyleSheet("")

        if not self.min_priceEdit.text().strip():
            self.min_priceEdit.setStyleSheet("border: 1px solid red;")
            error_messages.append("Поле 'Минимальная цена' не может быть пустым.")
            valid = False
        else:
            self.min_priceEdit.setStyleSheet("")
            min_price = float(self.min_priceEdit.text())
            

        if not self.max_priceEdit.text().strip():
            self.max_priceEdit.setStyleSheet("border: 1px solid red;")
            error_messages.append("Поле 'Максимальная цена' не может быть пустым.")
            valid = False
        else:
            self.max_priceEdit.setStyleSheet("")
            max_price = float(self.max_priceEdit.text())

        if not self.quantEdit.text().strip():
            self.quantEdit.setStyleSheet("border: 1px solid red;")
            error_messages.append("Поле 'Объем торгов' не может быть пустым.")
            valid = False
        else:
            self.quantEdit.setStyleSheet("")

        
        

        # Проверка минимальной и максимальной цены
        # min_price = float(self.min_priceEdit.text())
        # max_price = float(self.max_priceEdit.text())
        if min_price != -1 and max_price != -1:
            if min_price > max_price:
                self.min_priceEdit.setStyleSheet("border: 1px solid red;")
                self.max_priceEdit.setStyleSheet("border: 1px solid red;")
                error_messages.append("Минимальная цена не может быть больше максимальной.")
                valid = False
            else:
                self.min_priceEdit.setStyleSheet("")
                self.max_priceEdit.setStyleSheet("")

        # Проверка дат
        print(self.start_dateEdit.date(),"----",self.dateEdit.date())
        if self.start_dateEdit.date() > self.dateEdit.date():
            self.start_dateEdit.setStyleSheet("border: 1px solid red;")
            self.dateEdit.setStyleSheet("border: 1px solid red;")
            error_messages.append("Дата начала не может быть позже даты исполнения.")
            valid = False
        else:
            self.start_dateEdit.setStyleSheet("")
            self.dateEdit.setStyleSheet("")

        # Отображение ошибок
        if not valid:
            error_label = QLabel("\n".join(error_messages))
            self.formLayout.addRow(error_label)

        return valid

    def confirmAndDeleteSelectedRows(self): # ----------------
        db_name = 'Subd2.db' # ----------------
        table_name = self.table_name
        self.toggleButtons(False)
        # selectionModel = self.tableView.selectionModel()
        # selectedRows = selectionModel.selectedRows()
        selectedRows = self.tableView.selectionModel().selectedRows()
        
        ids = [self.model.item(index.row(), 0).text() for index in selectedRows]
        # print(selectedRows[0].model)

        # if not selectedRows:
        #     return

        rowIndices = sorted(index.row() for index in selectedRows)
        print(rowIndices)
        # ids = [self.model.data(index.siblingAtColumn(0)) for index in selectedRows]
        ranges = self.formatRanges(rowIndices)

        reply = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить следующие строки: {ranges}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            for index in ids:
                cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (index,))
                # self.model.removeRow(index)

            for i in reversed(rowIndices):
                self.model.removeRow(i)
            conn.commit()
            conn.close()
        self.toggleButtons(True)   
           

    # Форматирование диапазонов
    def formatRanges(self, indices):
        if not indices:
            return ""

        ranges = []
        start = indices[0]
        end = indices[0]

        for i in range(1, len(indices)):
            if indices[i] == end + 1:
                end = indices[i]
            else:
                if start == end:
                    ranges.append(f"{start+1}")
                else:
                    ranges.append(f"{start+1}-{end+1}")
                start = end = indices[i]

        # Добавляем последний диапазон
        if start == end:
            ranges.append(f"{start+1}")
        else:
            ranges.append(f"{start+1}-{end+1}")
        return ", ".join(ranges)    

    def get_table(self, table_name, db_name):
        conn = sqlite3.connect(db_name)
        data = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        return data
    
    def get_column_names(self, table_name, db_name):
        if table_name == 'stat':
            return ["Идентификатор","Название","Начало торгов","Конец торгов","Цена","Минимальная цена","Максимальная цена","Объем торгов"]
        if table_name == 'contractss':
            return ["Идентификатор","Название","Код","Дата исполнения"]
        if table_name == 'summary':
            return ["Идентификатор","Название","Начало торгов","Конец торгов","Дата исполнения","Код","Цена","Минимальная цена","Максимальная цена","Объем торгов"]
        # Подключаемся к базе данных
        # conn = sqlite3.connect(db_name)

        # Выполняем SQL-запрос для получения названий столбцов
        # query = f"PRAGMA table_info({table_name})"
        # columns_info = pd.read_sql_query(query, conn)

        # # Извлекаем названия столбцов
        # column_names = columns_info['name'].tolist()

        # conn.close()
        # return column_names
    
    # def to_update_or_create_union_table(self, db_name):
    #     # Объединяем данные
    #     merged_data = pd.merge(self.kontrakti_data, self.statistics_data, on='name', how='outer')

    #     # Переименовываем столбцы для новой таблицы
    #     merged_data.columns = ['name'] + [f'{col}' for col in self.get_column_names('stat', db_name) if col != 'name'] + \
    #                           [f'{col}' for col in self.get_column_names('contractss', db_name) if col != 'name']

    #     # Сохраняем объединенные данные в новую таблицу
    #     conn = sqlite3.connect(db_name)
    #     cursor = conn.cursor()
    #     cursor.execute("DROP TABLE IF EXISTS Union_table")
    #     conn.commit()
    #     merged_data.to_sql('Union_table', conn, if_exists='replace',
    #                        index=False)  # Если таблица существует, заменяем её
    #     conn.close()
    #     # Загружаем данные из новой таблицы в QTableWidget
    #     self.load_table_from_db('Union_table', db_name)


    # def create_summary_table():
    #     
    #     """Создает сводную таблицу, если она еще не существует."""
    #     create_table_sql = """
    #     CREATE TABLE IF NOT EXISTS summary (
    #         id INTEGER PRIMARY KEY,
    #         contractss_id INTEGER,
    #         stat_id INTEGER,
    #         name TEXT,
    #         other_contractss_columns TEXT,
    #         other_stat_columns TEXT
    #     );
    #     """
    #     conn.execute(create_table_sql)
    #     conn.commit()

    def update_summary_table(self,db_name):
        conn = sqlite3.connect(db_name)
        """Обновляет сводную таблицу."""
        # Удаляем все записи из сводной таблицы
        conn.execute("DELETE FROM summary")
        
        # Вставляем обновленные данные
        insert_sql = """
        INSERT INTO summary (name,start_date,day_end,price,min_price,max_price,contracts_quantity,exec_date,base)
        SELECT s.name, s.start_date,s.day_end,s.price,s.min_price,s.max_price,s.contracts_quantity,c.exec_date,c.base
        FROM contractss c
        JOIN stat s ON c.name = s.name;
        """
        conn.execute(insert_sql)
        conn.commit()
        conn.close()
        self.load_table_from_db('summary',db_name )




    def load_table_from_db(self, table_name, db_name):
        if table_name == 'summary':
            self.toggleButtons(False)
        else :
            self.toggleButtons(True)
        self.table_name = table_name
        # Используем Pandas для загрузки данных
        conn = sqlite3.connect(db_name)
        data = pd.read_sql_query((f"SELECT * FROM {table_name}"), conn)
        flag = table_name
        conn.close()
        self.data_to_table(data)
        self.model.setHorizontalHeaderLabels(self.get_column_names(table_name,db_name))

    def data_to_table(self, data):
        self.model.clear()  # Очищаем предыдущие данные

        if not data.empty:
            # Устанавливаем заголовки столбцов
            
            li = ['Название','Название','Название',]

            # Заполняем модель данными
            for row_index, row_data in data.iterrows():
                items = [QStandardItem(str(item)) for item in row_data]
                self.model.insertRow(0,items)

            # for row_index, row_data in data.iterrows():
            #     items = [QStandardItem(str(item)) for item in row_data]
            #     self.model.appendRow(items)

            self.tableView.setModel(self.model)
            self.tableView.hideColumn(0) # Раскоментировать при production

    def toggleButtons(self, show):
        self.EditButton.setVisible(show)
        self.AddButton.setVisible(show)
        self.DeleteButton.setVisible(show)        

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()  # Используем ваш класс MainWindow
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()



    '''def data_to_table(self, data):
        # Очистка текущих данных в таблице
        self.table_widget.clear()

        # Проверка, что данные не пустые
        if data.empty:
            print("Данные пустые.")
            return

        # Заполнение таблицы данными
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(data.columns))
        self.table_widget.setHorizontalHeaderLabels(data.columns.tolist())

        for row_idx, row in data.iterrows():
            for col_idx, value in enumerate(row):
                self.table_widget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(value)))'''

'''def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())'''