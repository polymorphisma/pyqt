from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QWidget, QLabel, QPushButton, QDateEdit, QDoubleSpinBox, QComboBox, QFileDialog
from PyQt5.QtCore import QDate, QTimer
import MetaTrader5 as mt
import pandas as pd
import sys


class CandlestickGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.selected_instrument = None
        self.setWindowTitle("Candlestick Chart")
        self.windowWidth = 800
        self.startRange = 20
        self.baseHeight = 30

        # Interval Mapping
        self.interval_mapping = {
            "1 minute": "TIMEFRAME_M1",
            "2 minutes": "TIMEFRAME_M2",
            "3 minutes": "TIMEFRAME_M3",
            "4 minutes": "TIMEFRAME_M4",
            "5 minutes": "TIMEFRAME_M5",
            "6 minutes": "TIMEFRAME_M6",
            "10 minutes": "TIMEFRAME_M10",
            "12 minutes": "TIMEFRAME_M12",
            "15 minutes": "TIMEFRAME_M15",
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

        self.interval_mapping_metatrader = {
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

        # MetaTrader5 Initialization
        mt.initialize()
        username = 10004945780
        password = "*5PyZjTb"
        server = "MetaQuotes-Demo"

        if not mt.login(username, password, server):
            print("MetaTrader5 login failed")
            return
        else:
            print("MetaTrader5 login successful")

        # Add Tabs
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        # Create Main Tab
        self.main_tab = QWidget()
        self.tabs.addTab(self.main_tab, "Candlestick Chart")

        # Add Widgets to Main Tab
        self.file_label = QLabel("Select CSV file:", self.main_tab)
        self.file_label.move(self.startRange, self.baseHeight)

        self.startRange += 85
        self.file_button = QPushButton("Select File", self.main_tab)
        self.file_button.move(self.startRange, self.baseHeight)
        self.file_button.clicked.connect(self.select_file)

        self.startRange += 150
        self.start_date_label = QLabel("Start Date (Y-M-D):", self.main_tab)
        self.start_date_label.move(self.startRange, self.baseHeight)

        self.startRange += 120
        self.date_edit = QDateEdit(QDate.currentDate(), self.main_tab)
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        self.date_edit.move(self.startRange, self.baseHeight)

        self.startRange += 150
        self.end_date_label = QLabel("End Date (Y-M-D):", self.main_tab)
        self.end_date_label.move(self.startRange, self.baseHeight)

        self.startRange += 120
        self.end_date_entry = QDateEdit(QDate.currentDate(), self.main_tab)
        self.end_date_entry.setDisplayFormat('yyyy-MM-dd')
        self.end_date_entry.move(self.startRange, self.baseHeight)

        self.baseHeight += 40
        self.startRange = 20
        self.candle_width_label = QLabel("Candle Width (% of width):", self.main_tab)
        self.candle_width_label.move(self.startRange, self.baseHeight)

        self.startRange += 180
        self.doubleSpinBox = QDoubleSpinBox(self.main_tab)
        self.doubleSpinBox.setDecimals(2)
        self.doubleSpinBox.setRange(0, 100)
        self.doubleSpinBox.setSingleStep(0.01)
        self.doubleSpinBox.move(self.startRange, self.baseHeight)

        self.startRange += 120
        self.instrument_label = QLabel("Select Instrument:", self.main_tab)
        self.instrument_label.move(self.startRange, self.baseHeight)

        self.startRange += 100
        self.instrument_dropdown = QComboBox(self.main_tab)
        self.instrument_dropdown.move(self.startRange, self.baseHeight)
        self.instruments = ["-", "BTCUSD", "EURUSD", "RANUSD"]
        self.instrument_dropdown.addItems(self.instruments)
        self.instrument_dropdown.currentIndexChanged.connect(self.on_instrument_selected)

        self.startRange += 120
        self.interval_label = QLabel("Select Interval:", self.main_tab)
        self.interval_label.move(self.startRange, self.baseHeight)

        self.startRange += 100
        self.interval_dropdown = QComboBox(self.main_tab)
        self.interval_dropdown.move(self.startRange, self.baseHeight)
        self.intervals = list(self.interval_mapping.keys())
        self.interval_dropdown.addItems(self.intervals)
        self.interval_dropdown.currentIndexChanged.connect(self.on_interval_selected)

        self.baseHeight += 60
        self.plot_button = QPushButton("Plot", self.main_tab)
        self.plot_button.move(int(self.windowWidth / 2) - 50, self.baseHeight)
        self.plot_button.clicked.connect(self.plot_candles)

        self.baseHeight += 60
        self.errorLabel = QLabel("", self.main_tab)
        self.errorLabel.setStyleSheet("color: red;")
        self.errorLabel.move(20, self.baseHeight)

        # Timer for live updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(10000)

    def select_file(self):
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV file")
        self.errorLabel.setText(f"Selected file: {self.file_path}" if self.file_path else "No file selected.")

    def on_instrument_selected(self):
        self.selected_instrument = self.instrument_dropdown.currentText()

    def on_interval_selected(self):
        selected_interval = self.interval_dropdown.currentText()
        self.selected_interval = self.interval_mapping.get(selected_interval, "TIMEFRAME_M1")

    def update_data(self):
        if self.file_path:
            self.get_data_from_file()
        else:
            self.fetch_live_data()

    def get_data_from_file(self):
        # Dummy implementation
        print("Fetching data from file...")

    def fetch_live_data(self):
        # Dummy implementation
        print("Fetching live data from MetaTrader5...")

    def plot_candles(self):
        self.errorLabel.setText("Plotting candles... (Feature not implemented)")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CandlestickGUI()
    gui.show()
    sys.exit(app.exec())
