config = {
    'gemini': {
        'url': 'https://api.gemini.com/v1',
        'key': 'A2Vi33Da5ESehulxBYJD',
        # 'secret': '4Xgj1U5HrxgHB7bvVeTjftBzN2nK',
        # 'sandbox': false,
        'orderFillTime': 1
    },
    'gdax': {
        'url': 'https://api.gdax.com/products/ETH-USD/book?level=2',
        'sandbox': False,
        # 'key': 'debd5e0dc3ea74c87550a75d275c51bf',
        # 'secret': '0HrdzdopW5qnf74CgeErVN0HwwDcuYzs7M49cWcQ4FCAHY1TJuDQl48so7fvpa8Hwr6Co/+GhKeizMZsP8qZ8A==',
        # 'passphrase': 'if61ndcnzod',
        # 'usdAccountId': 'b878dae8-b114-4170-a5c7-a58446f1bf9a',
        # 'ethAcountId': '74153015-34f2-444f-8093-2aae38f3d164',
        'orderFillTime': 1
    },
    'ethereumTradingQuantity': 45,
    'takeProfitTradeThreshold': 1.4,
    'swapFundsTradeThreshold': 1.4,
    'timeDelta': 2,
    'transactionPercentageGemini': .3,
    'transactionPercentageGdax': .3
}