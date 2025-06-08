import time
from strategies import Scalper
from core import util
import pprint
from strategies.scalping import helpers

# from alerts.sounds import play_alert

SET_TUP_PERIODS = ["30m"]
TRADE_PERIODS = ["30m"]
SYMBOLS = ['BTCUSDT', 'ETHUSDT']
ALERT_UPTIME = 90


# BIASE = helpers.get_biase(period='1d', quantity=500, symbol='BTCUSDT')

def get_signals():
    signals = []
    for symbol in SYMBOLS:
        for period in SET_TUP_PERIODS:
            scalper = Scalper(symbol, setup_period=period, signal_period=TRADE_PERIODS[0])
            if signal := scalper.get_trade():
                signals.append(signal)
    return signals if signals else None


def get_trade_alert():
    trade_alerts = []
    signals = get_signals()

    if signals is not None:
        for signal in signals:
            if not signal:
                continue
            trade_time = signal["time"]
            if util.is_active_signal(trade_time, ALERT_UPTIME):
                trade_alerts.append(signal)
    return trade_alerts if trade_alerts else None


def print_alert(trade_alerts):
    for trade in trade_alerts:
        pprint.pprint(trade, indent=4, depth=2)


def play_alert():
    from alerts import sounds
    sounds.play_alert()


def main():
    while True:
        trade_alerts = get_trade_alert()
        if trade_alerts:
            print_alert(trade_alerts)
            play_alert()
        time.sleep(60)


if __name__ == "__main__":
    print("Scalper running...")
    main()
