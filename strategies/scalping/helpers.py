from core.settings import ULTIMATE_SCALPING_SETTINGS
from core.indicators import EmaCross
from core import apirequests


def get_scalping_trend(symbol):
    """
    Get the ema cross trend for the scalping direction.
    """
    period = ULTIMATE_SCALPING_SETTINGS['trend']['period']
    quantity = ULTIMATE_SCALPING_SETTINGS['default_quantity']
    candles = apirequests.get_candles(period, quantity, symbol)
    fast_period = ULTIMATE_SCALPING_SETTINGS['trend']['fast_ema']
    slow_period = ULTIMATE_SCALPING_SETTINGS['trend']['slow_ema']
    
    ema_cross = EmaCross(candles, fast_ema_period=fast_period, slow_ema_period=slow_period)
    
    return 'buy' if ema_cross.is_bullish else 'sell'


