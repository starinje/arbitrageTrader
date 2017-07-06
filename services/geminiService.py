class geminiService:
    
    def __init__(self, options):
        self.options = options
        # self.publicClient = gdax.PublicClient()
        # self.authedClient = 
        # this.baseUrl = this.options.sandbox ? `https://api-public.sandbox.gdax.com` : `https://api.gdax.com`
        # this.publicClient = new Gdax.PublicClient('ETH-USD', this.baseUrl);
        # this.authedClient = new Gdax.AuthenticatedClient(
        #     this.options.key, this.options.secret, this.options.passphrase, this.baseUrl);
        # }

    def getOrderBook(self):
     
        return 'gemini order book'
    
    def executeTrade(positionChange, tradeResults):
        tradeResults[0] = 'someResults'
        return 