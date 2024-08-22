from logger.exchange_logger import ExchangeLogger
from utils.mysql_utils import MySqlDb
import ao
import ao.su_messages
from utils.datatime_utils import convert_timestamp_to_datetime
from datetime import datetime, timedelta
import time
import threading

_exchange_config = {}

def flatten(edges, exchange_pid, token_x_pid):
    data = []
    for edge in edges:
        msg = edge.node.message
        if msg.get_tagvalue("X-PS-Status") != "Swapped":
            continue

        player_id = msg.get_tagvalue("Recipient")
        if token_x_pid == msg.get_tagvalue("X-PS-TokenIn"):
            w_ar_amount = msg.get_tagvalue("Quantity")
            llama_amount = msg.get_tagvalue("X-PS-AmountIn")
            sell_flag = 1
        else:
            llama_amount = msg.get_tagvalue("Quantity")
            w_ar_amount = msg.get_tagvalue("X-PS-AmountIn")
            sell_flag = 0
        created_time = convert_timestamp_to_datetime(int(edge.cursor))

        id = msg.id
        data.append((id, player_id, llama_amount, w_ar_amount, created_time, sell_flag))
    return data

def exchange_data_collection(logger: ExchangeLogger, exchange_pid: str, token_x_pid: str, start_time: datetime, end_time: datetime):
    has_next_page = True
    edges = []
    logger.info(str(start_time) + " " + str(end_time))
    start_timestamp = int(time.mktime(start_time.timetuple())) * 1000
    end_timestamp = int(time.mktime(end_time.timetuple())) * 1000
    while has_next_page:
        try:
            logger.info(exchange_pid + " " + str(start_timestamp) + " " + str(end_timestamp))

            json = ao.get_messages(exchange_pid, start_timestamp, end_timestamp)
            # print(json)
            su_msg = ao.su_messages.parse(json)
            edges.extend(su_msg.get_edges_via_tags("Action", "Debit-Notice"))
            has_next_page = su_msg.page_info.has_next_page
            # has_next_page = False
            start_timestamp = su_msg.get_latest_cursor()
            logger.info(f"has_next_page: {has_next_page}")
        except Exception as e:
            logger.info(f"grant_analysis error: {e}")
        
        time.sleep(5)

    return flatten(edges, exchange_pid, token_x_pid)

def fetch_data_once(logger: ExchangeLogger, db: MySqlDb, exchange_code: str, exchange_pid: str, token_x_pid: str, start_time, end_time):
    try:
        data_to_insert = exchange_data_collection(logger, exchange_pid, token_x_pid, start_time, end_time)
        db.insert('''
            REPLACE INTO ''' + exchange_code + ''' (
                id,
                player_id,
                x_amount,
                y_amount,
                created_time,
                sell_flag
            ) VALUES (%s, %s, %s, %s, %s, %s)
        ''', data_to_insert)
        time.sleep(5 * 60)
    except Exception as e:
        logger.error(e)
        logger.error("Unexpected error in fetch_data_once")

def fetch_data(logger: ExchangeLogger, db: MySqlDb, exchange_code: str, exchange_pid: str, token_x_pid: str):
    logger.info(f'exchange_code:{exchange_code}')
    count = db.count(f"SELECT COUNT(1) FROM {exchange_code}")
    if count == 0:
        sync_history(logger, db, exchange_code, exchange_pid, token_x_pid)

    while True:
        now = datetime.now()
        start_time = now - timedelta(minutes=24 * 60)
        end_time = now
        fetch_data_once(logger, db, exchange_code, exchange_pid, token_x_pid, start_time, end_time)

def sync_history(logger: ExchangeLogger, db: MySqlDb, exchange_code: str, exchange_pid: str, token_x_pid: str):
    logger.info(">>>>>>>>>>>>> start sync history exchange >>>>>>>>>>>>>>>>>")
    now = datetime.now()
    start_time = now - timedelta(days=400)
    end_time = now
    fetch_data_once(logger, db, exchange_code, exchange_pid, token_x_pid, start_time, end_time)
    logger.info(">>>>>>>>>>>>> finish sync history exchange >>>>>>>>>>>>>>>>>")

def init():
    logger = ExchangeLogger("init_exchange_data")
    db = MySqlDb(logger)
    results = db.select("SELECT * FROM exchange_price_config WHERE del_flag = 0;")
    for result in results:
        _exchange_config[result['code']] = result
    logger.info(">>>>>>>>>>>>> finish init exchange config >>>>>>>>>>>>>>>>>")
    logger.info(_exchange_config)
    logger.info(">>>>>>>>>>>>> finish init exchange config >>>>>>>>>>>>>>>>>")

def start_timer():
    for exchange_code, exchange_config in _exchange_config.items():
        logger = ExchangeLogger(exchange_code)
        db = MySqlDb(logger)
        logger.info(">>>>>>>>>>>>> start exchange data timer >>>>>>>>>>>>>>>>>")
        logger.info(exchange_config)
        logger.info(">>>>>>>>>>>>> start exchange data timer >>>>>>>>>>>>>>>>>")
        
        exchange_pid = exchange_config.get('process_id')
        token_x_pid = exchange_config.get('token_x_pid')
        
        thread_fetch_data = threading.Thread(
            target=fetch_data, args=(logger, db, exchange_code, exchange_pid, token_x_pid))
        thread_fetch_data.start()





if __name__ == '__main__':
    init()
    start_timer()