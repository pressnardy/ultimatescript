from core.charting import Chart
from core import fakeouts
from strategies.scalping.scalping_settings import ULTIMATE_SCALPING_SETTINGS
from core import apirequests


class UltimateSetups:
    def __init__(self, candles, buy_levels=None, sell_levels=None):
        self._candles = candles
        self._pivot_lookback = ULTIMATE_SCALPING_SETTINGS["pivot_lookback"]
        self._sell_levels = sell_levels
        self._buy_levels = buy_levels
        self._fo_lookback = ULTIMATE_SCALPING_SETTINGS["fo_lookback"]
        self._fo_candles = candles[-self._fo_lookback:]
        self._range_quantity = ULTIMATE_SCALPING_SETTINGS["default_quantity"]

    def start_chart(self):
        return Chart.start_chart(self._candles, self._range_quantity, self._pivot_lookback)

    def buy_levels(self):
        if self._buy_levels:
            return self._buy_levels
        chart = self.start_chart()
        return chart.lows()

    def all_buy_levels(self):
        if self._buy_levels:
            return self._buy_levels
        chart = self.start_chart()
        return chart.all_lows()

    def sell_levels(self):
        if self._sell_levels is not None:
            return self._sell_levels
        chart = self.start_chart()
        return chart.highs()

    def all_sell_levels(self):
        if self._sell_levels is not None:
            return self._sell_levels
        chart = self.start_chart()
        return chart.all_highs()

    def get_signals(self):
        candles, pivot_lookback, fo_lookback = self._candles, self._pivot_lookback, self._fo_lookback
        buy_levels, sell_levels = self.buy_levels(), self.sell_levels()
        signals = fakeouts.get_all_signals(candles, buy_levels, sell_levels, fo_lookback)
        if signals:
            sorted_signals = sorted(signals, key=lambda x: x['trigger_candle']['time'], reverse=True)
            return sorted_signals[0]
        return None

    def get_all_signals(self):
        candles, pivot_lookback, fo_lookback = self._candles, self._pivot_lookback, self._fo_lookback
        buy_levels, sell_levels = self.all_buy_levels(), self.all_sell_levels()
        all_signals = fakeouts.get_all_signals(candles, buy_levels, sell_levels, fo_lookback)
        if all_signals:
            return all_signals
        return None


class Scalper:
    def __init__(self, symbol=None, setup_period=None, signal_period=None, signal_quantity=None):
        self._setup_period = setup_period
        self._signal_period = signal_period
        self._symbol = symbol
        self._setup_quantity = ULTIMATE_SCALPING_SETTINGS["default_quantity"]
        self._signal_quantity = signal_quantity
        self._setup_candles = apirequests.get_candles(self.setup_period, self._setup_quantity, self.symbol)
        self._signal_candles = apirequests.get_candles(self.signal_period, self.signal_quantity, self.symbol)

    @property
    def symbol(self):
        if self._symbol:
            return self._symbol
        return ULTIMATE_SCALPING_SETTINGS["default_symbol"]

    @property
    def setup_period(self):
        if self._setup_period:
            return self._setup_period
        return ULTIMATE_SCALPING_SETTINGS["default_period"]

    @property
    def signal_quantity(self):
        if self._signal_quantity:
            return self._signal_quantity
        return ULTIMATE_SCALPING_SETTINGS["signal_quantity"][self.signal_period]

    @property
    def signal_candles(self):
        return self._signal_candles

    @signal_candles.setter
    def signal_candles(self, candles):
        self._signal_candles = candles

    @property
    def signal_period(self):
        if self._signal_period:
            return self._signal_period
        return ULTIMATE_SCALPING_SETTINGS["default_period"]

    @signal_period.setter
    def signal_period(self, value):
        self._signal_period = value

    @property
    def setup_candles(self):
        return self._setup_candles

    @setup_candles.setter
    def setup_candles(self, candles):
        self._setup_candles = candles

    def get_buy_levels(self):
        candles = self.setup_candles
        buy_levels = UltimateSetups(candles).buy_levels()
        return buy_levels

    def get_all_buy_levels(self):
        candles = self.setup_candles
        buy_levels = UltimateSetups(candles).all_buy_levels()
        return buy_levels

    def get_sell_levels(self):
        candles = self.setup_candles
        sell_levels = UltimateSetups(candles).sell_levels()
        return sell_levels

    def get_all_sell_levels(self):
        candles = self.setup_candles
        sell_levels = UltimateSetups(candles).all_sell_levels()
        return sell_levels

    def get_signal(self):
        candles = self.signal_candles
        buy_levels = self.get_buy_levels()
        sell_levels = self.get_sell_levels()
        return UltimateSetups(candles, buy_levels, sell_levels).get_signals()

    def get_all_signals(self):
        candles = self.signal_candles
        buy_levels = self.get_all_buy_levels()
        sell_levels = self.get_all_sell_levels()
        return UltimateSetups(candles, buy_levels, sell_levels).get_all_signals()

    def get_trade(self):
        signal = self.get_signal()
        return self.get_trade_detail(signal)

    def get_trade_detail(self, signal):
        trade_details = {}
        if signal is None:
            return None
        if buy_trade := BuyTrade(signal).trade_details():
            trade_details.update(buy_trade)

        if sell_trade := SellTrade(signal).trade_details():
            trade_details.update(sell_trade)

        trade_details["type"], trade_details["period"], trade_details["symbol"] = \
            signal["signal_type"], self.signal_period, self.symbol
        return trade_details

    def get_prev_trades(self):
        prev_trades = []
        if signals := self.get_all_signals():
            # print(signals[-1])
            for signal in signals:
                trade_details = self.get_trade_detail(signal)
                prev_trades.append(trade_details)

        return prev_trades if prev_trades else None


