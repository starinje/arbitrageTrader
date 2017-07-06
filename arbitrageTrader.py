# main code
# need to import config and services
import time
from config import config
from services.gemini import geminiService
from services.gdax import gdaxService

geminiService  = geminiService()
gdaxService = gdaxService()

def main():
    
    try: 
        print '****************************************************'
        

        orderBookGdax = gdaxService.getOrderBook()
        orderBookGemini = geminiService.getOrderBook()

        print orderBookGdax
        print orderBookGemini

        # orderBooks = {
        #     'gdax': orderBookGdax,
        #     'gemini': orderBookGemini
        # }

        # positionChange = determinePositionChange()

        # if positionChange == 'none':
        #     return 
        
        # print '****************************NEW TRADE****************************' 

        # tradeResults = executeTrade(positionChange)

        # gdaxResults = tradeResults['gdax']
        # geminiResults = tradeResults['gemini']

        # buyValue = null
        # sellValue = null

        # if tradeResults['takeProfit'] == 'gdax':
        #     buyValue = (tradeResults[gemini][price]*tradeResults[gemini][amount]) - tradeResults[gemini][fee]
        #     sellValue = (tradeResults[gdax][price]*tradeResults[gdax][amount]) - tradeResults[gdax][fee]
        
        # if tradeResults['takeProfit'] == 'gemini'
        #     sellValue = (tradeResults[gemini][price]*tradeResults[gemini][amount] - tradeResults[gemini][fee]
        #     buyValue = (tradeResults[gdax][price]*tradeResults[gdax][amount]) - tradeResults[gdax][fee]

        # profit = (sellValue - buyValue) / buyValue

        # print "successful " + tradeResults[gdax][action] + "on Gdax for " + tradeResults[gdax][amount] + "ethereum at " + tradeResults[gdax][price] + "/eth, fee of " + tradeResults[gdax][fee]
        # print "successful " + tradeResults[gemini][action] + "on Gemini for " + tradeResults[gemini][amount] + "ethereum at " + tradeResults[gemini][price] + "/eth, fee of " + tradeResults[gemini][fee]

        # print "profit percentage: " + profit
        # determineCurrentEthereumPosition()
    except:
        print("Error:",sys.exc_info()[0],"occured.")
    finally: 
        time.sleep(config['timeDelta'])
        main()




main()



# TODO: Convert main loop below to python

# import GdaxService from './services/gdax'
# import GeminiService from './services/gemini'
# import logger from './services/logger.js'
# import heartbeatLogger from './services/heartbeatLogger.js'

# const gdaxService = new GdaxService({...config.gdax, logger, })
# const geminiService = new GeminiService({...config.gemini, logger})

# main()

# async function main(){

#   try {
   
#     heartbeatLogger.info('')
#     heartbeatLogger.info('****************************************************')

#     let orderBookGemini = await geminiService.getOrderBook()
#     let orderBookGdax = await gdaxService.getOrderBook()

#     let orderBooks = {
#       gdax: orderBookGdax,
#       gemini: orderBookGemini
#     }

#     let positionChange = await determinePositionChange(orderBooks)

#     if(positionChange == 'none'){
#       return 
#     }

#     logger.info('')
#     logger.info('NEW TRADE')
    
#     let tradeResults = await execute(positionChange)

#     let gdaxResults = tradeResults.gdax
#     let geminiResults = tradeResults.gemini

#     //check here for results from each exchage. If either is bad then process.exit and cancel all orders on both exchanges.

#     let buyValue
#     let sellValue

#     switch(tradeResults.takeProfit){
#       case 'gdax':
#         buyValue = (tradeResults.gemini.price*tradeResults.gemini.amount) - tradeResults.gemini.fee
#         sellValue = (tradeResults.gdax.price*tradeResults.gdax.amount) - tradeResults.gdax.fee
#         break
  
#       case 'gemini':
#         sellValue = (tradeResults.gemini.price*tradeResults.gemini.amount) - tradeResults.gemini.fee
#         buyValue = (tradeResults.gdax.price*tradeResults.gdax.amount) - tradeResults.gdax.fee
#         break
#     }
    
#     let profit = (sellValue - buyValue) / buyValue
    
#     logger.info(`successful ${tradeResults.gdax.action} on Gdax for ${tradeResults.gdax.amount} ethereum at $${tradeResults.gdax.price}/eth, fee of ${tradeResults.gdax.fee}`)
#     logger.info(`successful ${tradeResults.gemini.action} on Gemini for ${tradeResults.gemini.amount} ethereum at ${tradeResults.gemini.price}/eth, fee of ${tradeResults.gemini.fee}`)
#     logger.info(`profit percentage: ${profit}`)
#     await determineCurrentEthereumPosition()
    
#   } catch(err){
#     heartbeatLogger.info(`error: ${err}`)
#     logger.info(`error: ${err}`)
#     // geminiService.cancelOrders()
#     // gdaxService.cancelOrders()
#     // process.exit()
#   } finally{
#     await Promise.delay(config.timeDelta)
#     main()
#   }

