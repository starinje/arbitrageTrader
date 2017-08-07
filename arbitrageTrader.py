import time
from config import config
from services.geminiService import geminiService
from services.gdaxService import gdaxService
import gdax
import sys
import threading
from multiprocessing import Process, Queue
import logging

geminiService  = geminiService(config['gemini'])
gdaxService = gdaxService(config['gdax'], gdax)
logging.basicConfig(filename="logs.log", level=logging.INFO)

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

def determineExchangeBalances():
    try: 
        currentGeminiBalances = geminiService.availableBalances()
        print currentGeminiBalances

        geminiUsdBalance = filter(lambda accountDetails: accountDetails['currency'] == 'USD', currentGeminiBalances)

        geminiUsdBalance = float(geminiUsdBalance[0]['amount'])

        geminiEthBalance = filter(lambda accountDetails: accountDetails['currency'] == 'ETH', currentGeminiBalances)
        geminiEthBalance = float(geminiEthBalance[0]['amount'])

        currentGdaxBalances = gdaxService.availableBalances()
    
        gdaxUsdBalance = filter(lambda accountDetails: accountDetails['currency'] == 'USD', currentGdaxBalances)
        gdaxUsdBalance = float(gdaxUsdBalance[0]['balance'])

        gdaxEthBalance = filter(lambda accountDetails: accountDetails['currency'] == 'ETH', currentGdaxBalances)
        gdaxEthBalance = float(gdaxEthBalance[0]['balance'])

        exchangeBalances = {
            'gdax':{
                'usd': gdaxUsdBalance,
                'eth': gdaxEthBalance
            },
            'gemini':{
                'usd': geminiUsdBalance,
                'eth': geminiEthBalance
            }
        }

        return exchangeBalances

    except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

def determinePositionChange(orderBooks):
    try: 
        ethereumTradingQuantity = config['ethereumTradingQuantity']
        takeProfitTradeThreshold = config['takeProfitTradeThreshold']
        swapFundsTradeThreshold = config['swapFundsTradeThreshold']

        # below logic for taker scheme
        bidPriceGemini = calculateBidPrice(orderBooks['gemini']['bids'], ethereumTradingQuantity)
        bidPriceGdax = calculateBidPrice(orderBooks['gdax']['bids'], ethereumTradingQuantity)
        askPriceGemini = calculateAskPrice(orderBooks['gemini']['asks'], ethereumTradingQuantity)
        askPriceGdax = calculateAskPrice(orderBooks['gdax']['asks'], ethereumTradingQuantity)


        # below logic for maker-only scheme
        # bidPriceGemini = float(orderBooks['gemini']['bids'][0]['price'])
        # bidPriceGdax = float(orderBooks['gdax']['bids'][0]['price'])
        # askPriceGemini = float(orderBooks['gemini']['asks'][0]['price'])
        # askPriceGdax = float(orderBooks['gdax']['asks'][0]['price'])
   
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
        print 'OR'
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
    except Exception as e: 
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def execute(positionChange):
    try:

        processes = []
        gdaxTradeResults = Queue()
        geminiTradeResults = Queue()

        process1 = Process(target=gdaxService.executeTrade, args=(positionChange, gdaxTradeResults))
        process2 = Process(target=geminiService.executeTrade, args=(positionChange, geminiTradeResults))

        processes.append(process1)
        processes.append(process2)

        for p in processes:
            p.start()

        for p in processes:
            p.join()

        gdaxTradeResults = gdaxTradeResults.get()
        geminiTradeResults = geminiTradeResults.get()

        gdaxTradeResults = gdaxTradeResults[0]
        geminiTradeResults = geminiTradeResults[0]

        tradeLog = {
            'gdax': gdaxTradeResults,
            'gemini': geminiTradeResults,
            'takeProfit': positionChange['takeProfit']
        }

        return tradeLog
    except Exception as e: 
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


def isTradePossible(positionChange, ethereumTradingQuantity):
    try:
        exchangeBalances = determineExchangeBalances()

        if positionChange['takeProfit'] == 'gdax':
            enoughEth = exchangeBalances['gdax']['eth'] >= ethereumTradingQuantity
            enoughUsd = exchangeBalances['gemini']['usd'] > ethereumTradingQuantity*positionChange['gemini']['rate']*2
        elif positionChange['takeProfit'] == 'gemini':
            enoughEth = exchangeBalances['gemini']['eth'] >= ethereumTradingQuantity
            enoughUsd = exchangeBalances['gdax']['usd'] > ethereumTradingQuantity*positionChange['gdax']['rate']*2
        
        if enoughUsd and enoughEth:
            return True
        else:
            return False
       
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
            return 
        
        tradePossible = isTradePossible(positionChange, config['ethereumTradingQuantity'])

        if tradePossible:
            print 'trade is possible'
          
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

            print "successful " + tradeResults['gdax']['action'] + " on Gdax for " + str(tradeResults['gdax']['amount']) + " ethereum at " + str(tradeResults['gdax']['price']) + "/eth, fee of " + str(tradeResults['gdax']['fee'])
            print "successful " + tradeResults['gemini']['action'] + " on Gemini for " + str(tradeResults['gemini']['amount']) + " ethereum at " + str(tradeResults['gemini']['price']) + "/eth, fee of " + str(tradeResults['gemini']['fee'])
           
            logging.info(time.time())
            logging.info("successful " + tradeResults['gdax']['action'] + " on Gdax for " + str(tradeResults['gdax']['amount']) + " ethereum at " + str(tradeResults['gdax']['price']) + "/eth, fee of " + str(tradeResults['gdax']['fee']))
            logging.info("successful " + tradeResults['gemini']['action'] + " on Gemini for " + str(tradeResults['gemini']['amount']) + " ethereum at " + str(tradeResults['gemini']['price']) + "/eth, fee of " + str(tradeResults['gemini']['fee']))
            
            print "profit percentage: " + str(profit)
            exchangeBalances = determineExchangeBalances()
            totalUsd = exchangeBalances['gdax']['usd']+exchangeBalances['gemini']['usd']
            totalEth = exchangeBalances['gdax']['eth']+exchangeBalances['gemini']['eth']

            print 'total USD: ' + str(totalUsd)
            print 'total ETH: ' + str(totalEth)

            logging.info('total USD: ' + str(totalUsd))
            logging.info('total ETH: ' + str(totalEth))
        else:
            print 'trade is not possible'
            sys.exit()

    except Exception as e: 
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    finally: 
        time.sleep(config['timeDelta'])
        
while True:
    main()






