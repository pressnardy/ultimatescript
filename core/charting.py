from core import pivots
from core import apirequests
from core import settings
from core import util


class Chart:
    def __init__(self, candles):
        self._candles = candles
        self._pivot_lookback = settings.CHART_SETTINGS["lookback"]
        self._time_frame = settings.TIMEFRAMES["default"]
        self._range_quantity = settings.CHART_SETTINGS["range_quantity"]

    @property
    def range_quantity(self):
        return self._range_quantity

    def set_range_quantity(self, quantity=None):
        if isinstance(quantity, int):
            self._range_quantity = quantity
        else:
            raise ValueError("The 'quantity' value should be an integer")

    def set_pivot_lookback(self, lookback=None):
        if not isinstance(lookback, int):
            raise ValueError("The 'lookback' value must be an integer")
        self._pivot_lookback = lookback

    def lows(self):
        candles = self._candles[-self.range_quantity:]
        supports = pivots.get_lows(candles, self._pivot_lookback)
        return util.lows_to_levels(supports)

    def highs(self):
        candles = self._candles[-self.range_quantity:]
        resistance_pivots = pivots.get_highs(candles, self._pivot_lookback)
        return util.highs_to_levels(resistance_pivots)

    def all_highs(self):
        candles = self._candles[-self.range_quantity:]
        resistance_pivots = pivots.get_resistance_pivots(candles, self._pivot_lookback)
        return util.highs_to_levels(resistance_pivots)

    def all_lows(self):
        candles = self._candles[-self.range_quantity:]
        supports = pivots.get_support_pivots(candles, self._pivot_lookback)
        return util.lows_to_levels(supports)

    @classmethod
    def start_chart(cls, candles: list, range_quantity: int, pivot_lookback: int):
        chart = cls(candles)
        chart.set_pivot_lookback(pivot_lookback)
        chart.set_range_quantity(range_quantity)
        return chart

    @classmethod
    def get_candles(cls, timeframe=settings.TIMEFRAMES["default"], quantity=settings.CHART_SETTINGS["range_quantity"],
                    symbol=settings.SYMBOLS["bitcoin"]):
        candles = apirequests.get_candles(timeframe, quantity, symbol)
        return cls(candles)

# if __name__ == "__main__":
# candles = apirequests.get_candles("30m", 500, "BTCUSDT")
# lookback = 30
# range_quantity = 500
#
# chart = Chart.start_chart(candles, range_quantity, lookback)
# highs = chart.all_highs()
# for h in highs:
#     print(h)
