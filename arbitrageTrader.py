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

        orderBooks = {
            'gdax': orderBookGdax,
            'gemini': orderBookGemini
        }

        print orderBooks

        positionChange = determinePositionChange()

        if positionChange == 'none':
            return 
        
        print '****************************NEW TRADE****************************' 

        tradeResults = executeTrade(positionChange)

        gdaxResults = tradeResults['gdax']
        geminiResults = tradeResults['gemini']

        buyValue = null
        sellValue = null

        if tradeResults['takeProfit'] == 'gdax':
            buyValue = (tradeResults[gemini][price]*tradeResults[gemini][amount]) - tradeResults[gemini][fee]
            sellValue = (tradeResults[gdax][price]*tradeResults[gdax][amount]) - tradeResults[gdax][fee]
        
        if tradeResults['takeProfit'] == 'gemini'
            sellValue = (tradeResults[gemini][price]*tradeResults[gemini][amount] - tradeResults[gemini][fee]
            buyValue = (tradeResults[gdax][price]*tradeResults[gdax][amount]) - tradeResults[gdax][fee]

        profit = (sellValue - buyValue) / buyValue

        print "successful " + tradeResults[gdax][action] + "on Gdax for " + tradeResults[gdax][amount] + "ethereum at " + tradeResults[gdax][price] + "/eth, fee of " + tradeResults[gdax][fee]
        print "successful " + tradeResults[gemini][action] + "on Gemini for " + tradeResults[gemini][amount] + "ethereum at " + tradeResults[gemini][price] + "/eth, fee of " + tradeResults[gemini][fee]

        print "profit percentage: " + profit
        determineCurrentEthereumPosition()
    except:
        print("Error:",sys.exc_info()[0],"occured.")
    finally: 
        time.sleep(config['timeDelta'])
        main()

main()


def determinePositionChange(orderBooks):
    ethereumTradingQuantity = config['ethereumTradingQuantity']
    takeProfitTradeThreshold = config['takeProfitTradeThreshold']
    swapFundsTradeThreshold = config['swapFundsTradeThreshold']

    bidPriceGemini = calculateBidPrice(orderBooks['gemini']['bids'], ethereumTradingQuantity)
    bidPriceGdax = calculateBidPrice(orderBooks['gdax']['bids'], ethereumTradingQuantity)
    askPriceGemini = calculateAskPrice(orderBooks['gemini']['asks'], ethereumTradingQuantity)
    askPriceGdax = calculateAskPrice(orderBooks['gdax']['asks'], ethereumTradingQuantity)

    transactionPercentageGemini = config['transactionPercentageGemini']
    transactionPercentageGdax = config['transactionPercentageGdax']

    gdaxBasePercentageDifference = ((bidPriceGdax - askPriceGemini)/askPriceGemini)*100
    geminiBasePercentageDifference = ((bidPriceGemini - askPriceGdax)/askPriceGdax)*100

    gdaxRateIsHigherAndProfitable = gdaxBasePercentageDifference > takeProfitTradeThreshold
    geminiRateIsSwappable = geminiBasePercentageDifference > swapFundsTradeThreshold

    positionChange = null
    estimatedTransactionFees = null
    estimatedGrossProfit = null
    estimatedNetProfit = null

    print ''
    print "Sell on Gemini for " + bidPriceGemini
    print "Buy on Gdax for " + askPriceGdax
    print "Percent Difference: " + geminiBasePercentageDifference

    print ''
    print "Sell on Gdax for " + bidPriceGdax
    print "Buy on Gemini for " + askPriceGemini
    print "Percent Difference: " + gdaxBasePercentageDifference

    if gdaxRateIsHigherAndProfitable:

        print "bidPriceGemini: " + bidPriceGemini
        print "bidPriceGdax: " + bidPriceGdax
        print "askPriceGemini: " + askPriceGemini
        print "askPriceGdax: " + askPriceGdax
    
        print "gdaxBasePercentageDifference: " + gdaxBasePercentageDifference
        print "geminiBasePercentageDifference: " + geminiBasePercentageDifference

        print "gdax rate is higher and profitable"

        totalSaleValue = bidPriceGdax*ethereumTradingQuantity
        totalPurchaseCost = askPriceGemini*ethereumTradingQuantity
        estimatedGrossProfit = totalSaleValue-totalPurchaseCost
        estimatedTransactionFees = ((transactionPercentageGdax/100)*totalSaleValue) + ((transactionPercentageGemini/100)*totalPurchaseCost)
        estimatedNetProfit = estimatedGrossProfit - estimatedTransactionFees
        
        print "estimated total sale value: " + totalSaleValue
        print "estimated total purchase cost: " + totalPurchaseCost
        print "estimated gross profit: " + estimatedGrossProfit
        print "estimated transaction fees: " + estimatedTransactionFees
        print "estimated net profit: " + estimatedNetProfit
      

        positionChange = {
            'takeProfit': 'gdax',
            'gdax' : {
                'action': 'sell',
                'quantity': ethereumTradingQuantity,
                'units': 'eth',
                'rate': bidPriceGdax
            },
            'gemini': {
                'action': 'buy',
                'quantity': ethereumTradingQuantity,
                'units': 'eth',
                'rate': askPriceGemini
            }
        }
    elif geminiRateIsSwappable:
        print "bidPriceGemini: " + bidPriceGemini
        print "bidPriceGdax: " + bidPriceGdax
        print "askPriceGemini: " + askPriceGemini
        print "askPriceGdax: " + askPriceGdax

        print "gdaxBasePercentageDifference: " + gdaxBasePercentageDifference
        print "geminiBasePercentageDifference: " + geminiBasePercentageDifference
        print "gemini rate is higher and profitable"

        totalSaleValue = bidPriceGemini*ethereumTradingQuantity
        totalPurchaseCost = askPriceGdax*ethereumTradingQuantity
        estimatedGrossProfit = totalSaleValue-totalPurchaseCost
        estimatedTransactionFees = ((transactionPercentageGemini/100)*totalSaleValue) + ((transactionPercentageGdax/100)*totalPurchaseCost)
        estimatedNetProfit = estimatedGrossProfit - estimatedTransactionFees
        
        print "estimated total sale value: " + totalSaleValue
        print "estimated total purchase cost: " + totalPurchaseCost
        print "estimated gross profit: " + estimatedGrossProfit
        print "estimated transaction fees: " + estimatedTransactionFees
        print "estimated net profit: " + estimatedNetProfit

        positionChange= {
            'takeProfit' : 'gemini',
            'gemini' : {
                'action' : 'sell',
                'quantity' : ethereumTradingQuantity,
                'units' : 'eth',
                'rate' : bidPriceGemini
            },
            'gdax' : {
                'action' : 'buy',
                'quantity' : ethereumTradingQuantity,
                'units' : 'eth',
                'rate' : askPriceGdax
            }
        }
    else:
        positionChange = 'none'
        return positionChange
    
    exchangeWithEthereumBalance = determineCurrentEthereumPosition()

    if exchangeWithEthereumBalance == 'either':
        return positionChange
    elif positionChange[exchangeWithEthereumBalance][action] == 'sell':
        return positionChange
    else:
        return 'none'


def execute(positionChange):

    tradeResults = []
    jobs = []

    thread1 = threading.Thread(target=gdaxService.executeTrade(positionChange, tradeResults))
    thread2 = threading.Thread(target=geminiService.executeTrade(positionChange, tradeResults))

    jobs.append(thread1)
    jobs.append(thread2)

    for j in jobs:
        j.start()

    for j in jobs:
        j.join()

    # print "List processing complete."
    # let tradeResults = await Promise.all([gdaxService.executeTrade(positionChange), geminiService.executeTrade(positionChange)])
  
    tradeLog = {
        'gdax': tradeResults[0],
        'gemini': tradeResults[1],
        'takeProfit': positionChange['takeProfit']
    }

    return tradeLog

def determineCurrentEthereumPosition():

    currentGeminiBalances = geminiService.availableBalances()
  
    geminiUsdBalance = filter(lambda accountDetails: accountDetails['currency'] == 'USD', currentGeminiBalances)
    geminiUsdBalance = float(geminiUsdBalance[0]['amount'])

    geminiEthBalance = filter(lambda accountDetails: accountDetails['currency'] == 'ETH', currentGeminiBalances)
    geminiEthBalance = float(geminiEthBalance[0]['amount'])


    currentGdaxBalances = gdaxService.availableBalances()
  
    gdaxUsdBalance = filter(lambda accountDetails: accountDetails['currency'] == 'USD', currentGdaxBalances)
    gdaxUsdBalance = float(gdaxUsdBalance[0]['balance'])

    gdaxEthBalance = filter(lambda accountDetails: accountDetails['currency'] == 'ETH', currentGdaxBalances)
    gdaxEthBalance = float(gdaxEthBalance[0]['balance'])

    print "geminiEthBalance: " + geminiEthBalance
    print "geminiUsdBalance: " + geminiUsdBalance
    print "gdaxEthBalance: " + gdaxEthBalance
    print "gdaxUsdBalance: " + gdaxUsdBalance


    ethereumTradingQuantity = config['ethereumTradingQuantity']
    ethereumBalance = null

    if geminiEthBalance >= ethereumTradingQuantity and gdaxEthBalance >= ethereumTradingQuantity:
        ethereumBalance = 'either'
    elif geminiEthBalance >= gdaxEthBalance:
        ethereumBalance = 'gemini'
    elif gdaxEthBalance >= geminiEthBalance:
        ethereumBalance = 'gdax'
    
    print 'ethereum balance is in ' + ethereumBalance

    return ethereumBalance


def calculateBidPrice(bids, ethereumTradingQuantity):

    priceLevel = filter(lambda bid: bid['amount'] >= ethereumTradingQuantity, bids)

    if len(priceLevel) > 0:
        return float(priceLevel['price'])
    else:
        return 'no match found'
}


def calculateAskPrice(asks, ethereumTradingQuantity):

    priceLevel = filter(lambda ask: ask['amount'] >= ethereumTradingQuantity, asks)

    if len(priceLevel) > 0:
        return float(priceLevel['price'])
    else:
        return 'no match found'
}





