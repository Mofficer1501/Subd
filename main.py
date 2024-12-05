import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий
import sqlite3
import pandas as pd
import numpy as np
from math import log
from scipy.stats import kstest
from datetime import datetime

# import locale

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QDate,QLocale
from PyQt6.QtWidgets import QTableWidgetItem,QLabel
from PyQt6.QtGui import QStandardItemModel, QStandardItem,QIntValidator, QDoubleValidator

import MainForm  # Это наш конвертированный файл дизайна
# locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

# day_end это дата погашения
# exec_date - дата исполнения

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
        self.Analyze.triggered.connect(lambda: self.update_analyze_table(db_name))
        # self.Analyze.triggered.connect(lambda: self.get_max_x_gipotize(db_name))
        self.Gipot.triggered.connect(self.open_gipot_popup)
        self.Mean.triggered.connect(self.open_mean_popup)
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
        self.tableView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        # self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        

        # Выделение всей строки при наведении 
        # self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setColumnWidth(0, 250)
        self.tableView.setFocus()
        self.layout.addWidget(self.tableView)
        self.tableView.setSortingEnabled(True)

        # Кнопки
        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.EditButton)
        self.button_layout.addWidget(self.AddButton)
        self.button_layout.addWidget(self.FilterButton)
        self.button_layout.addWidget(self.DeleteButton)
        self.DeleteButton.clicked.connect(self.confirmAndDeleteSelectedRows)
        self.EditButton.clicked.connect(self.editRecord)
        self.AddButton.clicked.connect(self.addRecord)
        self.FilterButton.clicked.connect(self.filterRecord)
        self.layout.addLayout(self.button_layout)
        # self.layout.addWidget(self.formWidget)
        # self.layout.addWidget(self.formTypeLabel)
        '''-----------------------------------------------------------------------------------------'''
    
    def filterRecord(self):
        self.open_filter_popup()

    def open_filter_popup(self):
        self.toggleButtons(False)
        self.formLayout = QtWidgets.QFormLayout()
        # self.nameFilter = QtWidgets.QLineEdit()
        # self.nameFilter.setPlaceholderText("Название")
        # self.formWidget = QtWidgets.QDialog()
        # self.formWidget.setWindowTitle(self.get_window_title("filter"))
        # buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        # ok_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        # cancel_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        # ok_button.setText("Фильтровать")
        # cancel_button.setText("Отмена")
        # self.formLayout.addRow(buttonBox)

        self.name_filter = QtWidgets.QLineEdit()
        self.name_filter.setPlaceholderText("2222-2222")

        self.start_date_filter = QtWidgets.QDateEdit()
        self.start_date_filter.setCalendarPopup(True)
        self.start_date_filter.setDate(QDate.currentDate())

        self.end_date_filter = QtWidgets.QDateEdit()
        self.end_date_filter.setCalendarPopup(True)
        self.end_date_filter.setDate(QDate.currentDate())

        self.code_filter = QtWidgets.QLineEdit()
        self.code_filter.setPlaceholderText("ABCD1234")

        self.min_price_filter = QtWidgets.QLineEdit()
        self.min_price_filter.setPlaceholderText("1")

        self.max_price_filter = QtWidgets.QLineEdit()
        self.max_price_filter.setPlaceholderText("100")

        self.min_volume_filter = QtWidgets.QLineEdit()
        self.min_volume_filter.setPlaceholderText("0")

        self.max_volume_filter = QtWidgets.QLineEdit()
        self.max_volume_filter.setPlaceholderText("100000")

        # Добавляем виджеты в layout
        self.formLayout.addRow("Название:", self.name_filter)
        self.formLayout.addRow("Начало торгов:", self.start_date_filter)
        self.formLayout.addRow("Конец торгов:", self.end_date_filter)
        self.formLayout.addRow("Код:", self.code_filter)
        self.formLayout.addRow("Минимальная цена:", self.min_price_filter)
        self.formLayout.addRow("Максимальная цена:", self.max_price_filter)
        self.formLayout.addRow("Объем торгов от:", self.min_volume_filter)
        self.formLayout.addRow("Объем торгов до:", self.max_volume_filter)

        self.min_price_filter.setValidator(QDoubleValidator(0.0, 100, 2))
        self.max_price_filter.setValidator(QDoubleValidator(0.0, 100, 2))
        self.min_volume_filter.setValidator(QIntValidator(0, 999999))
        self.max_volume_filter.setValidator(QIntValidator(0, 999999))

        self.formWidget = QtWidgets.QDialog()
        self.formWidget.setWindowTitle(self.get_window_title("filter"))
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        cancel_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_button.setText("Фильтровать")
        cancel_button.setText("Отмена")
        self.formLayout.addRow(buttonBox)
        buttonBox.accepted.connect(self.on_filter_button_clicked)
        # buttonBox.rejected.connect(self.formWidget.reject)
        buttonBox.rejected.connect(self.reject_summary)
        self.formWidget.setLayout(self.formLayout)
        self.formWidget.open()


    def open_gipot_popup(self):
        print('gipot')
        self.toggleButtons(False)
        self.formLayout = QtWidgets.QFormLayout()
        self.gipot_date = QtWidgets.QDateEdit()
        self.gipot_date.setCalendarPopup(True)
        # self.end_date_filter.setDate(QDate.currentDate())

        # Добавляем виджеты в layout
        self.formLayout.addRow("Дата:", self.gipot_date)

        self.formWidget = QtWidgets.QDialog()
        self.formWidget.setWindowTitle(self.get_window_title("gipot"))
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        cancel_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_button.setText("Проверить")
        cancel_button.setText("Отмена")
        self.formLayout.addRow(buttonBox)
        buttonBox.accepted.connect(self.get_max_x_gipotize)
        # buttonBox.rejected.connect(self.formWidget.reject)
        buttonBox.rejected.connect(self.reject_and_show_btns)
        self.formWidget.setLayout(self.formLayout)
        self.formWidget.open()  

    def open_mean_popup(self):
        print('mean')
        self.toggleButtons(False)
        self.formLayout = QtWidgets.QFormLayout()
        self.mean_date = QtWidgets.QDateEdit()
        self.mean_date.setCalendarPopup(True)
        # self.end_date_filter.setDate(QDate.currentDate())

        # Добавляем виджеты в layout
        self.formLayout.addRow("Дата:", self.mean_date)

        self.formWidget = QtWidgets.QDialog()
        self.formWidget.setWindowTitle(self.get_window_title("stat"))
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        cancel_button = buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        ok_button.setText("Рассчитать")
        cancel_button.setText("Отмена")
        self.formLayout.addRow(buttonBox)
        buttonBox.accepted.connect(self.update_mean_table)
        # buttonBox.rejected.connect(self.formWidget.reject)
        buttonBox.rejected.connect(self.reject_and_show_btns)
        self.formWidget.setLayout(self.formLayout)
        self.formWidget.open()    

    def get_filters(self):
        # return {
        #     "name": self.name_filter.text()
        # }
    
        return {
            "name": self.name_filter.text(),
            "start_date": self.start_date_filter.date().toString("yy-MMM-dd") ,
            "end_date": self.end_date_filter.date().toString("yy-MMM-dd"),
            "code": self.code_filter.text(),
            "min_price": self.min_price_filter.text() if self.min_price_filter.text() else 1,
            "max_price": self.max_price_filter.text() if self.max_price_filter.text() else 100,
            "min_volume": self.min_volume_filter.text() if self.min_volume_filter.text() else 0,
            "max_volume": self.max_volume_filter.text() if self.max_volume_filter.text() else 100000000000,
        }
    

    def get_t_date(self):
        return self.gipot_date.date()
    
    def get_t_mean_date(self):
        return self.mean_date.date()

    def on_filter_button_clicked(self):
        filters = self.get_filters()
        self.apply_filters(filters)

    def apply_filters(self, filters):
        data = self.get_data_from_db('summary','Subd2.db')
        print(data)
    # Пример фильтрации данных
        # filtered_data = data[
        #     (data['name'].str.contains(filters['name'], case=False))
        # ]
        filtered_data = data[
            (data['name'].str.contains(filters['name'], case=False)) &
            # (data['exec_date'] >= filters['start_date']) &
            # (data['exec_date'] <= filters['end_date']) &
            (data['base'].str.contains(filters['code'], case=False)) &
            (data['price'] >= float(filters['min_price'])) &
            (data['price'] <= float(filters['max_price'])) &
            (data['contracts_quantity'] >= int(filters['min_volume'])) &
            (data['contracts_quantity'] <= int(filters['max_volume'])) 
        ]
        self.data_to_table(filtered_data)    


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

    def reject_summary(self):
        self.update_summary_table('Subd2.db')
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
        elif title == "edit":
            return "Редактирование"
        elif title == "filter":
            return "Фильтрация"
        elif title == "gipot":
            return "Проверка гипотезы"
        elif title == "stat":
            return "Статистика показателей"
    
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
            return ["Идентификатор","Название","День торгов","Дата погашения","Цена","Минимальная цена","Максимальная цена","Объем торгов"]
        if table_name == 'contractss':
            return ["Идентификатор","Название","Код","Дата исполнения"]
        if table_name == 'summary':
            return ["Идентификатор","Название","Дата торгов","Дата погашения","Дата исполнения","Код","Цена","Минимальная цена","Максимальная цена","Объем торгов"]
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

    # def replace_buttons_for_filter(self,flag):
    #     if flag:
    #         self.button_layout.addWidget(self.FilterButton)
    #         self.button_layout.removeWidget(self.EditButton)
    #         self.button_layout.removeWidget(self.AddButton)
    #         self.button_layout.removeWidget(self.DeleteButton)
    #     else:
    #         self.button_layout.removeWidget(self.FilterButton)
    #         self.button_layout.addWidget(self.EditButton)
    #         self.button_layout.addWidget(self.AddButton)
    #         self.button_layout.addWidget(self.DeleteButton)

    def update_summary_table(self,db_name):
        # self.replace_buttons_for_filter(True)
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

    def only_update_summary_table(self,db_name):
        # self.replace_buttons_for_filter(True)
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




    def load_table_from_db(self, table_name, db_name):
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        # if table_name == 'summary':
        #     self.toggleButtons(False)
        # else :
        #     self.toggleButtons(True)
        self.table_name = table_name
        # Используем Pandas для загрузки данных
        conn = sqlite3.connect(db_name)
        data = pd.read_sql_query((f"SELECT * FROM {table_name}"), conn)
        if table_name == "contractss" or table_name == "summary":
            data['exec_date']=data['exec_date'].apply(self.convert_date)
            data['exec_date']=pd.to_datetime(data['exec_date'], format='%d-%b-%y')
            data['exec_date'] = data['exec_date'].dt.date

        if table_name == "stat" or table_name == "summary":
            data['start_date']=data['start_date'].apply(self.convert_date)
            data['day_end']=data['day_end'].apply(self.convert_date)
            data['start_date']=pd.to_datetime(data['start_date'], format='%d-%b-%y')
            data['day_end']=pd.to_datetime(data['day_end'], format='%d-%b-%y')
            data['start_date'] = data['start_date'].dt.date
            data['day_end'] = data['day_end'].dt.date
        # data['start_date'] = pd.to_datetime(data['start_date'], format='%d-%b-%y')
        flag = table_name
        conn.close()
        self.data_to_table(data)
        self.model.setHorizontalHeaderLabels(self.get_column_names(table_name,db_name))

    def get_data_from_db(self, table_name, db_name):
        # if table_name == 'summary':
        #     self.toggleButtons(False)
        # else :
        #     self.toggleButtons(True)
        self.table_name = table_name
        # Используем Pandas для загрузки данных
        conn = sqlite3.connect(db_name)
        data = pd.read_sql_query((f"SELECT * FROM {table_name}"), conn)
        # data['start_date']=data['start_date'].apply(self.convert_date)
        self.model.setHorizontalHeaderLabels(self.get_column_names(table_name,db_name))
        conn.close()
        return data
        

    def data_to_table(self, data):

        self.model.clear()  # Очищаем предыдущие данные

        if not data.empty:
            # Устанавливаем заголовки столбцов

            # Заполняем модель данными
            for row_index, row_data in data.iterrows():
                items = [QStandardItem(str(item)) for item in row_data]
                self.model.insertRow(0,items)

            # for row_index, row_data in data.iterrows():
            #     items = [QStandardItem(str(item)) for item in row_data]
            #     self.model.appendRow(items)

            self.tableView.setModel(self.model)
            self.tableView.hideColumn(0) # Раскоментировать при production

    def analyze_data_to_table(self, data):
        self.model.clear()  # Очищаем предыдущие данные
        if not data.empty:
        # Пивотируем данные
            pivot_data = data.pivot(index='start_date', columns='name', values='xk').fillna('')

            # Устанавливаем заголовки столбцов
            self.model.setHorizontalHeaderLabels([''] + list(pivot_data.columns))

            # Заполняем модель данными
            for row_index, (index, row_data) in enumerate(pivot_data.iterrows()):
                items = [QStandardItem(str(index))] + [QStandardItem(str(item)) for item in row_data]
                self.model.insertRow(row_index, items)
        # if not data.empty:
        #     # Устанавливаем заголовки столбцов
        #     self.model.setHorizontalHeaderLabels(data["name"])
            # for row_index, row_data in data.iterrows():
            #     items = []
            #     for item in row_data:
            #         # Проверяем, является ли значение NaN
            #         if pd.isna(item):
            #             items.append(QStandardItem(""))  # Пустая строка для NaN
            #         else:
            #             items.append(QStandardItem(str(item)))
            #     self.model.appendRow(items)
        # column_width = 200  # Задаем желаемую ширину
        # for column in range(self.model.columnCount()):
        #     self.tableView.setColumnWidth(column, column_width)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.tableView.setColumnWidth(0, 250)

    def mean_data_to_table(self, data):
        self.model.clear()  # Очищаем предыдущие данные
        if not data.empty:
        # Пивотируем данные
            pivot_data = data.pivot(index='start_date', columns='name', values='xk').fillna('')

            # Устанавливаем заголовки столбцов
            self.model.setHorizontalHeaderLabels([''] + list(pivot_data.columns))

            # Заполняем модель данными
            for row_index, (index, row_data) in enumerate(pivot_data.iterrows()):
                items = [QStandardItem(str(index))] + [QStandardItem(str(item)) for item in row_data]
                self.model.insertRow(row_index, items)
        # if not data.empty:
        #     # Устанавливаем заголовки столбцов
        #     self.model.setHorizontalHeaderLabels(data["name"])
            # for row_index, row_data in data.iterrows():
            #     items = []
            #     for item in row_data:
            #         # Проверяем, является ли значение NaN
            #         if pd.isna(item):
            #             items.append(QStandardItem(""))  # Пустая строка для NaN
            #         else:
            #             items.append(QStandardItem(str(item)))
            #     self.model.appendRow(items)
        # column_width = 200  # Задаем желаемую ширину
        # for column in range(self.model.columnCount()):
        #     self.tableView.setColumnWidth(column, column_width)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        self.tableView.setColumnWidth(0, 250)



    def toggleButtons(self, show):
        self.FilterButton.setVisible(show)
        self.EditButton.setVisible(show)
        self.AddButton.setVisible(show)
        self.DeleteButton.setVisible(show)       

    def convert_date(self, date_str):
    # замена русских названий месяцев на английские
        months = {
            'янв': 'Jan', 'фев': 'Feb', 'мар': 'Mar', 'апр': 'Apr',
            'май': 'May', 'июн': 'Jun', 'июл': 'Jul', 'авг': 'Aug',
            'сен': 'Sep', 'окт': 'Oct', 'ноя': 'Nov', 'дек': 'Dec'
        }
        day, month_rus, year = date_str.split('-')
        month_rus = month_rus.lower()
        month_eng = months[month_rus]
        new_date_str = f"{day}-{month_eng}-{year}"
        return new_date_str 
      
    def convert_date_for_analyze(self, date_str):
    # замена русских названий месяцев на английские
        months = {
            'янв': 'Jan', 'фев': 'Feb', 'мар': 'Mar', 'апр': 'Apr',
            'май': 'May', 'июн': 'Jun', 'июл': 'Jul', 'авг': 'Aug',
            'сен': 'Sep', 'окт': 'Oct', 'ноя': 'Nov', 'дек': 'Dec'
        }
        day, month_rus, year = date_str.split('-')
        month_rus = month_rus.lower()
        month_eng = months[month_rus]
        new_date_str = f"{day}-{month_eng}-{year}"
        return datetime.strptime(new_date_str, "%d-%b-%y")
    
    def convert_to_pd_date(self, qdate):
        year = qdate.year()
        month = qdate.month()
        day = qdate.day()
        
        # Создаем объект datetime
        date_obj = datetime(year, month, day)
        
        # Форматируем дату в строку
        return date_obj.strftime("%d-%b-%y")
    
    def calculate_stats(self,lst):
    # Убираем None из списка
        filtered_lst = [x for x in lst if x is not None]
        
        if not filtered_lst:
            return None, None, None, None
        
        # Вычисляем минимальное и максимальное значения
        min_val = round(min(filtered_lst),2)
        max_val = round(max(filtered_lst),2)
        
        # Вычисляем среднее значение
        mean_val = round((sum(filtered_lst) / len(filtered_lst)),2)
        
        # Вычисляем дисперсию
        variance = sum((x - mean_val) ** 2 for x in filtered_lst) / len(filtered_lst)
        
        return [min_val, max_val, mean_val, round(variance,2)]
    
    def update_mean_table(self):
        db_name = 'Subd2.db'
            # date_up = "01-Сен-96"
        date_up = self.get_t_mean_date()
        print(date_up)
            # date_x = self.convert_date_for_analyze(date_up)
        date_x = self.convert_to_pd_date(date_up)

        self.only_update_summary_table(db_name)

        conn = sqlite3.connect(db_name)
            
            # Загружаем данные из таблицы
        query = "SELECT name, start_date, day_end, exec_date, price FROM summary"
        df = pd.read_sql_query(query, conn)
            
        conn.close()

        df['start_date'] = df['start_date'].apply(self.convert_date_for_analyze)
        df_up = df[df['start_date'] < date_x]
        df_up['day_end'] = df['day_end'].apply(self.convert_date_for_analyze)
        df_up['exec_date'] = df['exec_date'].apply(self.convert_date_for_analyze)
            
            # Группируем данные по названию фьючерса
        grouped = df_up.groupby('name')
        
        # Создаем список для хранения результатов
        results = []

        for name, group in grouped:
            # Сортируем по дате торгов
            group = group.sort_values('start_date')
            # Рассчитываем rk(i) и xk(i)
            rks = []
            xks = []
            
            for i in range(len(group)):
                Tnk = group.iloc[i]['day_end']
                Tik = group.iloc[i]['exec_date']
                Tr = (Tik - Tnk).days
                Fk = group.iloc[i]['price']
                rk = log(Fk / 100) / Tr
                rks.append(rk)
                if i < 1:
                    xks.append(None)
                else:
                    xk = round(log(rk / rks[i-2]), 2)
                    xks.append(xk)
            
            # Добавляем результаты в список
            results.append(
                pd.DataFrame({
                'name': name, 
                'start_date': ['минимум','максимум','сренднее','дисперсия'],
                'xk': self.calculate_stats(xks)
            }))
        
        # Объединяем результаты в один DataFrame
        result_df = pd.concat(results)
        self.formWidget.reject()
        self.toggleButtons(True)
        print(result_df)
        self.mean_data_to_table(result_df)

    def update_analyze_table(self, db_name):
    # Подключаемся к базе данных
        self.only_update_summary_table(db_name)

        conn = sqlite3.connect(db_name)
        
        # Загружаем данные из таблицы
        query = "SELECT name, start_date, day_end, exec_date, price FROM summary"
        df = pd.read_sql_query(query, conn)
        
        # Закрываем соединение с базой данных
        conn.close()
        
        # Преобразуем даты в формат datetime
        # df['start_date'] = pd.to_datetime(df['start_date'])
        # df['day_end'] = pd.to_datetime(df['day_end'])
        # df['exec_date'] = pd.to_datetime(df['exec_date'])

        df['start_date'] = df['start_date'].apply(self.convert_date_for_analyze)
        df['day_end'] = df['day_end'].apply(self.convert_date_for_analyze)
        df['exec_date'] = df['exec_date'].apply(self.convert_date_for_analyze)
        
        # Группируем данные по названию фьючерса
        grouped = df.groupby('name')
        max_length = max(len(group) for name,group in grouped)
        
        
        # Создаем список для хранения результатов
        results = []

        for name, group in grouped:
            # Сортируем по дате торгов
            group = group.sort_values('start_date')
            # Рассчитываем rk(i) и xk(i)
            rks = []
            xks = []
            
            for i in range(len(group)):
                Tnk = group.iloc[i]['day_end']
                Tik = group.iloc[i]['exec_date']
                Tr = (Tik - Tnk).days
                Fk = group.iloc[i]['price']
                rk = log(Fk / 100) / Tr
                rks.append(rk)
                if i < 1:
                    xks.append(None)
                else:
                    xk = round(log(rk / rks[i-2]), 2)
                    xks.append(xk)
            
            # Добавляем результаты в список
            results.append(
                pd.DataFrame({
                'name': name,
                'start_date': group['start_date'],
                'xk': xks
            }))
        
        # Объединяем результаты в один DataFrame
        result_df = pd.concat(results)
        print(result_df)
        self.analyze_data_to_table(result_df)
        # Выводим таблицу

    def get_max_x_gipotize(self):
    # Подключаемся к базе данных
            db_name = 'Subd2.db'
            # date_up = "01-Сен-96"
            date_up = self.get_t_date()
            print(date_up)
            # date_x = self.convert_date_for_analyze(date_up)
            date_x = self.convert_to_pd_date(date_up)

            self.only_update_summary_table(db_name)

            conn = sqlite3.connect(db_name)
            
            # Загружаем данные из таблицы
            query = "SELECT name, start_date, day_end, exec_date, price FROM summary"
            df = pd.read_sql_query(query, conn)
            
            conn.close()

            df['start_date'] = df['start_date'].apply(self.convert_date_for_analyze)
            df_up = df[df['start_date'] < date_x]
            df_up['day_end'] = df['day_end'].apply(self.convert_date_for_analyze)
            df_up['exec_date'] = df['exec_date'].apply(self.convert_date_for_analyze)
            
            # Группируем данные по названию фьючерса
            grouped = df_up.groupby('name')
            max_length = max(len(group) for name,group in grouped)

            max_group = [group for name,group in grouped if len(group) == max_length]
            group = max_group[0].sort_values('start_date')
            rks = []
            xks = []
            for i in range(len(group)):
                Tnk = group.iloc[i]['day_end']
                Tik = group.iloc[i]['exec_date']
                Tr = (Tik - Tnk).days
                Fk = group.iloc[i]['price']
                rk = log(Fk / 100) / Tr
                rks.append(rk)
                print(i)
                if i < 2:
                    xks.append(None)
                else:
                    xk = round(log(rk / rks[i-2]), 2)
                    xks.append(xk)
            print("XKS=",xks)   
            xk_values = list(filter(lambda x: x is not None, xks))   
            mean = np.mean(xk_values)
            std = np.std(xk_values, ddof=1)

            # Применяем тест Колмогорова-Смирнова
            stat, p_value = kstest(xk_values, 'norm', args=(mean, std))
            self.formWidget.reject()
            print('Статистика теста Колмогорова-Смирнова:', stat)
            print('p-значение:', p_value)
            message = ""
            # Проверка гипотезы
            alpha = 0.05
            if p_value > alpha:
                message = 'Не удается отвергнуть нулевую гипотезу: данные распределены нормально'
            else:
                message = 'Нулевая гипотеза отвергнута: данные не распределены нормально'
            self.toggleButtons(True)
            QtWidgets.QMessageBox.information(self, "Результат проверки гипотезы", message)

                

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