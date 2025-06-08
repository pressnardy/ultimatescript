import copy
import json
import time
from datetime import datetime, timezone
from core import apirequests
from core import settings


def get_candles_from_json(file_name):
    with open(file_name, "r") as file:
        candles = json.load(file)
    return candles


def highs_to_levels(pivots):
    levels = []
    for p in pivots:
        level_data = {
            "time": p["time"],
            "value": p["high"]
        }
        levels.append(level_data)
    return levels


def lows_to_levels(pivots):
    levels = []
    for p in pivots:
        level_data = {
            "time": p["time"],
            "value": p["low"]
        }
        levels.append(level_data)
    return levels


# def process_time(unix):
#     return pd.to_datetime(unix, unit="ms")


def process_levels(levels):
    resolved_levels = []
    for p in levels:
        level_data = {
            "time": p["time"],
            "value": p["high"]
        }
        resolved_levels.append(level_data)
    return resolved_levels


def get_next(elements: list, index: int):
    """
    returns the next element in a list
    """
    if index >= len(elements) - 1:
        return None
    return elements[index + 1]


def get_range_details(candles):
    min_open = min(c["open"] for c in candles)
    min_close = min(c["close"] for c in candles)
    min_low = min(c["low"] for c in candles)
    max_open = max(c["open"] for c in candles)
    max_close = max(c["close"] for c in candles)
    max_high = max(c["high"] for c in candles)
    min_oc = min(min_open, min_close)
    max_oc = max(max_open, max_close)
    return min_oc, min_low, max_oc, max_high


def eliminate_triggers(triggers):
    """
    prevents subsequent candles that share a lookback high from triggering sell signal
    for the same level before the previous signal is stopped out the trade
    """
    level_triggers = copy.deepcopy(triggers)
    for i in level_triggers:
        i_time = i["trigger_candle"]["time"]
        for j in level_triggers:
            j_time = j["trigger_candle"]["time"]
            if i["level"] == j["level"] and i_time < j_time:
                i_lookback_hl = i["lookback_hl"]
                j_lookback_hl = j["lookback_hl"]
                if "sell" in i["signal_type"] and i_lookback_hl >= j_lookback_hl or \
                        "buy" in i["signal_type"] and i_lookback_hl <= j_lookback_hl:
                    level_triggers = [t for t in level_triggers if t != j]

    return level_triggers


def is_active_signal(signal_time, uptime_duration=None):
    """
    Check if the signal trigger time is within the last uptime duration.
    parameter:
        signal_time (unix_time): the timestamp to check.
        uptime_duration (int): duration in minutes.
    """
    if not uptime_duration:
        uptime_duration = settings.ULTIMATE_SCALPING_SETTINGS["signal_uptime"]
    uptime_duration_in_seconds = uptime_duration * 60
    current_time = datetime.now(timezone.utc).timestamp()
    difference = abs(current_time - signal_time / 1000)

    return difference <= uptime_duration_in_seconds


def create_fo_signal(period, trigger):
    """
    resolves the signal returned from SFP and Failed Auctions
    """
    signal = {"period": period, **trigger}
    return signal


def get_lookback_candles(candles, lookback, candle_index):
    if lookback <= candle_index <= len(candles):
        fo_candles = candles[candle_index - lookback:candle_index + 1]
        return fo_candles

    return False


def resolve_level(level):
    """
    extracts level values for levels passed as dicts
    and return a list of int
    """
    if isinstance(level, dict):
        level = level["value"]
    return level


def resolve_levels(levels):
    resolved_levels = []
    for level in levels:
        if isinstance(level, dict):
            level = level["value"]
        resolved_levels.append(level)
    return resolved_levels


def get_untested_levels(candles, levels, signal_type):
    """
    check if a level has been tested by candles
    uses the trigger candle to eliminate previously tested levels
    returns: the levels that have not been broken
    """
    untested_levels = []
    for level in levels:
        if not is_tested(candles, level, signal_type):
            untested_levels.append(level)
    return untested_levels


def is_tested(candles, level, signal_type):
    max_breach = settings.ULTIMATE_SCALPING_SETTINGS["max_breach"]
    breach = 0
    for candle in candles:
        if int(candle["time"]) < int(level["time"]):
            continue
        level_value = level["value"]
        if candle["close"] < level_value and "buy" in signal_type:
            breach += 1
        if candle["close"] > level_value and "sell" in signal_type:
            breach += 1
        if breach >= max_breach:
            return True
    return False


def write_to_json(data, file_name):
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)


def create_markers(signals):

    markers = []
    for signal in signals:
        if signal["direction"] == "buy":
            buy_marker = copy.deepcopy(settings.MARKERS["buy_marker"])
            buy_marker["time"] = signal["time"]
            markers.append(buy_marker)

        if signal["direction"] == "sell":
            sell_marker = copy.deepcopy(settings.MARKERS["sell_marker"])
            sell_marker["time"] = signal["time"]
            markers.append(sell_marker)
    return markers


def get_unique_trades(trades):
    trades_copy = copy.deepcopy(trades)
    unique_trades = []
    for trade in trades_copy:
        unique_trades.append(trade)
        trades_copy = [j for j in trades_copy if j["entry_price"] != trade["entry_price"]]
    return unique_trades


def get_trade_periods(setup_period):
    return settings.ULTIMATE_SCALPING_SETTINGS["trade_periods"][setup_period]


def get_default_period():
    return settings.ULTIMATE_SCALPING_SETTINGS["default_period"]