# }


# def determinePositionChange(orderBooks):


# async function determinePositionChange(orderBooks){

#   const ethereumTradingQuantity = config.ethereumTradingQuantity
#   const takeProfitTradeThreshold = config.takeProfitTradeThreshold
#   const swapFundsTradeThreshold = config.swapFundsTradeThreshold

#   let bidPriceGemini = calculateBidPrice(orderBooks.gemini.bids, ethereumTradingQuantity)
#   let bidPriceGdax = calculateBidPrice(orderBooks.gdax.bids, ethereumTradingQuantity)
#   let askPriceGemini = calculateAskPrice(orderBooks.gemini.asks, ethereumTradingQuantity)
#   let askPriceGdax = calculateAskPrice(orderBooks.gdax.asks, ethereumTradingQuantity)

#   const transactionPercentageGemini = config.transactionPercentageGemini
#   const transactionPercentageGdax = config.transactionPercentageGdax

#   const gdaxBasePercentageDifference = ((bidPriceGdax - askPriceGemini)/askPriceGemini)*100
#   const geminiBasePercentageDifference = ((bidPriceGemini - askPriceGdax)/askPriceGdax)*100

#   const gdaxRateIsHigherAndProfitable = gdaxBasePercentageDifference > takeProfitTradeThreshold
#   const geminiRateIsSwappable = geminiBasePercentageDifference > swapFundsTradeThreshold

#   let positionChange
#   let estimatedTransactionFees
#   let estimatedGrossProfit
#   let estimatedNetProfit

#   heartbeatLogger.info(``)
#   heartbeatLogger.info(`Sell on Gemini for ${bidPriceGemini}`)
#   heartbeatLogger.info(`Buy on Gdax for ${askPriceGdax}`)
#   heartbeatLogger.info(`Percent Difference: ${geminiBasePercentageDifference}`)

#   heartbeatLogger.info(``)
#   heartbeatLogger.info(`Sell on Gdax for ${bidPriceGdax}`)
#   heartbeatLogger.info(`Buy on Gemini for ${askPriceGemini}`)
#   heartbeatLogger.info(`Percent Difference: ${gdaxBasePercentageDifference}`)
  
 
#   if(gdaxRateIsHigherAndProfitable){

#     logger.info(`bidPriceGemini: ${bidPriceGemini}`)
#     logger.info(`bidPriceGdax: ${bidPriceGdax}`)
#     logger.info(`askPriceGemini: ${askPriceGemini}`)
#     logger.info(`askPriceGdax: ${askPriceGdax}`)

#     logger.info(`gdaxBasePercentageDifference: ${gdaxBasePercentageDifference}`)
#     logger.info(`geminiBasePercentageDifference: ${geminiBasePercentageDifference}`)

#     logger.info('gdax rate is higher and profitable')

#     let totalSaleValue = bidPriceGdax*ethereumTradingQuantity
#     let totalPurchaseCost = askPriceGemini*ethereumTradingQuantity
#     estimatedGrossProfit = totalSaleValue-totalPurchaseCost
#     estimatedTransactionFees = ((transactionPercentageGdax/100)*totalSaleValue) + ((transactionPercentageGemini/100)*totalPurchaseCost)
#     estimatedNetProfit = estimatedGrossProfit - estimatedTransactionFees
    
#     logger.info(`estimated total sale value: ${totalSaleValue}`)
#     logger.info(`estimated total purchase cost: ${totalPurchaseCost}`)
#     logger.info(`estimated gross profit: ${estimatedGrossProfit}`)
#     logger.info(`estimated transaction fees: ${estimatedTransactionFees}`)
#     logger.info(`estimated net profit: ${estimatedNetProfit}`)

#     positionChange = {
#       takeProfit: 'gdax',
#       gdax : {
#         action: 'sell',
#         quantity: ethereumTradingQuantity,
#         units: 'eth',
#         rate: bidPriceGdax
#       },
#       gemini: {
#         action: 'buy',
#         quantity: ethereumTradingQuantity,
#         units: 'eth',
#         rate: askPriceGemini
#       }
#     }
#   } else if (geminiRateIsSwappable) {
#     logger.info(`bidPriceGemini: ${bidPriceGemini}`)
#     logger.info(`bidPriceGdax: ${bidPriceGdax}`)
#     logger.info(`askPriceGemini: ${askPriceGemini}`)
#     logger.info(`askPriceGdax: ${askPriceGdax}`)

#     logger.info(`gdaxBasePercentageDifference: ${gdaxBasePercentageDifference}`)
#     logger.info(`geminiBasePercentageDifference: ${geminiBasePercentageDifference}`)
#     logger.info('Gemini rate is higher and profitable')

#     let totalSaleValue = bidPriceGemini*ethereumTradingQuantity
#     let totalPurchaseCost = askPriceGdax*ethereumTradingQuantity
#     estimatedGrossProfit = totalSaleValue-totalPurchaseCost
#     estimatedTransactionFees = ((transactionPercentageGemini/100)*totalSaleValue) + ((transactionPercentageGdax/100)*totalPurchaseCost)
#     estimatedNetProfit = estimatedGrossProfit - estimatedTransactionFees
    
