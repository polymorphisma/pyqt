# import sys
# from PyQt5.QtWidgets import QApplication, QSizePolicy, QDateEdit, QWidget, QDoubleSpinBox, QMainWindow, QLabel, \
#     QPushButton, QHBoxLayout, QFileDialog, QComboBox, QVBoxLayout
# import pandas as pd
# import mplfinance as mpf
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import pandas as pd
# from matplotlib.ticker import MultipleLocator
from PyQt5.QtCore import QDate, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QDateEdit, QDoubleSpinBox, QFileDialog, QComboBox, QTabWidget, QWidget
from plotWindow import PlotWindow
import sys
import pandas as pd
import datetime
import MetaTrader5 as mt
# from PySide2 import QtWidgets


class CandlestickGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.selected_instrument = None
        self.setWindowTitle("Candlestick Chart")
        self.windowWidth = 800
        self.startRange = 20
        self.baseHeight = 30

        self.interval_mapping = {
            "1 minute": "TIMEFRAME_M1",
            "2 minutes": "TIMEFRAME_M2",
            "3 minutes": "TIMEFRAME_M3",
            "4 minutes": "TIMEFRAME_M4",
            "5 minutes": "TIMEFRAME_M5",
            "6 minutes": "TIMEFRAME_M6",
            "10 minutes": "TIMEFRAME_M10",
            "12 minutes": "TIMEFRAME_M12",
            "15 minutes": "TIMEFRAME_M15",  # Possible duplicate in your list
            "20 minutes": "TIMEFRAME_M20",
            "30 minutes": "TIMEFRAME_M30",
            "1 hour": "TIMEFRAME_H1",
            "2 hours": "TIMEFRAME_H2",
            "3 hours": "TIMEFRAME_H3",
            "4 hours": "TIMEFRAME_H4",
            "6 hours": "TIMEFRAME_H6",
            "8 hours": "TIMEFRAME_H8",
            "12 hours": "TIMEFRAME_H12",
            "1 day": "TIMEFRAME_D1",
            "1 week": "TIMEFRAME_W1",
            "1 month": "TIMEFRAME_MN1",
        }

        self.metatrader_mapping = {
            "TIMEFRAME_M1": mt.TIMEFRAME_M1,
            "TIMEFRAME_M2": mt.TIMEFRAME_M2,
            "TIMEFRAME_M3": mt.TIMEFRAME_M3,
            "TIMEFRAME_M4": mt.TIMEFRAME_M4,
            "TIMEFRAME_M5": mt.TIMEFRAME_M5,
            "TIMEFRAME_M6": mt.TIMEFRAME_M6,
            "TIMEFRAME_M10": mt.TIMEFRAME_M10,
            "TIMEFRAME_M12": mt.TIMEFRAME_M12,
            "TIMEFRAME_M20": mt.TIMEFRAME_M20,
            "TIMEFRAME_M30": mt.TIMEFRAME_M30,
            "TIMEFRAME_H1": mt.TIMEFRAME_H1,
            "TIMEFRAME_H2": mt.TIMEFRAME_H2,
            "TIMEFRAME_H3": mt.TIMEFRAME_H3,
            "TIMEFRAME_H4": mt.TIMEFRAME_H4,
            "TIMEFRAME_H6": mt.TIMEFRAME_H6,
            "TIMEFRAME_H8": mt.TIMEFRAME_H8,
            "TIMEFRAME_H12": mt.TIMEFRAME_H12,
            "TIMEFRAME_D1": mt.TIMEFRAME_D1,
            "TIMEFRAME_W1": mt.TIMEFRAME_W1,
            "TIMEFRAME_MN1": mt.TIMEFRAME_MN1,
        }


        self.selected_interval = "TIMEFRAME_M1"


        # MetaTrader5 variables
        self.metatrader_timeframe = mt.TIMEFRAME_M1

        # MetaTrader5 initialization
        mt.initialize()
        username = 10004945780
        password = "*5PyZjTb"
        server = "MetaQuotes-Demo"

        if not mt.login(username, password, server):
            print("MetaTrader5 login failed")
            return
        else:
            print("success")

        symbols = mt.symbols_get()
        symbol_list = [x.name for x in symbols]


        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.csv_tab = QWidget()
        self.tabs.addTab(self.csv_tab, "CSV upload")

        self.live_tab = QWidget()
        self.tabs.addTab(self.live_tab, "Live Data")

        self.setFixedSize(self.windowWidth, 300)
        # Create file selection button
        self.file_label = QLabel(self.csv_tab)
        self.file_label.setText("Select CSV file:")
        self.file_label.move(self.startRange, self.baseHeight)

        self.startRange += 85
        self.file_button = QPushButton(self.csv_tab)
        self.file_button.setText("Select File")
        self.file_button.move(self.startRange, self.baseHeight)
        self.file_button.clicked.connect(self.select_file)

        # Create date range selection fields
        self.startRange += 150
        self.start_date_label = QLabel(self.csv_tab)
        self.start_date_label.setText("Start Date (Y-M-D):")
        self.start_date_label.move(self.startRange, self.baseHeight)
        # self.start_date_entry = QLineEdit(self)
        self.startRange += 120

        self.date_edit = QDateEdit(QDate.currentDate(), self.csv_tab)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.move(self.startRange, self.baseHeight)

        self.startRange += 150
        self.end_date_label = QLabel(self.csv_tab)
        self.end_date_label.setText("End Date (YY-M-D):")
        self.end_date_label.move(self.startRange, self.baseHeight)

        self.startRange += 120
        self.end_date_entry = QDateEdit(QDate.currentDate(), self.csv_tab)
        self.end_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.end_date_entry.move(self.startRange, self.baseHeight)

        # Create candle width selection field
        self.baseHeight += 40
        self.startRange = 20

        self.candle_width_label = QLabel(self.csv_tab)
        self.candle_width_label.setText("Candle Width(x% of width):")

        self.candle_width_label.move(self.startRange, self.baseHeight)
        self.candle_width_label.setMinimumWidth(350)
        # self.candle_width_entry = QLineEdit(self)
        self.startRange += 180

        self.doubleSpinBox = QDoubleSpinBox(self.csv_tab)
        self.doubleSpinBox.setDecimals(2)
        self.doubleSpinBox.setRange(0, 100)
        self.doubleSpinBox.setSingleStep(0.01)
        self.doubleSpinBox.move(self.startRange, self.baseHeight)

        self.startRange = 20
        self.baseHeight = 30
        # Dropdown Selection for instrumnet
        # self.startRange += 120  # Reset range

        self.instrument_label = QLabel(self.live_tab)
        self.instrument_label.setText("Select Instrument:")
        self.instrument_label.move(self.startRange, self.baseHeight)

        self.startRange += 100

        self.instrument_dropdown = QComboBox(self.live_tab)
        self.instrument_dropdown.move(self.startRange, self.baseHeight)

        # Configurable list
        self.instruments = ["-"]  # Default list
        self.instruments.extend(symbol_list)
        self.instrument_dropdown.addItems(self.instruments)

        # set a default value
        self.instrument_dropdown.setCurrentIndex(0)
        # Connect signal to slot
        self.instrument_dropdown.currentIndexChanged.connect(self.on_instrument_selected)

        # Dropdown Selection for interval
        self.startRange += 120  # Reset range

        self.interval_label = QLabel(self.live_tab)
        self.interval_label.setText("Select Interval:")
        self.interval_label.move(self.startRange, self.baseHeight)

        self.startRange += 100

        self.interval_dropdown = QComboBox(self.live_tab)
        self.interval_dropdown.move(self.startRange, self.baseHeight)

        # Configurable list
        # self.intervals = ["-"]  # Default list
        # self.intervals.extend(list(self.interval_mapping.keys()))
        self.intervals = list(self.interval_mapping.keys())
        self.interval_dropdown.addItems(self.intervals)

        # set a default value
        self.interval_dropdown.setCurrentIndex(0)
        # Connect signal to slot
        self.interval_dropdown.currentIndexChanged.connect(self.on_interval_selected)

        self.startRange += 120
        self.start_date_label = QLabel(self.live_tab)
        self.start_date_label.setText("Start Date (Y-M-D):")
        self.start_date_label.move(self.startRange, self.baseHeight)

        self.startRange += 120

        self.date_edit = QDateEdit(QDate.currentDate(), self.live_tab)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.move(self.startRange, self.baseHeight)

        self.baseHeight += 60

        # Create plot button
        self.plot_button = QPushButton(self)
        self.plot_button.setText("Plot")
        self.plot_button.move(int(self.windowWidth / 2) - 50, self.baseHeight)
        self.plot_button.clicked.connect(self.plot_candles)

        self.baseHeight += 60

        self.errorLabel = QLabel(self)
        self.errorLabel.setStyleSheet("color: red;")

        self.errorLabel.setMinimumWidth(350)
        self.errorLabel.move(20, self.baseHeight)

        # self.showMaximized()
        self.plot_windows = []


        # Timer for updating the plot window every 60 seconds
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_plot_windows)
        # self.update_timer.start(1000)  # 60 seconds (60000 ms)
        self.timer_started = False

    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self.csv_tab, "Select CSV file")
        self.errorDisplay(' ')
        # self.file_button.setText(self.file_path)

    def on_instrument_selected(self):
        selected_instrument = self.instrument_dropdown.currentText()
        if selected_instrument != "-":
            self.selected_instrument = selected_instrument
        else:
            self.selected_instrument = None

    def on_interval_selected(self):
        selected_interval = self.interval_dropdown.currentText()
        
        if self.selected_instrument is not None and selected_interval != "-":  

            # Get the MetaTrader5 timeframe constant
            timeframe_constant = self.interval_mapping[selected_interval]
            # Check if the constant exists in the MetaTrader5 module
            if timeframe_constant in self.metatrader_mapping:
                self.metatrader_timeframe = self.metatrader_mapping[timeframe_constant]
            else:
                self.errorDisplay("Interval not valid.")

        print(self.metatrader_timeframe)

    def errorDisplay(self, error):
        self.errorLabel.setText(f'{self.file_path} {error}')

    def getDataFromFile(self):
        startDate = self.date_edit.date().toPyDate()
        endDate = self.end_date_entry.date().toPyDate()

        timestamp = pd.Timestamp(startDate)
        timestamp2 = pd.Timestamp(endDate)
        # Load data from CSV file
        if self.file_path is None:
            self.errorDisplay("Please Select a File path")
            return None

        df = pd.read_csv(self.file_path, names=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y.%m.%d %H:%M')
        df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d')

        df = df[df['Date'] >= timestamp]
        df = df[df['Date'] <= timestamp2]

        if df.shape[0] <= 0:
            self.errorDisplay("Empty!!!.No Data To Display")
            return None

    def fetch_live_data(self):
        """Fetch the latest data from MetaTrader5."""
        # date_from = datetime.now() - pd.Timedelta(minutes=60)
        # print(self.date_edit.date().toPyDate())
        date_from = self.date_edit.date().toPyDate()
        datetime_from = datetime.datetime.combine(date_from, datetime.datetime.min.time())
        date_to = datetime.datetime.now() + datetime.timedelta(days=1)

        # Retrieve price data from MetaTrader5
        # self.selected_instrument = "BTCUSD"
        price = mt.copy_rates_range(self.selected_instrument, self.metatrader_timeframe, datetime_from, date_to)
        if price is None or len(price) == 0:
            self.errorDisplay("No data retrieved from MetaTrader5")
            return

        # Update DataFrame
        df = pd.DataFrame(price)
        df['time'] = pd.to_datetime(df['time'], unit='s')

        # Renaming 'time' column to 'DateTime' to match plotWindow expectations
        df.rename(columns={
                        "time": "DateTime", "open": "Open", "high": "High",
                        "low": "Low", "close": "Close", "tick_volume": "Volume"
                    }, inplace=True)
        df = df[df['DateTime'] >= datetime_from]
        df.reset_index(drop=True, inplace=True)
        print(df)
        return df

    def getDataFrame(self):

        if self.file_path is not None:
            df = self.getDataFromFile()

        elif self.selected_instrument != '-' and self.file_path is None:
            df = self.fetch_live_data()

            # now start timer
            self.update_timer.start(60000)  # 60 seconds (60000 ms)
            self.timer_started = True


        return df

    def plot_candles(self, empty=False):
        self.errorDisplay(" ")
        df = self.getDataFrame()
        if df is None:
            return

        # Check if a plot window for the current instrument already exists
        plot_window = next((w for w in self.plot_windows if w.instrument == self.selected_instrument), None)

        if plot_window is None:
            # Create a new plot window if it doesn't exist
            persentageVal = float(self.doubleSpinBox.value())
            plot_window = PlotWindow(df=df, persentageVal=persentageVal)
            plot_window.instrument = self.selected_instrument
            self.plot_windows.append(plot_window)
            plot_window.show()
        else:
            # Update the existing plot window
            plot_window.update_data(df)

    def update_plot_windows(self):
        print("Updating plot windows...")
        df = self.fetch_live_data()
        if df is None:
            return

        # Find the plot window for the current instrument and update it
        for window in self.plot_windows:
            if window.instrument == self.selected_instrument:
                window.update_data(df)
                break

    def setDate(self, date):
        self.startDate = date


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CandlestickGUI()
    gui.show()
    sys.exit(app.exec())
