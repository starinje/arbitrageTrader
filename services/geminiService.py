import time
import uuid
import base64
import hmac
import hashlib
import requests
import json
import sys
import moment
import datetime
import arrow

def createRequestConfig(key, secret, payload):
	encodedPayload = base64.b64encode(json.dumps(payload))
	signature = hmac.new(secret, encodedPayload, hashlib.sha384).hexdigest()
	config = {
			  'X-GEMINI-APIKEY': key,
              'X-GEMINI-PAYLOAD': encodedPayload,
              'X-GEMINI-SIGNATURE': signature,
			 }

	return config

def nonce_time():
    nonce = time.time()
    nonce = float(str(nonce).replace(".", ""))*100000
    return str(nonce)


def nonce_uuid():
	return uuid.uuid4().hex

class geminiService:

    def __init__(self, options):
        self.options = options
        subdomain = 'api.sandbox' if self.options['sandbox'] == True else 'api'
        self.baseUrl = 'https://' + subdomain + "." + 'gemini.com/v1'
        return 
        

    def requestPrivate(self, endpoint, params):
        time.sleep(1)
        requestUrl = self.baseUrl + endpoint

        payload = params.copy()
        payload['request'] = "/v1" + endpoint
        payload['nonce'] = nonce_time()

        config = createRequestConfig(self.options["key"], self.options["secret"], payload)
    
        r = requests.post(requestUrl, headers=config)

        return json.loads(r.text)

    def requestPublic(self, endpoint, params):
        requestUrl = self.baseUrl + endpoint
        r = requests.get(requestUrl)
        return json.loads(r.text)

    def getOrderBook(self):
        try: 
            orderBook = self.requestPublic('/book/ethusd', {})
    
            bids = []
            asks = []

            for bidLevel in orderBook['bids']: 
                bid = {
                    'price': bidLevel['price'],
                    'amount': bidLevel['amount'],
                }
                bids.append(bid)

            for askLevel in orderBook['asks']: 
                ask = {
                    'price': askLevel['price'],
                    'amount': askLevel['amount'],
                }
                asks.append(ask)
            
            reformattedOrderBook = {
                'asks': asks,
                'bids': bids,
            }

            return reformattedOrderBook

        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def executeTrade(self, positionChange, geminiTradeResults):
        try:
            print 'in gemini executeTrade...'
            
            tradeDetails = positionChange['gemini']
            counterPrice = positionChange['gdax']['rate']

            tradeCompleted = False
            tradeProfitable = True

            finalOrderResults = None
            price = None
            tradeQuantity = tradeDetails['quantity']

            while not tradeCompleted & tradeProfitable:
                # time.sleep(1.1)
                orderBook = self.getOrderBook()

                if tradeDetails['action'] == 'buy':
                    lowestSellPriceLevel = filter(lambda ask: float(ask['amount']) >= tradeQuantity, orderBook['asks'])

                    if len(lowestSellPriceLevel) > 0:
                        price = float(lowestSellPriceLevel[0]['price'])
                    else:
                        continue
                    
                    # if price >= counterPrice:
                    #     tradeProfitable = False
                    #     continue

                if tradeDetails['action'] == 'sell':
                    
                    highestBuyPriceLevel = filter(lambda bid: float(bid['amount']) >= tradeQuantity, orderBook['bids'])

                    if len(highestBuyPriceLevel) > 0:
                        price = float(highestBuyPriceLevel[0]['price'])
                    else:
                        continue
                    
                    # if price <= counterPrice:
                    #     tradeProfitable = False
                    #     continue

                print 'placing ' + tradeDetails['action'] + ' trade on Gemini for ' + str(tradeDetails['quantity']) + ' ethereum at ' + str(price) + '/eth'

                orderParams = {
                    'client_order_id': "20150102-4738721", 
                    'symbol': 'ethusd',       
                    'amount': tradeQuantity,        
                    'price': price,
                    'side': tradeDetails['action'],
                    'type': 'exchange limit'
                }

                if orderParams['price'] < 100 or orderParams['price'] > 400:
                    print 'failed gemini price sanity check. price: ' + str(orderParams['price'])
                    sys.exit()

                orderResults = self.newOrder(orderParams)
                print orderResults

                if 'order_id' not in orderResults:
                    print 'gemini order could not be submitted'
                    continue

                while not tradeCompleted:
                    time.sleep(2)
                    tradeStatus = self.orderStatus(orderResults['order_id'])
                    if tradeStatus['executed_amount'] == tradeStatus['original_amount']:
                        tradeCompleted = True
                        finalOrderResults = orderResults
                        continue
                    else:
                        print 'canceling all orders...'
                        self.cancelOrders()
                        tradeQuantity = float(tradeStatus['original_amount']) - float(tradeStatus['executed_amount'])
                        print 'new trading quantity: ' + str(tradeQuantity)
                        positionChange = positionChange.copy()
                        positionChange['quantity'] = tradeQuantity
                        self.executeTrade(positionChange, geminiTradeResults)
                        
            if tradeCompleted:
                    tradeSummary = self.orderHistory(finalOrderResults['order_id'])
                    finalTradeResults  = tradeSummary.copy()

                    finalTradeResults['action'] = tradeDetails['action']
                    geminiTradeResults.put([finalTradeResults])
                    return 
            elif not tradeProfitable:
                print tradeDetails['action'] + 'on gemini for ' + tradeDetails['quantity'] + 'ethereum at ' + price + '/eth was unsuccesful - order book no longer profitable'
                sys.exit()

        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def newOrder(self, params):
        try: 
            orderOptions = params.copy()
            orderOptions['client_order_id'] = 'someId'
            orderOptions['type'] = 'exchange limit'

            return self.requestPrivate('/order/new', orderOptions)
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def cancelOrders(self):
        try: 
            return self.requestPrivate('/order/cancel/all', {})
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def availableBalances(self):
        try: 
            return self.requestPrivate('/balances', {})
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def orderStatus(self, orderId):
        try: 
            return self.requestPrivate('/order/status', { 'order_id': orderId })
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def orderHistory(self, orderId):
        try: 
            trades = self.requestPrivate('/mytrades', { 'symbol': 'ETHUSD'} )
        
            orderTrades = filter(lambda trade: trade['order_id'] == orderId, trades)

            fee = 0
            amount = 0
            price = 0

            numberOfTrades = 0

            for trade in orderTrades:
                fee = float(trade['fee_amount']) + fee
                amount = float(trade['amount']) + amount
                price = float(trade['price']) + price
                numberOfTrades = numberOfTrades + 1
            
            averagePrice = price/numberOfTrades

            tradeSummary = {
                'fee': fee,
                'amount': amount,
                'price': price
            }

            return tradeSummary
        except Exception as e:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        