#     logger.info(`estimated total sale value: ${totalSaleValue}`)
#     logger.info(`estimated total purchase cost: ${totalPurchaseCost}`)
#     logger.info(`estimated gross profit: ${estimatedGrossProfit}`)
#     logger.info(`estimated transaction fees: ${estimatedTransactionFees}`)
#     logger.info(`estimated net profit: ${estimatedNetProfit}`)

#     positionChange= {
#       takeProfit: 'gemini',
#       gemini: {
#         action: 'sell',
#         quantity: ethereumTradingQuantity,
#         units: 'eth',
#         rate: bidPriceGemini
#       },
#       gdax : {
#         action: 'buy',
#         quantity: ethereumTradingQuantity,
#         units: 'eth',
#         rate: askPriceGdax
#       }
#     }
#   } else {
#     positionChange = 'none'
#     return positionChange
#   }

#   let exchangeWithEthereumBalance = await determineCurrentEthereumPosition()

#   if(exchangeWithEthereumBalance == 'either'){
#     return positionChange
#   } else if(positionChange[exchangeWithEthereumBalance].action == 'sell'){
#     return positionChange
#   } else {
#     return 'none'
#   }
# }

# def execute(positionChange):
# async function execute(positionChange){

#   let tradeResults = await Promise.all([gdaxService.executeTrade(positionChange), geminiService.executeTrade(positionChange)])
#   //let tradeResults = await Promise.all([gdaxService.executeTrade(positionChange)])

#   let tradeLog = {
#     gdax: tradeResults[0],
#     gemini: tradeResults[1],
#     takeProfit: positionChange.takeProfit
#   }

#   return tradeLog
# }

# def determineCurrentEthereumPosition():
# async function determineCurrentEthereumPosition(){

#   // determine gemini ethereum balance
#   let currentGeminiBalances = await geminiService.availableBalances()
  
#   let geminiUsdBalance = currentGeminiBalances.filter(accountDetails => accountDetails.currency == 'USD')
#   geminiUsdBalance = parseFloat(geminiUsdBalance[0].amount)

#   let geminiEthBalance = currentGeminiBalances.filter(accountDetails => accountDetails.currency == 'ETH')
#   geminiEthBalance = parseFloat(geminiEthBalance[0].amount)

#   // determine gdax ethereum balance
#   let currentGdaxBalances = await gdaxService.availableBalances()
  
#   let gdaxUsdBalance = currentGdaxBalances.filter((accountDetails) => accountDetails.currency == 'USD')
#   gdaxUsdBalance = parseFloat(gdaxUsdBalance[0].balance)

#   let gdaxEthBalance = currentGdaxBalances.filter((accountDetails) => accountDetails.currency == 'ETH')
#   gdaxEthBalance = parseFloat(gdaxEthBalance[0].balance)

#   logger.info(`geminiEthBalance: ${geminiEthBalance}`)
#   logger.info(`geminiUsdBalance: ${geminiUsdBalance}`)
#   logger.info(`gdaxEthBalance: ${gdaxEthBalance}`)
#   logger.info(`gdaxUsdBalance: ${gdaxUsdBalance}`)

#   const ethereumTradingQuantity = config.ethereumTradingQuantity
#   let ethereumBalance


#   if(geminiEthBalance >= ethereumTradingQuantity && gdaxEthBalance >= ethereumTradingQuantity){
#       ethereumBalance = 'either'
#   } else if(geminiEthBalance >= gdaxEthBalance){
#     ethereumBalance = 'gemini'
#   } else if(gdaxEthBalance >= geminiEthBalance){
#     ethereumBalance = 'gdax'
#   }

#   // if(geminiEthBalance > gdaxEthBalance){
#   //   ethereumBalance = 'gemini'
#   // } else if (gdaxEthBalance > geminiEthBalance){
#   //   ethereumBalance = 'gdax'
#   // }

#   logger.info(`ethereum balance is in ${ethereumBalance}`)

#   return ethereumBalance
# }


# def calculateBidPrice(bids, ethereumTradingQuantity):

# function calculateBidPrice(bids, ethereumTradingQuantity){

#   let priceLevel = bids.find((bid) => {
#     return parseFloat(bid.amount) >= ethereumTradingQuantity
#   })
#   //let priceLevel = bids[0]

#   return priceLevel ? parseFloat(priceLevel.price) : 'no match found'
# }

# def calculateAskPrice(asks, ethereumTradingQuantity):
# function calculateAskPrice(asks, ethereumTradingQuantity){

#   let priceLevel = asks.find((ask) => {
#     return parseFloat(ask.amount) >= ethereumTradingQuantity
#   })
#   //let priceLevel = asks[0]

#   return priceLevel ? parseFloat(priceLevel.price) : 'no match found'
# }



