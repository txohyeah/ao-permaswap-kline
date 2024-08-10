import pymysql
import configparser
import hashlib
import pandas as pd

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取数据库配置
db_config = {
    'host': config.get('database', 'host'),
    'user': config.get('database', 'user'),
    'password': config.get('database', 'password'),
    'db': config.get('database', 'db'),
    'charset': config.get('database', 'charset')
}

def generate_unique_id(record):
    '''
    为给定的记录生成一个基于其内容的唯一ID。
    使用hashlib的sha256算法对记录的字符串表示进行哈希处理。
    
    参数:
    record (tuple): 数据记录元组
    
    返回:
    str: 基于记录内容计算出的唯一ID
    '''
    # 将记录转换为字符串并使用UTF-8编码
    record_str = '|'.join(str(item) for item in record).encode('utf-8')
    # 计算SHA-256哈希值
    hash_object = hashlib.sha256(record_str)
    # 获取哈希值的十六进制表示，并取前32位作为简化版的唯一ID
    unique_id = hash_object.hexdigest()[:32]
    return unique_id

class MySqlDb:

    def __init__(self):
        self.conn = pymysql.connect(**db_config)

    def insert(self, sql: str, data_to_insert: dict):
        try:
            cursor = self.conn.cursor()
            # 执行批量插入
            cursor.executemany(sql, data_to_insert)
            
            # 提交事务
            self.conn.commit()
            print(f'{cursor.rowcount} 条记录插入成功。')
        except pymysql.MySQLError as e:
            print(f'发生错误：{e}')

    def select(self, sql: str):
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            result = []
            for row in cursor.fetchall():
                result.append(dict(zip(columns, row)))
            return result
        
    def select_as_pd(self, sql: str):
        print(sql)
        data = pd.read_sql_query(sql, self.conn)
        return data
        
    def count(self, sql: str):
        print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            count_result = cursor.fetchone()[0]
            return count_result