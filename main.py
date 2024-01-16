import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt5 import uic  # Импортируем uic


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.con = sqlite3.connect("coffee.sqlite")
        self.btn.clicked.connect(self.result)

    def result(self):
        cur = self.con.cursor()
        result = cur.execute("""SELECT Coffee.ID, 
                                       Coffee.title, 
                                       roast.title,
                                       Coffee.grind,
                                       Coffee.taste,
                                       Coffee.price, 
                                       Coffee.volume FROM Coffee
                                       LEFT JOIN roast ON Coffee.roasting = roast.ID""").fetchall()
        try:
            titles = ["ID", "название сорта", "степень обжарки", "молотый/в зернах", "описание вкуса", "цена",
                           "объем упаковки"]
            self.tableWidget.setColumnCount(len(result[0]))
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setHorizontalHeaderLabels(titles)
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.statusBar().showMessage("")
        except Exception:
            self.statusBar().showMessage("По этому запросу ничего не найдено")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())