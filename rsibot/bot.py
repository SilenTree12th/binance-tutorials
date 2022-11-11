import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/btcusdt@kline_15m"


RSI_PERIOD = 16
RSI_OVERSOLD = 20
TRADE_SYMBOL = 'BTCUSDT'


closes = []

client = Client(config.API_KEY, config.API_SECRET, tld='com')

def order(side, quantity, symbol,order_type=ORDER_TYPE_LIMIT):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    
    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']
    TRADE_QUANTITY = round(11/close,5)

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))
            
            if last_rsi <= RSI_OVERSOLD:
                print("Oversold! Buy! Buy! Buy!")
                # put binance buy order logic here
                order_succeeded = False
                while not order_succeeded:
                    order_succeeded = client.create_market_order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
