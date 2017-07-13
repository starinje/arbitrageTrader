import time
import uuid
import base64
import hmac
import hashlib
import requests
import json
import sys

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
	return str(int(time.time()) * 1000)

def nonce_uuid():
	return uuid.uuid4().hex

class geminiService:

    def __init__(self, options):
        self.options = options
        subdomain = 'api.sandbox' if self.options['sandbox'] == True else 'api'
        self.baseUrl = 'https://' + subdomain + "." + 'gemini.com/v1'
        return 
        

    def requestPrivate(self, endpoint, params):
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

	def executeTrade(self):
		print('Inside executeTrade ...')

	def newOrder(self, params):
        try: 
            orderOptions = params.copy()
            orderOptions['client_order_id'] = 'someId'
            orderOptions['type'] = exchange limit'

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


	def orderHistory(self):
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


        #     executeTrade = async (positionChange) => {
        #         try{

        #             const tradeDetails = positionChange.gemini
        #             const counterPrice = positionChange.gdax.rate
        #             const rateDelta = Math.abs(positionChange.gdax.rate - positionChange.gemini.rate)

        #             let tradeCompleted = false
        #             let tradeProfitable = true

        #             let finalOrderResults
        #             let price
        #             let tradeQuantity = tradeDetails.quantity

        #             while(!tradeCompleted && tradeProfitable){
        #                 let orderBook = await this.getOrderBook()
                        
        #                 switch(tradeDetails.action){
        #                 case 'buy':
        #                     // let lowestSellPrice = parseFloat(orderBook.asks[0].price)
        #                     // price = lowestSellPrice - .01

        #                     // let highestBuyPrice = parseFloat(orderBook.bids[0].price)
        #                     // price = highestBuyPrice 

        #                     let lowestSellPriceLevel = orderBook.asks.find((ask) => {
        #                         return parseFloat(ask.amount) >= tradeQuantity
        #                     })

        #                     price = parseFloat(lowestSellPriceLevel.price)

        #                     if(price >= counterPrice){ //-(rateDelta/2)
        #                         tradeProfitable = false
        #                         continue
        #                     }
        #                     break
        #                 case 'sell':
        #                     // let highestBuyPrice = parseFloat(orderBook.bids[0].price)
        #                     // price = highestBuyPrice + .01

        #                     // let lowestSellPrice = parseFloat(orderBook.asks[0].price)
        #                     // price = lowestSellPrice

        #                     let highestBuyPriceLevel = orderBook.bids.find((ask) => {
        #                         return parseFloat(ask.amount) >= tradeQuantity
        #                     })

        #                     price = parseFloat(highestBuyPriceLevel.price)


        #                     if(price <= counterPrice){ //+(rateDelta/2)
        #                         tradeProfitable = false
        #                         continue
        #                     }
        #                     break
        #                 }

        #                 price = price.toFixed(2).toString()

        #                 this.logger.info(`placing ${tradeDetails.action} trade on Gemini for ${tradeDetails.quantity} ethereum at $${price}/eth`)
                    
        #                 let orderParams = { 
        #                     client_order_id: "20150102-4738721", 
        #                     symbol: 'ethusd',       
        #                     amount: tradeQuantity,        
        #                     price: price,
        #                     side: tradeDetails.action,
        #                     type: 'exchange limit',
        #                     //options: ['maker-or-cancel']
        #                 }

        #                 if(parseFloat(orderParams.price) < 200 || parseFloat(orderParams.price) > 400){
        #                     this.logger.info(`failed gemini price sanity check. price: ${orderParams.price} `)
        #                     process.exit()
        #                 }

        #                 let orderResults = await this.newOrder(orderParams)

        #                 if(orderResults.is_cancelled){
        #                     this.logger.info('gemini order could not be submitted')
        #                     this.logger.info(orderResults)
        #                     continue
        #                 }

        #                 await Promise.delay(1000)

        #                 let timeStart = moment.utc(new Date())
        #                 let timeExpired = false

        #                 this.logger.info(`gemini order entered - going into check status loop...`)
        #                 while(!timeExpired && !tradeCompleted){
        #                     await Promise.delay(1000)
        #                     let now = moment.utc(new Date())
        #                     let timeSinceTradePlaced = moment.duration(now.diff(timeStart))

        #                     let tradeStatus = await this.orderStatus(orderResults.order_id)
        #                     if(tradeStatus.executed_amount == tradeStatus.original_amount){
        #                         tradeCompleted = true
        #                         finalOrderResults = orderResults
        #                         continue
        #                     } else {
        #                         tradeQuantity = parseFloat(tradeStatus.original_amount) - parseFloat(tradeStatus.executed_amount)
        #                     }

        #                     if(timeSinceTradePlaced.asMinutes() > this.options.orderFillTime){
        #                         this.logger.info(`time has expired trying to ${tradeDetails.action} ${tradeDetails.quantity} ethereum on gemini at ${price}/eth, canceling order`)
        #                         await this.cancelOrders()
        #                         timeExpired = true
        #                     }
        #                 }
        #             }

        #             let tradeSummary

        #             if(tradeCompleted){
        #                 tradeSummary = await this.orderHistory(finalOrderResults.order_id)
        #                 return {...tradeSummary, action: tradeDetails.action}
        #             } else if(!tradeProfitable){
        #                 this.logger.info(`${tradeDetails.action} on gemini for ${tradeDetails.quantity} ethereum at ${price}/eth was unsuccesful - order book no longer profitable`)
        #                 process.exit()
        #             }
        #         } catch(err){
        #             return Promise.reject(`gemini executeTrade |> ${err}`)
        #         }
        #     }