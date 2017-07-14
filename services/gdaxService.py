import simplejson as json
import base64
import sys

class gdaxService:

    'https://api.gdax.com/products/ETH-USD/book?level=2',

    def __init__(self, options, gdaxLibrary):
        self.options = options
        subdomain = 'api'
        self.baseUrl = 'https://' + subdomain + "." + 'gdax.com'
        self.publicClient = gdaxLibrary.PublicClient()
        self.authedClient = gdaxLibrary.AuthenticatedClient(
            self.options['key'], 
            self.options['secret'], 
            self.options['passphrase'],
            self.baseUrl
        )
          
    def getOrderBook(self):
        try: 
            orderBook = self.publicClient.get_product_order_book('ETH-USD', level=2)
        
            bids = []
            asks = []

            for bidLevel in orderBook['bids']: 
                bid = {
                    'price': bidLevel[0],
                    'amount': bidLevel[1],
                }
                bids.append(bid)

            for askLevel in orderBook['asks']: 
                ask = {
                    'price': askLevel[0],
                    'amount': askLevel[1],
                }
                asks.append(ask)

            reformattedOrderBook = {
                'asks': asks,
                'bids': bids,
            }

            return reformattedOrderBook
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
        

    def availableBalances(self):
        try: 
            return self.authedClient.get_accounts()
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def orderStatus(self, orderId):
        try: 
            return self.authedClient.get_order(orderId)
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def cancelOrders(self):
        try: 
            return self.authedClient.cancel_all(product='ETH-USD')
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    def newOrder(self, params):
        try: 
            return self.authedClient[params['action']](price=params['price'], size=params['size'], product_id=params['productId'])
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
    
    def executeTrade(self, positionChange, gdaxTradeResults):
        try: 
            return 
            tradeDetails = positionChange['gdax']

            counterPrice = positionChange['gemini']['rate']

            tradeCompleted = False
            tradeProfitable = True

            finalOrderResults = None
            price = None
            tradeQuantity = tradeDetails['quantity']


            while not tradeCompleted & tradeProfitable:
                orderBook = self.getOrderBook()

                if tradeDetails['action'] == 'buy':
                    lowestSellPriceLevel = filter(lambda ask: float(ask['amount']) >= tradeQuantity, orderBook['asks'])

                    if len(lowestSellPriceLevel) > 0:
                        price = float(lowestSellPriceLevel[0]['price'])
                    else:
                        continue
                    
                    if price >= counterPrice:
                        tradeProfitable = False
                        continue

                if tradeDetails['action'] == 'sell':
                    highestBuyPriceLevel = filter(lambda bid: float(bid['amount']) >= tradeQuantity, orderBook['bids'])

                    if len(highestBuyPriceLevel) > 0:
                        price = float(highestBuyPriceLevel[0]['price'])
                    else:
                        continue
                    
                    if price <= counterPrice:
                        tradeProfitable = False
                        continue


                print 'placing' + tradeDetails['action'] + 'trade on Gdax for ' + str(tradeDetails['quantity']) + 'ethereum at ' + str(price) + '/eth'

                orderParams = {
                    'productId': 'ETH-USD',
                    'size': tradeQuantity,     
                    'price': price,
                    'action': tradeDetails['action']
                }


                if orderParams['price'] < 100 or orderParams['price'] > 400:
                    print 'failed gdax price sanity check. price: ' + str(orderParams['price'])
                    sys.exit()

                orderResults = self.newOrder(orderParams)

                if orderResults['is_cancelled']:
                    print 'gemini order could not be submitted'
                    print orderResults
                    continue

                time.sleep(2)

                while not tradeCompleted:
                    time.sleep(1)
                    tradeStatus = self.orderStatus(orderResults['id'])
                    if tradeStatus['filled_size'] == tradeStatus['size']:
                        tradeCompleted = true
                        finalOrderResults = orderResults
                        continue
                    else:
                        self.cancelOrders()
                        tradeQuantity = float(tradeStatus['size']) - float(tradeStatus['filled_size'])
                        continue

                if tradeCompleted:
                    finalTradeResults = {
                        'fee': float(finalOrderResults['fill_fees']),
                        'amount': float(finalOrderResults['size']),
                        'price': float(price),

                        'action': tradeDetails['action']
                    }

                    gdaxTradeResults = finalTradeResults
                    return 
                elif not tradeProfitable:
                    print tradeDetails['action'] + 'on gdax for ' + tradeDetails['quantity'] + 'ethereum at ' + price + '/eth was unsuccesful - order book no longer profitable'
                    sys.exit()

        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)