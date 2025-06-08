import requests


def get_candles(timeframe, quantity, symbol):
	"""
	excludes the last candle which is always an open candle
	"""
	url = 'https://api.binance.com/api/v3/klines'
	params = {
		'symbol': symbol,
		'interval': timeframe
	}
	response = requests.get(url, params=params).json()
	# print(response)
	candles = []
	for data in response:

		try:
			candle = {}
			open_time, open_price, high, low, close, volume, end_time = data[:7]
			candle['time'] = open_time
			candle['open'] = float(open_price)
			candle['high'] = float(high)
			candle['low'] = float(low)
			candle['close'] = float(close)
			candle['volume'] = float(volume)
			candle["end_time"] = end_time
			candles.append(candle)
		except Exception:
			raise ValueError("Big error")

	try:
		return candles[- quantity:-1]
	except ValueError:
		raise ValueError(f"maximum number of candles is 500")


def get_cvd_candles(symbol, interval, start_time, end_time):
	"""
	Fetch candlestick data from Binance API with a specified start time and end time.
	for calculating cvd
	"""
	base_url = "https://api.binance.com"
	endpoint = "/api/v3/klines"
	url = f"{base_url}{endpoint}?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}"

	response = requests.get(url).json()
	candles = []

	for data in response:
		try:
			candle = {}
			open_time, open_price, high, low, close, volume, end_time = data[:7]

			candle['open'] = float(open_price)
			candle['close'] = float(close)
			candle['volume'] = float(volume)
			candles.append(candle)
		except ValueError:
			raise ValueError

	return candles


if __name__ == "__main__":
	timeframe = "4h"
	symbol = "BTCUSDT"
	quantity = 200
	print(get_candles(timeframe, quantity, symbol))
