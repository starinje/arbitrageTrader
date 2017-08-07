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

def nonce_time(self):
    nonce = time.time()
    nonce = str(nonce).split(".", 1)[0] + str(self.nonceIncrement)+'00'
    if self.nonceIncrement <= 9:
        self.nonceIncrement = self.nonceIncrement + 1
    else: 
        self.nonceIncrement = 0
    return nonce

def nonce_uuid():
	return uuid.uuid4().hex

class geminiService:

    def __init__(self, options):
        self.options = options
        self.nonceIncrement = 0
        subdomain = 'api.sandbox' if self.options['sandbox'] == True else 'api'
        self.baseUrl = 'https://' + subdomain + "." + 'gemini.com/v1'
        return 
    
    def requestPrivate(self, endpoint, params):
        requestUrl = self.baseUrl + endpoint

        payload = params.copy()
        payload['request'] = "/v1" + endpoint
        payload['nonce'] = nonce_time(self)

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
            
            tradeDetails = positionChange['gemini']
            counterPrice = positionChange['gdax']['rate']

            tradeCompleted = False
            tradeProfitable = True

            finalOrderResults = None
            price = None
            tradeQuantity = tradeDetails['quantity']

            while not tradeCompleted and tradeProfitable:
                orderBook = self.getOrderBook()

                if tradeDetails['action'] == 'buy':
                    lowestSellPriceLevel = filter(lambda ask: float(ask['amount']) >= tradeQuantity, orderBook['asks'])

                    if len(lowestSellPriceLevel) > 0:
                        price = float(lowestSellPriceLevel[0]['price'])
                    else:
                        continue
                    
                    # if price >= counterPrice:
                    #     print 'gemini trade not profitable'
                    #     tradeProfitable = False
                    #     continue

                if tradeDetails['action'] == 'sell':
                    
                    highestBuyPriceLevel = filter(lambda bid: float(bid['amount']) >= tradeQuantity, orderBook['bids'])

                    if len(highestBuyPriceLevel) > 0:
                        price = float(highestBuyPriceLevel[0]['price'])
                    else:
                        continue
                    
                    # if price <= counterPrice:
                    #     print 'gemini trade not profitable'
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

                if 'order_id' not in orderResults:
                    print 'gemini order could not be submitted'
                    continue

                if 'original_amount' in orderResults:
                    print 'order was sucessfully placed on gemini'

                time.sleep(4)

                tradeStatus = self.orderStatus(orderResults['order_id'])

                if tradeStatus['executed_amount'] == tradeStatus['original_amount']:
                    print 'gemini order is complete'
                    tradeCompleted = True
                    finalOrderResults = orderResults
                else:
                    print 'canceling all orders on gemini'
                    self.cancelOrders()
                    tradeQuantity = float(tradeStatus['original_amount']) - float(tradeStatus['executed_amount'])
                    print 'new gemini trading quantity: ' + str(tradeQuantity)
                

            if tradeCompleted:
                    tradeSummary = self.orderHistory(finalOrderResults['order_id'])
                    finalTradeResults  = tradeSummary.copy()

                    finalTradeResults['action'] = tradeDetails['action']
                    geminiTradeResults.put([finalTradeResults])
                    return 
            elif not tradeProfitable:
                print tradeDetails['action'] + ' on gemini for ' + str(tradeDetails['quantity']) + ' ethereum at ' + str(price) + '/eth was unsuccesful - order book no longer profitable'
                sys.exit()

        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def executeMakerTrade(self, positionChange, geminiTradeResults):
        try:
            
            tradeDetails = positionChange['gemini']
            counterPrice = positionChange['gdax']['rate']

            tradeCompleted = False
            tradeProfitable = True

            finalOrderResults = None
            price = None
            tradeQuantity = tradeDetails['quantity']

            while not tradeCompleted and tradeProfitable:
                orderBook = self.getOrderBook()

                if tradeDetails['action'] == 'buy':
                    highestBuyPriceLevel = orderBook['bids'][0]
                    price = float(highestBuyPriceLevel['price'])
                
                    # if price >= counterPrice:
                    #     print 'trade not profitable'
                    #     tradeProfitable = False
                    #     continue

                if tradeDetails['action'] == 'sell':
                    lowestSellPriceLevel = orderBook['asks'][0]
                    price = float(lowestSellPriceLevel['price'])
                    
                    # if price <= counterPrice:
                    #     print 'trade not profitable'
                    #     tradeProfitable = False
                    #     continue

                print 'placing ' + tradeDetails['action'] + ' trade on Gemini for ' + str(tradeDetails['quantity']) + ' ethereum at ' + str(price) + '/eth'

                orderParams = {
                    'client_order_id': "20150102-4738721", 
                    'symbol': 'ethusd',       
                    'amount': tradeQuantity,        
                    'price': price,
                    'side': tradeDetails['action'],
                    'type': 'exchange limit',
                    'options': ["maker-or-cancel"] 
                }

                if orderParams['price'] < 100 or orderParams['price'] > 400:
                    print 'failed gemini price sanity check. price: ' + str(orderParams['price'])
                    sys.exit()

                orderResults = self.newOrder(orderParams)

                # -- check the order was successfully placed
                if 'order_id' not in orderResults:
                    print 'gemini order could not be submitted'
                    continue

                if 'original_amount' in orderResults:
                    print 'order was sucessfully placed on gemini...'

                # -- wait period of time for order to get filled
                

                priceLevelUnchanged = True
                # -- get current status of order
                while priceLevelUnchanged:
                    time.sleep(4)
                    print 'getting gemini trade status'
                    tradeStatus = self.orderStatus(orderResults['order_id'])

                    if tradeStatus['executed_amount'] == tradeStatus['original_amount']:
                        print 'order is complete'
                        tradeCompleted = True
                        finalOrderResults = orderResults
                        break
                    else:
                        orderBook = self.getOrderBook()

                        if tradeDetails['action'] == 'buy':
                            newPriceLevel = float(orderBook['bids'][0]['price'])
                                
                        if tradeDetails['action'] == 'sell':
                            newPriceLevel = float(orderBook['asks'][0]['price'])

                        if newPriceLevel == price:
                            print 'gemini price hasnt changed...'
                            continue
                        else:
                            print 'canceling all orders on gemini...'
                            self.cancelOrders()
                            tradeQuantity = float(tradeStatus['original_amount']) - float(tradeStatus['executed_amount'])
                            priceLevelUnchanged = False
                            print 'new gemini trading quantity: ' + str(tradeQuantity)
               
            if tradeCompleted:
                    tradeSummary = self.orderHistory(finalOrderResults['order_id'])
                    finalTradeResults  = tradeSummary.copy()

                    finalTradeResults['action'] = tradeDetails['action']
                    geminiTradeResults.put([finalTradeResults])
                    return 
            elif not tradeProfitable:
                print tradeDetails['action'] + ' on gemini for ' + str(tradeDetails['quantity']) + ' ethereum at ' + str(price) + '/eth was unsuccesful - order book no longer profitable'
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
        

