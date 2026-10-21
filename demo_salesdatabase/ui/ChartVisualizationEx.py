from demo_salesdatabase.connectors.connector import Connector
from demo_salesdatabase.ui.ChartVisualization import Ui_MainWindow
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import seaborn as sns

class ChartVisualizationEx(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow=MainWindow
        self.setupSignalAndSlot()
        self.setupPlot()
    def showWindow(self):
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        self.pushButtonCustomer.clicked.connect(self.showPieChartForCustomer)

    def setupPlot(self):
        self.figure=plt.figure()
        self.canvas=FigureCanvas(self.figure)
        self.toolbar=NavigationToolbar(self.canvas,self.MainWindow)
        self.verticalLayoutPlot.addWidget(self.toolbar)
        self.verticalLayoutPlot.addWidget(self.canvas)
    def showPieChartForCustomer(self):
        conn = Connector()
        conn.connect()
        sql="select * from customer"
        df=conn.queryDataset(sql)
        dfGender = (
            df["Gender"]
            .value_counts()
            .rename_axis("Gender")
            .reset_index(name="Count")
        )
        print(dfGender)
        columnlabel="Gender"
        columnStatistic="Count"
        title="Gender Distribution"

        print(dfGender[columnStatistic])
        print(dfGender[columnlabel])

        legend=True
        self.figure.clear()
        ax=self.figure.add_subplot(111)

        ax.pie(dfGender[columnStatistic],
               labels=dfGender[columnlabel],
               autopct='%1.2f%%')
        if legend:
            ax.legend(dfGender[columnlabel],loc='lower right')
        ax.set_title(title)
        self.canvas.draw()