class TradeSetup:
    def __init__(self, signal, tp1_rrr=None, tp2_rrr=None, sl_padding=None):
        self._tp1_rrr = tp1_rrr
        self._tp2_rrr = tp2_rrr
        self._sl_padding = sl_padding
        self._signal = signal
        self._lookback_hl = signal["lookback_hl"]
        self._trigger_candle = signal["trigger_candle"]
        self._entry_price = signal["trigger_candle"]["close"]
        self._signal_time = signal["trigger_candle"]["time"]

    @property
    def entry_price(self):
        return self._entry_price

    @property
    def signal_time(self):
        return self._signal_time

    @property
    def trade_direction(self):
        signal_type = self._signal["signal_type"]
        if "buy" in signal_type:
            return "buy"
        if "sell" in signal_type:
            return "sell"

    @property
    def tp1_rrr(self):
        if self._tp1_rrr:
            return self._tp1_rrr
        return ULTIMATE_SCALPING_SETTINGS["tp1_rrr"]

    @property
    def tp2_rrr(self):
        if self._tp2_rrr:
            return self._tp2_rrr
        return ULTIMATE_SCALPING_SETTINGS["tp2_rrr"]

    @property
    def sl_padding(self):
        if self._sl_padding is None:
            return ULTIMATE_SCALPING_SETTINGS["stop_lose_padding"]
        return self._sl_padding

    def sell_sl(self):
        lookback_high = self._lookback_hl
        return lookback_high + (self.sl_padding * lookback_high)

    def buy_sl(self):
        lookback_low = self._lookback_hl
        return lookback_low - (self.sl_padding * lookback_low)


class BuyTrade(TradeSetup):
    def __init__(self, signal):
        super().__init__(signal)

    def percentage_risk(self):
        return (self._entry_price - self.buy_sl()) / self._entry_price * 100

    def tp1_percentage_profit(self):
        return self.tp1_rrr * self.percentage_risk()

    def percentage_profit(self):
        return self.tp2_rrr * self.percentage_risk()

    def tp1(self):
        return self._entry_price + (self.tp1_percentage_profit() * self._entry_price / 100)

    def tp2(self):
        return self._entry_price + (self.percentage_profit() * self._entry_price / 100)

    def trade_details(self):
        if self.trade_direction != "buy":
            return None
        return {
            "time": self.signal_time,
            "entry_price": self.entry_price,
            "sl": self.buy_sl(),
            "tp1": self.tp1(),
            "tp2": self.tp2(),
            "direction": "buy"
        }


class SellTrade(TradeSetup):
    def __init__(self, signal):
        super().__init__(signal)

    def percentage_risk(self):
        return (self.sell_sl() - self._entry_price) / self._entry_price * 100

    def tp1(self):
        perc_profit = self.tp1_rrr * self.percentage_risk()
        tp = self._entry_price - (perc_profit * self._entry_price / 100)
        return tp

    def tp2(self):
        perc_profit = self.tp2_rrr * self.percentage_risk()
        tp = self._entry_price - (perc_profit * self._entry_price / 100)
        return tp

    def trade_details(self):
        if self.trade_direction != "sell":
            return None
        return {
            "time": self.signal_time,
            "entry_price": self.entry_price,
            "sl": self.sell_sl(),
            "tp1": self.tp1(),
            "tp2": self.tp2(),
            "direction": "sell"
        }


if __name__ == "__main__":
    scalper = Scalper("BTCUSDT")
    trade = scalper.get_trade()
    print(trade)
