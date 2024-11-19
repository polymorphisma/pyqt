from PyQt5.QtCore import QDate, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QDateEdit, QDoubleSpinBox
from updated_plotWindow import PlotWindow
import sys
import pandas as pd
import MetaTrader5 as mt
from datetime import datetime


class CandlestickGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Candlestick Chart")
        self.windowWidth = 800
        self.startRange = 20
        self.baseHeight = 30
        self.setFixedSize(self.windowWidth, 300)

        # MetaTrader5 variables
        self.symbol = "EURUSD"
        self.timeframe = mt.TIMEFRAME_M1
        self.df = pd.DataFrame()  # Initialize an empty DataFrame

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
            

        # Start fetching live data
        self.start_date_label = QLabel(self)
        self.start_date_label.setText("Fetching data for:")
        self.start_date_label.move(self.startRange, self.baseHeight)

        self.startRange += 150
        self.symbol_label = QLabel(self)
        self.symbol_label.setText(self.symbol)
        self.symbol_label.move(self.startRange, self.baseHeight)

        # Candle width selection field
        self.baseHeight += 40
        self.startRange = 20

        self.candle_width_label = QLabel(self)
        self.candle_width_label.setText("Candle Width (x% of width):")
        self.candle_width_label.move(self.startRange, self.baseHeight)

        self.startRange += 180
        self.doubleSpinBox = QDoubleSpinBox(self)
        self.doubleSpinBox.setDecimals(2)
        self.doubleSpinBox.setRange(0, 100)
        self.doubleSpinBox.setSingleStep(0.01)
        self.doubleSpinBox.move(self.startRange, self.baseHeight)

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

        self.plot_windows = []

        # Timer for live updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_live_data)
        self.timer.start(10000)  # Fetch new data every minute

        # Fetch initial data
        self.fetch_live_data()

    def fetch_live_data(self):
        """Fetch the latest data from MetaTrader5."""
        # date_from = datetime.now() - pd.Timedelta(minutes=60)
        date_from = datetime(2024, 11, 14)
        date_to = datetime.now()

        # Retrieve price data from MetaTrader5
        price = mt.copy_rates_range(self.symbol, self.timeframe, date_from, date_to)
        if price is None or len(price) == 0:
            self.errorDisplay("No data retrieved from MetaTrader5")
            return

        # Update DataFrame
        self.df = pd.DataFrame(price)
        self.df = self.df[:100]
        self.df['time'] = pd.to_datetime(self.df['time'], unit='s')

        # Rename 'time' column to 'DateTime' to match plotWindow expectations
        self.df.rename(columns={"time": "DateTime", "open": "Open", "high": "High", 
                                "low": "Low", "close": "Close", "tick_volume": "Volume"}, 
                    inplace=True)

        self.errorDisplay(f"Data updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Automatically refresh the plot
        self.plot_candles()

    def errorDisplay(self, error):
        self.errorLabel.setText(error)

    def plot_candles(self):
        """Plot the candlestick chart."""
        if self.df.empty:
            self.errorDisplay("No data to plot.")
            return

        persentageVal = float(self.doubleSpinBox.value())
        plot_window = PlotWindow(df=self.df, persentageVal=persentageVal)
        self.plot_windows.append(plot_window)
        plot_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = CandlestickGUI()
    gui.show()
    sys.exit(app.exec())
