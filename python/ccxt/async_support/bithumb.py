# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange

# -----------------------------------------------------------------------------

try:
    basestring  # Python 3
except NameError:
    basestring = str  # Python 2
import base64
import hashlib
import json
from ccxt.base.errors import ExchangeError


class bithumb (Exchange):

    def describe(self):
        return self.deep_extend(super(bithumb, self).describe(), {
            'id': 'bithumb',
            'name': 'Bithumb',
            'countries': 'KR',  # South Korea
            'rateLimit': 500,
            'has': {
                'CORS': True,
                'fetchTickers': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30597177-ea800172-9d5e-11e7-804c-b9d4fa9b56b0.jpg',
                'api': {
                    'public': 'https://api.bithumb.com/public',
                    'private': 'https://api.bithumb.com',
                },
                'www': 'https://www.bithumb.com',
                'doc': 'https://www.bithumb.com/u1/US127',
            },
            'api': {
                'public': {
                    'get': [
                        'ticker/{currency}',
                        'ticker/all',
                        'orderbook/{currency}',
                        'orderbook/all',
                        'transaction_history/{currency}',
                        'transaction_history/all',
                    ],
                },
                'private': {
                    'post': [
                        'info/account',
                        'info/balance',
                        'info/wallet_address',
                        'info/ticker',
                        'info/orders',
                        'info/user_transactions',
                        'trade/place',
                        'info/order_detail',
                        'trade/cancel',
                        'trade/btc_withdrawal',
                        'trade/krw_deposit',
                        'trade/krw_withdrawal',
                        'trade/market_buy',
                        'trade/market_sell',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'maker': 0.15 / 100,
                    'taker': 0.15 / 100,
                },
            },
            'exceptions': {
                '5100': ExchangeError,  # {"status":"5100","message":"After May 23th, recent_transactions is no longer, hence users will not be able to connect to recent_transactions"}
            },
        })

    async def fetch_markets(self):
        markets = await self.publicGetTickerAll()
        currencies = list(markets['data'].keys())
        result = []
        for i in range(0, len(currencies)):
            id = currencies[i]
            if id != 'date':
                market = markets['data'][id]
                base = id
                quote = 'KRW'
                symbol = id + '/' + quote
                result.append({
                    'id': id,
                    'symbol': symbol,
                    'base': base,
                    'quote': quote,
                    'info': market,
                    'lot': None,
                    'active': True,
                    'precision': {
                        'amount': None,
                        'price': None,
                    },
                    'limits': {
                        'amount': {
                            'min': None,
                            'max': None,
                        },
                        'price': {
                            'min': None,
                            'max': None,
                        },
                        'cost': {
                            'min': None,
                            'max': None,
                        },
                    },
                })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privatePostInfoBalance(self.extend({
            'currency': 'ALL',
        }, params))
        result = {'info': response}
        balances = response['data']
        currencies = list(self.currencies.keys())
        for i in range(0, len(currencies)):
            currency = currencies[i]
            account = self.account()
            lowercase = currency.lower()
            account['total'] = self.safe_float(balances, 'total_' + lowercase)
            account['used'] = self.safe_float(balances, 'in_use_' + lowercase)
            account['free'] = self.safe_float(balances, 'available_' + lowercase)
            result[currency] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'currency': market['base'],
        }
        if limit is not None:
            request['count'] = limit  # max = 50
        response = await self.publicGetOrderbookCurrency(self.extend(request, params))
        orderbook = response['data']
        timestamp = int(orderbook['timestamp'])
        return self.parse_order_book(orderbook, timestamp, 'bids', 'asks', 'price', 'quantity')

    def parse_ticker(self, ticker, market=None):
        timestamp = int(ticker['date'])
        symbol = None
        if market:
            symbol = market['symbol']
        open = self.safe_float(ticker, 'opening_price')
        close = self.safe_float(ticker, 'closing_price')
        change = close - open
        vwap = self.safe_float(ticker, 'average_price')
        baseVolume = self.safe_float(ticker, 'volume_1day')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'max_price'),
            'low': self.safe_float(ticker, 'min_price'),
            'bid': self.safe_float(ticker, 'buy_price'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'sell_price'),
            'askVolume': None,
            'vwap': vwap,
            'open': open,
            'close': close,
            'last': close,
            'previousClose': None,
            'change': change,
            'percentage': change / open * 100,
            'average': self.sum(open, close) / 2,
            'baseVolume': baseVolume,
            'quoteVolume': baseVolume * vwap,
            'info': ticker,
        }

    async def fetch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        response = await self.publicGetTickerAll(params)
        result = {}
        timestamp = response['data']['date']
        tickers = self.omit(response['data'], 'date')
        ids = list(tickers.keys())
        for i in range(0, len(ids)):
            id = ids[i]
            symbol = id
            market = None
            if id in self.markets_by_id:
                market = self.markets_by_id[id]
                symbol = market['symbol']
            ticker = tickers[id]
            ticker['date'] = timestamp
            result[symbol] = self.parse_ticker(ticker, market)
        return result

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetTickerCurrency(self.extend({
            'currency': market['base'],
        }, params))
        return self.parse_ticker(response['data'], market)

    def parse_trade(self, trade, market):
        # a workaround for their bug in date format, hours are not 0-padded
        transaction_date, transaction_time = trade['transaction_date'].split(' ')
        if len(transaction_time) < 8:
            transaction_time = '0' + transaction_time
        timestamp = self.parse8601(transaction_date + ' ' + transaction_time)
        timestamp -= 9 * 3600000  # they report UTC + 9 hours(server in list(Korean timezone.keys()))
        side = 'sell' if (trade['type'] == 'ask') else 'buy'
        return {
            'id': None,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'order': None,
            'type': None,
            'side': side,
            'price': self.safe_float(trade, 'price'),
            'amount': self.safe_float(trade, 'units_traded'),
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetTransactionHistoryCurrency(self.extend({
            'currency': market['base'],
            'count': 100,  # max = 100
        }, params))
        return self.parse_trades(response['data'], market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = None
        method = 'privatePostTrade'
        if type == 'limit':
            request = {
                'order_currency': market['id'],
                'Payment_currency': market['quote'],
                'units': amount,
                'price': price,
                'type': 'bid' if (side == 'buy') else 'ask',
            }
            method += 'Place'
        elif type == 'market':
            request = {
                'currency': market['id'],
                'units': amount,
            }
            method += 'Market' + self.capitalize(side)
        response = await getattr(self, method)(self.extend(request, params))
        id = None
        if 'order_id' in response:
            if response['order_id']:
                id = str(response['order_id'])
        return {
            'info': response,
            'id': id,
        }

    async def cancel_order(self, id, symbol=None, params={}):
        side_in_params = ('side' in list(params.keys()))
        if not side_in_params:
            raise ExchangeError(self.id + ' cancelOrder requires a side parameter(sell or buy) and a currency parameter')
        currency = ('currency' in list(params.keys()))
        if not currency:
            raise ExchangeError(self.id + ' cancelOrder requires a currency parameter')
        side = 'bid' if (params['side'] == 'buy') else 'ask'
        return await self.privatePostTradeCancel({
            'order_id': id,
            'type': side,
            'currency': params['currency'],
        })

    async def withdraw(self, currency, amount, address, tag=None, params={}):
        self.check_address(address)
        request = {
            'units': amount,
            'address': address,
            'currency': currency,
        }
        if currency == 'XRP' or currency == 'XMR':
            destination = ('destination' in list(params.keys()))
            if not destination:
                raise ExchangeError(self.id + ' ' + currency + ' withdraw requires an extra destination param')
        response = await self.privatePostTradeBtcWithdrawal(self.extend(request, params))
        return {
            'info': response,
            'id': None,
        }

    def nonce(self):
        return self.milliseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        endpoint = '/' + self.implode_params(path, params)
        url = self.urls['api'][api] + endpoint
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            body = self.urlencode(self.extend({
                'endpoint': endpoint,
            }, query))
            nonce = str(self.nonce())
            auth = endpoint + '\0' + body + '\0' + nonce
            signature = self.hmac(self.encode(auth), self.encode(self.secret), hashlib.sha512)
            signature64 = self.decode(base64.b64encode(self.encode(signature)))
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Api-Key': self.apiKey,
                'Api-Sign': str(signature64),
                'Api-Nonce': nonce,
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, httpCode, reason, url, method, headers, body):
        if not isinstance(body, basestring):
            return  # fallback to default error handler
        if len(body) < 2:
            return  # fallback to default error handler
        if (body[0] == '{') or (body[0] == '['):
            response = json.loads(body)
            if 'status' in response:
                #
                #     {"status":"5100","message":"After May 23th, recent_transactions is no longer, hence users will not be able to connect to recent_transactions"}
                #
                status = self.safe_string(response, 'status')
                if status is not None:
                    if status == '0000':
                        return  # no error
                    feedback = self.id + ' ' + self.json(response)
                    exceptions = self.exceptions
                    if status in exceptions:
                        raise exceptions[status](feedback)
                    else:
                        raise ExchangeError(feedback)

    async def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = await self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] == '0000':
                return response
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response
