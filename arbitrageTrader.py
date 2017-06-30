# main code
print 'running arbitrage trader'  

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



