from logger.exchange_logger import ExchangeLogger
from utils.mysql_utils import MySqlDb
from utils.datatime_utils import convert_timestamp_to_datetime
from datetime import datetime, timedelta
import time
import threading
from utils.ps_everpay_utils import get_orders

logger = ExchangeLogger("data_everpay_timer")
db = MySqlDb(logger)

def fetch_data(period, sleep_time):
    while True:
        orders = get_orders(logger, datetime.today(), '', period)
        print("fetch orders success.")

        # 遍历列表中的每个字典
        for item in orders:
            # 将时间戳从毫秒转换为秒
            timestamp_s = item['timestamp'] / 1000.0
            # 转换时间戳为 datetime 对象
            created_time = datetime.fromtimestamp(timestamp_s)
            # 添加 created_time 字段到字典
            item['created_time'] = created_time

        db.insert('''
            REPLACE INTO ps_everpay_exchange (
                id,
                address,
                ever_hash,
                token_in_tag,
                token_out_tag,
                token_in_amount,
                token_out_amount,
                price,
                status,
                timestamp
            ) VALUES (%(id)s, %(address)s, %(everHash)s, %(tokenInTag)s, %(tokenOutTag)s, %(tokenInAmount)s, %(tokenOutAmount)s, %(price)s, %(status)s, %(created_time)s)
        ''', orders)

        time.sleep(sleep_time)

def start_timer():
    thread_fetch_data = threading.Thread(
            target=fetch_data, args=(1, 5))
    thread_fetch_data.start()

if __name__ == '__main__':
    start_timer()