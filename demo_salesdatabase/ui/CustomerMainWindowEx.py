from PyQt6.QtWidgets import QTableWidgetItem, QMainWindow

from demo_salesdatabase.connectors.connector import Connector
from demo_salesdatabase.ui.ChartVisualizationEx import ChartVisualizationEx
from demo_salesdatabase.ui.CustomerMainWindow import Ui_MainWindow


class CustomerMainWindowEx(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow=MainWindow
        self.setupSignalAndSlot()
    def showWindow(self):
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        self.pushButtonCustomer.clicked.connect(self.showListCustomer)
        self.pushButtonStatistic.clicked.connect(self.showChartVisualizationUI)
    def showListCustomer(self):
        conn = Connector()
        conn.connect()
        sql2 = "select * from customer"
        df2 = conn.queryDataset(sql2)
        self.showDataIntoTableWidget(self.tableWidgetData,df2)
    def showDataIntoTableWidget(self,table,df):
        table.setRowCount(0)
        table.setColumnCount(len(df.columns))
        for i in range(len(df.columns)):
            column_header=df.columns[i]
            table.setHorizontalHeaderItem(i, QTableWidgetItem(column_header))
        row=0
        for item in df.iloc:
            arr=item.values.tolist()
            table.insertRow(row)
            j=0
            for data in arr:
                table.setItem(row,j,QTableWidgetItem(str(data)))
                j=j+1
            row=row+1
    def showChartVisualizationUI(self):
        self.myui = ChartVisualizationEx()
        self.myui.setupUi(QMainWindow())
        self.myui.showWindow()
