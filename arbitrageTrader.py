import time
from config import config
from services.geminiService import geminiService
from services.gdaxService import gdaxService
import gdax
import sys
import threading

geminiService  = geminiService(config['gemini'])
gdaxService = gdaxService(config['gdax'], gdax)

def calculateBidPrice(bids, ethereumTradingQuantity):
    try:
        priceLevel = filter(lambda bid: float(bid['amount']) >= ethereumTradingQuantity, bids)
   
        if len(priceLevel) > 0:
            return float(priceLevel[0]['price'])
        else:
            return 'no match found'
    except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

def calculateAskPrice(asks, ethereumTradingQuantity):
    try: 
        priceLevel = filter(lambda ask: float(ask['amount']) >= ethereumTradingQuantity, asks)

        if len(priceLevel) > 0:
            return float(priceLevel[0]['price'])
        else:
            return 'no match found'
    except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

def determineCurrentEthereumPosition():
    try: 
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

        print "geminiEthBalance: " + str(geminiEthBalance)
        print "geminiUsdBalance: " + str(geminiUsdBalance)
        print "gdaxEthBalance: " + str(gdaxEthBalance)
        print "gdaxUsdBalance: " + str(gdaxUsdBalance)

        ethereumTradingQuantity = config['ethereumTradingQuantity']
        ethereumBalance = None

        if geminiEthBalance >= ethereumTradingQuantity and gdaxEthBalance >= ethereumTradingQuantity:
            ethereumBalance = 'either'
        elif geminiEthBalance >= gdaxEthBalance:
            ethereumBalance = 'gemini'
        elif gdaxEthBalance >= geminiEthBalance:
            ethereumBalance = 'gdax'
        
        print 'ethereum balance is in ' + ethereumBalance

        return ethereumBalance
    except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def determinePositionChange(orderBooks):
    try: 
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

        positionChange = None
        estimatedTransactionFees = None
        estimatedGrossProfit = None
        estimatedNetProfit = None

        print ''
        print "Sell on Gemini for " + str(bidPriceGemini)
        print "Buy on Gdax for " + str(askPriceGdax)
        print "Percent Difference: " + str(geminiBasePercentageDifference)

        print ''
        print "Sell on Gdax for " + str(bidPriceGdax)
        print "Buy on Gemini for " + str(askPriceGemini)
        print "Percent Difference: " + str(gdaxBasePercentageDifference)

        if gdaxRateIsHigherAndProfitable:
            print "gdax rate is higher and profitable"

            totalSaleValue = bidPriceGdax*ethereumTradingQuantity
            totalPurchaseCost = askPriceGemini*ethereumTradingQuantity
            estimatedGrossProfit = totalSaleValue-totalPurchaseCost
            estimatedTransactionFees = ((transactionPercentageGdax/100)*totalSaleValue) + ((transactionPercentageGemini/100)*totalPurchaseCost)
            estimatedNetProfit = estimatedGrossProfit - estimatedTransactionFees
            
            print "estimated total sale value: " + str(totalSaleValue)
            print "estimated total purchase cost: " + str(totalPurchaseCost)
            print "estimated gross profit: " + str(estimatedGrossProfit)
            print "estimated transaction fees: " + str(estimatedTransactionFees)
            print "estimated net profit: " + str(estimatedNetProfit)
        
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
            print "gemini rate is higher and profitable"

            totalSaleValue = bidPriceGemini*ethereumTradingQuantity
            totalPurchaseCost = askPriceGdax*ethereumTradingQuantity
            estimatedGrossProfit = totalSaleValue-totalPurchaseCost
            estimatedTransactionFees = ((transactionPercentageGemini/100)*totalSaleValue) + ((transactionPercentageGdax/100)*totalPurchaseCost)
            estimatedNetProfit = estimatedGrossProfit - estimatedTransactionFees
            
            print "estimated total sale value: " + str(totalSaleValue)
            print "estimated total purchase cost: " + str(totalPurchaseCost)
            print "estimated gross profit: " + str(estimatedGrossProfit)
            print "estimated transaction fees: " + str(estimatedTransactionFees)
            print "estimated net profit: " + str(estimatedNetProfit)

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
        elif positionChange[exchangeWithEthereumBalance]['action'] == 'sell':
            return positionChange
        else:
            return 'none'
    except Exception as e: 
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)



def execute(positionChange):
    try:

        print 'in execute function...'

        geminiTradeResults = None
        gdaxTradeResults = None
        jobs = []

        thread1 = threading.Thread(target=gdaxService.executeTrade(positionChange, gdaxTradeResults))
        thread2 = threading.Thread(target=geminiService.executeTrade(positionChange, geminiTradeResults))

        jobs.append(thread1)
        jobs.append(thread2)

        for j in jobs:
            j.start()

        for j in jobs:
            j.join()

        # print "List processing complete."
        # let tradeResults = await Promise.all([gdaxService.executeTrade(positionChange), geminiService.executeTrade(positionChange)])

        tradeLog = {
            'gdax': gdaxTradeResults,
            'gemini': geminiTradeResults,
            'takeProfit': positionChange['takeProfit']
        }

        return tradeLog
    except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

def main():
    
    try: 
        orderBookGdax = gdaxService.getOrderBook()
        orderBookGemini = geminiService.getOrderBook()

        orderBooks = {
            'gdax': orderBookGdax,
            'gemini': orderBookGemini
        }

        positionChange = determinePositionChange(orderBooks)
        

        if positionChange == 'none':
            print 'no trade opportunity'
            print ''
            return 
        
        tradeResults = execute(positionChange)

        gdaxResults = tradeResults['gdax']
        geminiResults = tradeResults['gemini']

        buyValue = None
        sellValue = None

        if tradeResults['takeProfit'] == 'gdax':
            buyValue = (tradeResults['gemini']['price']*tradeResults['gemini']['amount']) - tradeResults['gemini']['fee']
            sellValue = (tradeResults['gdax']['price']*tradeResults['gdax']['amount']) - tradeResults['gdax']['fee']
        
        if tradeResults['takeProfit'] == 'gemini':
            sellValue = (tradeResults['gemini']['price']*tradeResults['gemini']['amount']) - tradeResults['gemini']['fee']
            buyValue = (tradeResults['gdax']['price']*tradeResults['gdax']['amount']) - tradeResults['gdax']['fee']

        profit = (sellValue - buyValue) / buyValue

        print "successful " + tradeResults['gdax']['action'] + "on Gdax for " + tradeResults['gdax']['amount'] + "ethereum at " + tradeResults['gdax']['price'] + "/eth, fee of " + tradeResults['gdax']['fee']
        print "successful " + tradeResults['gemini']['action'] + "on Gemini for " + tradeResults['gemini']['amount'] + "ethereum at " + tradeResults['gemini']['price'] + "/eth, fee of " + tradeResults['gemini']['fee']

        print "profit percentage: " + profit
        determineCurrentEthereumPosition()
    except Exception as e: 
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    finally: 
        time.sleep(config['timeDelta'])
        main()

main()




