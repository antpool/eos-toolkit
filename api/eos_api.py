from config.config import Config, HttpConfig
from utils import http
from utils.logger import logger

def_timeout = HttpConfig.default_time_out_sec()
def_api = Config.get_local_api()


def get_chain_info(url=def_api, timeout=def_timeout):
    success = False
    try:
        uri = "/v1/chain/get_info"
        url = url + uri
        result = http.get(uri, url, timeout=timeout)
        success = True
        msg = result.json()
    except Exception as e:
        msg = str(e)
        logger.error('Failed to call %s error:%s', url, msg)
    return success, msg


def server_version(url=def_api, timeout=def_timeout):
    success, result = get_chain_info(url, timeout)
    if success:
        return int(result['server_version'], 16)
    return 0


def get_producers(url=def_api, account=None, limit=21, timeout=def_timeout):
    uri = "/v1/chain/get_producers"
    url = url + uri
    data = """
    {
        "json":true,
        "limit":%s
    }
    """ % limit
    response = http.post(uri, url, data=data, timeout=timeout)
    if account is None:
        return response.json()['rows']
    rank = 0
    producer_info = None
    for producer in response.json()['rows']:
        rank = rank + 1
        if producer['owner'] == account:
            producer_info = producer
            producer_info['rank'] = rank
    return producer_info


def get_table_rows(table, scope='eosio', code='eosio', limit=1, lower_bound='',
                   url=def_api, timeout=def_timeout):
    uri = "/v1/chain/get_table_rows"
    url = url + uri
    data = """
    {
        "scope": "%s",
        "table": "%s",
        "code": "%s",
        "limit": %s,
        "lower_bound":"%s"
        "json": true
    }
    """ % (scope, table, code, limit, lower_bound)
    response = http.post(uri, url, data=data, timeout=timeout)
    return response.json()['rows']


def get_global_info(url=def_api, timeout=def_timeout):
    return get_table_rows('global', url=url, timeout=timeout)[0]


def get_currency_stats(url=def_api, symbol='EOS', code='eosio.token', timeout=def_timeout):
    uri = "/v1/chain/get_currency_stats"
    url = url + uri
    data = """
    {
        "symbol": "%s",
        "code": "%s"
    }
    """ % (symbol, code)
    response = http.post(uri, url, data=data, timeout=timeout)
    return response.json()[symbol]


def get_bindname_info(name, url=def_api, timeout=def_timeout):
    bid_info_list = get_table_rows('namebids', url=url, lower_bound=name, timeout=timeout)
    bid_info = bid_info_list[0]
    if name != bid_info['newname']:
        return None
    return bid_info


def get_ram_price(url=def_api, timeout=def_timeout):
    ram_info = get_table_rows('rammarket', url=url, timeout=timeout)
    ram = ram_info[0]
    quote_balance = float(ram['quote']['balance'].split(' ')[0])
    base_balance = float(ram['base']['balance'].split(' ')[0])
    return quote_balance / base_balance * 1024


def get_actions(account, pos=-1, offset=-50, url=def_api, timeout=def_timeout):
    uri = "/v1/history/get_actions"
    url = url + uri
    data = """
    {
        "account_name": "%s",
        "pos": %s,
        "offset": %s
    }
    """ % (account, pos, offset)
    return http.post('get_actions', url=url, data=data, timeout=timeout).json()['actions']


def get_block(block_num_or_id, url=def_api, timeout=def_timeout):
    uri = "/v1/chain/get_block"
    url = url + uri
    data = """
    {
        "block_num_or_id": "%s"
    }
    """ % (block_num_or_id)
    return http.post('get_block', url=url, data=data, timeout=timeout).json()
