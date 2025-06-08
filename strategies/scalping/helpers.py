from scalping_settings import ULTIMATE_SCALPING_SETTINGS
from core.indicators import EmaCross
from core import apirequests

def get_trend(symbol, period, quantity=500):
    """
    Get the biase for the scalping direction.
    """
    candles = apirequests.get_candles(period, quantity, symbol)
    fast_period = ULTIMATE_SCALPING_SETTINGS["biase_fast_ema"]
    slow_period = ULTIMATE_SCALPING_SETTINGS["biase_slow_ema"]
    
    ema_cross = EmaCross(candles, fast_ema_period=fast_period, slow_ema_period=slow_period)
    
    return 'buy' if ema_cross.is_bullish else 'sell'


