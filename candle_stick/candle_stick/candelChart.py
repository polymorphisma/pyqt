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
        self.factor = 10000

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
        # username = 10004945780
        # password = "*5PyZjTb"
        # server = "MetaQuotes-Demo"
        username = 52061104
        password = "0L@o8E4lAemqCb"
        server = "ICMarketsSC-Demo"

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

                # Add a QTimer for live updates
        self.live_update_timer = QTimer()
        self.live_update_timer.timeout.connect(self.update_live_data)  # Connect timer to the update method
        self.live_data_window = None  # To hold the PlotWindow instance for live updates
        self.latest_timestamp = None  # Track the latest timestamp for fetching new data


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
        # date_from = datetime.datetime.now() - datetime.timedelta(days=3)  # Fetch last 60 minutes for context
        # datetime_from = max(date_from, self.latest_timestamp or date_from)
        # date_to = datetime.datetime.now()


        date_from = self.date_edit.date().toPyDate()
        date_from = datetime.datetime.combine(date_from, datetime.datetime.min.time())
        
        datetime_from = max(date_from, self.latest_timestamp or date_from)
        # datetime_from = datetime.datetime.combine(datetime_from, datetime.datetime.min.time())
        date_to = datetime.datetime.now()

        print(date_from)
        print(datetime_from)
        print(date_to)
        print(self.latest_timestamp)
        # Retrieve price data from MetaTrader5
        price = mt.copy_rates_range(self.selected_instrument, self.metatrader_timeframe, datetime_from, date_to)
        if price is None or len(price) == 0:
            self.errorDisplay("No data retrieved from MetaTrader5")
            return

        # Update DataFrame
        df = pd.DataFrame(price)
        df['time'] = pd.to_datetime(df['time'], unit='s')

        # Renaming 'time' column to 'DateTime' to match PlotWindow expectations
        df.rename(columns={
            "time": "DateTime", "open": "Open", "high": "High",
            "low": "Low", "close": "Close", "tick_volume": "Volume"
        }, inplace=True)

        df = df[['DateTime', 'Open', 'High', 'Low', 'Close', 'Volume']]

        print("-" * 100)
        print(df)
        print("-" * 100)

        if self.latest_timestamp is not None:
            # Filter out data older than the latest timestamp
            df = df[df['DateTime'] > self.latest_timestamp]

        if not df.empty:
            self.latest_timestamp = df['DateTime'].max()
        return df

    def getDataFrame(self):

        if self.file_path is not None:
            df = self.getDataFromFile()

        elif self.selected_instrument != '-' and self.file_path is None:
            df = self.fetch_live_data()

        return df
    


    def generate_dummy_data(self):
        """Generate dummy data to simulate live updates."""
        import random

        # Create a single row of dummy data
        # You can adjust the logic to generate data that makes sense for your application
        last_row = self.live_data_window.df.iloc[-1]
        last_time = last_row['DateTime']

        # Increment time by the interval (e.g., 1 minute)
        new_time = last_time + datetime.timedelta(minutes=1)

        # Generate random price changes
        base_price = last_row['Close'] / self.factor
        open_price = base_price + random.uniform(-0.001, 0.001)
        high_price = open_price + random.uniform(0, 0.002)
        low_price = open_price - random.uniform(0, 0.002)
        close_price = open_price + random.uniform(-0.001, 0.001)

        # Create a DataFrame with the new data
        data = {
            'DateTime': [new_time],
            'Open': [open_price],
            'High': [high_price],
            'Low': [low_price],
            'Close': [close_price],
            'Volume': [0],  # Volume can be set to 0 or any dummy value
        }
        df = pd.DataFrame(data)

        return df
    def update_live_data(self):
        """Fetch new data and update the live chart."""
        print("Updating live data...")

        if self.live_data_window is None or self.selected_instrument is None:
            return

        new_data = self.fetch_live_data()
        # new_data = self.generate_dummy_data()
        print(new_data)
        if new_data is not None and not new_data.empty:
            print(f"Adding {len(new_data)} new rows to the chart.")
            self.live_data_window.add_live_data(new_data)

    # def update_live_data(self):
    #     """Simulate live data updates with dummy data."""
    #     print("Updating live data...")

    #     if self.live_data_window is None:
    #         return

    #     # Generate dummy data
    #     new_data = self.generate_dummy_data()
    #     print(new_data)
    #     if new_data is not None and not new_data.empty:
    #         print(f"Adding {len(new_data)} new rows to the chart.")
    #         self.live_data_window.add_live_data(new_data)


    # def plot_candles(self, empty=False):
    #     """Handle initial plotting and setup live updates if using live data."""
    #     self.errorDisplay(" ")
    #     df = self.getDataFrame()
    #     if df is None:
    #         return

    #     persentageVal = float(self.doubleSpinBox.value())
    #     self.live_data_window = PlotWindow(df=df, persentageVal=persentageVal)
    #     self.plot_windows.append(self.live_data_window)
    #     self.live_data_window.show()

    #     if self.selected_instrument is not None and self.file_path is None:
    #         # If live data is selected, start live updates
    #         self.live_update_timer.start(10000)  # Fetch new data every 5 seconds

    def plot_candles(self, empty=False):
        """Handle initial plotting and setup live updates."""
        self.errorDisplay(" ")
        df = self.getDataFrame()
        if df is None:
            return
        print(df)
        persentageVal = float(self.doubleSpinBox.value())
        self.live_data_window = PlotWindow(df=df, persentageVal=persentageVal)
        self.plot_windows.append(self.live_data_window)
        self.live_data_window.show()

        # Start the live update timer regardless of live data source
        self.live_update_timer.start(5000)  # Update every 5 seconds



    def setDate(self, date):
        self.startDate = date


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CandlestickGUI()
    gui.show()
    sys.exit(app.exec())
