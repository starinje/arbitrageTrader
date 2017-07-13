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

    def availableBalances(self):
        try: 
            return self.authedClient.get_accounts()
        except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


#     executeTrade = async (positionChange) => {
#         try{

#             const tradeDetails = positionChange.gdax
#             const counterPrice = positionChange.gemini.rate
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
#                    // let highestBuyPrice = parseFloat(orderBook.bids[0].price)
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

#                 this.logger.info(`placing ${tradeDetails.action} trade on Gdax for ${tradeDetails.quantity} ethereum at $${price}/eth`)

#                 let orderParams = { 
#                     productId: 'ETH-USD',       
#                     size: tradeQuantity,        
#                     price: price,
#                     action: tradeDetails.action,
#                     //postOnly: true
#                 }

#                 if(parseFloat(orderParams.price) < 200 || parseFloat(orderParams.price) > 400){
#                     this.logger.info(`failed gdax price sanity check. price: ${orderParams.price} `)
#                     process.exit()
#                 }

#                 let orderResults = await this.newOrder(orderParams)
#                 orderResults = JSON.parse(orderResults.body)
                

#                 if(!(orderResults.hasOwnProperty('status')) || !(orderResults.status == 'pending')){
#                     this.logger.info('gdax order could not be submitted')
#                     this.logger.info(orderResults)
#                     continue
#                 }

#                 await Promise.delay(1000)

#                 let timeStart = moment.utc(new Date())
#                 let timeExpired = false

#                 this.logger.info(`gdax order entered - going into check status loop...`)
#                 while(!timeExpired && !tradeCompleted){
#                     await Promise.delay(1000)
#                     let now = moment.utc(new Date())
#                     let timeSinceTradePlaced = moment.duration(now.diff(timeStart))

#                     let tradeStatus = await this.orderStatus(orderResults.id)
#                     if(tradeStatus.filled_size == tradeStatus.size){
#                         tradeCompleted = true
#                         finalOrderResults = tradeStatus
#                         continue
#                     } else {
#                         tradeQuantity = parseFloat(tradeStatus.size) - parseFloat(tradeStatus.filled_size)
#                     }

#                     if(timeSinceTradePlaced.asMinutes() > this.options.orderFillTime){
#                         this.logger.info(`time has expired trying to ${tradeDetails.action} ${tradeDetails.quantity} ethereum on gdax at ${price}/eth, canceling order`)
#                         await this.cancelOrders()
#                         timeExpired = true
#                     }
#                 }
#             }

#             let tradeSummary

#             if(tradeCompleted){

#                 let tradeSummary = {
#                     fee: parseFloat(finalOrderResults.fill_fees),
#                     amount: parseFloat(finalOrderResults.size),
#                     price: parseFloat(price),
#                 }

#                 return {...tradeSummary, action: tradeDetails.action}
#             } else if(!tradeProfitable){
#                 this.logger.info(`${tradeDetails.action} on gdax for ${tradeDetails.quantity} ethereum at ${price}/eth was unsuccesful - order book no longer profitable`)
#                 process.exit()
#             }
#         } catch(err){
#             return Promise.reject(`gdax executeTrade |> ${err}`)
#         }
#     }

#     newOrder = async (params = {}) => {
#         try {
#             return new Promise((resolve, reject) => {

#                 const reformattedParams = {
#                     price: params.price,
#                     size: params.size,
#                     product_id: params.productId,
#                     post_only: params.postOnly,
#                 }

#                 this.authedClient[params.action](reformattedParams, (err, results, data) => {
#                     return resolve(results)
#                 })
#             })
#         } catch(err){
#             return Promise.reject(`gdax newOrder Error: ${err}`)
            
#         }
#     }

#     cancelOrders = async () => {
#         try {
#             return new Promise((resolve, reject) => {
#                 this.authedClient.cancelAllOrders( (err, results, data) => {
#                     return resolve(results)
#                 })
#             })
#         } catch(err){
#             return Promise.reject(`gdax cancelOrders Error: ${err}`)
            
#         }
#     }


    
#     availableBalances = async () => {
#         try {
#             return new Promise((resolve, reject) => {
#                 this.authedClient.getAccounts((err, results, data) => {
#                     return resolve(data)
#                 })
#             })
           
#         } catch(err){
#             return Promise.reject(`gdax accounts |> ${err}`)
#         }
#     }

#     orderStatus = (orderId) => {
#         try {  
#            return new Promise((resolve, reject) => {
#                this.authedClient.getOrder(orderId, (err, results, data) => {
#                    return resolve(data)
#                });
#             })
#         } catch(err){
#             return Promise.reject(`gdax orderStatus |> ${err}`)
#         }
#     }
# }