from datetime import datetime

def convert_timestamp_to_datetime(timestamp):
    '''
    将给定的时间戳转换为 yyyy-MM-dd HH:mm:ss 格式的日期时间字符串。
    
    参数:
    timestamp (int): 待转换的时间戳，单位为毫秒。
    
    返回:
    str: 转换后的日期时间字符串。
    '''
    # 时间戳转换为datetime对象，注意这里需要除以1000，因为给定的是毫秒级时间戳
    dt_object = datetime.fromtimestamp(timestamp / 1000.0)
    # 使用strftime方法格式化日期时间
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time

if __name__ == '__main__':
    # 测试示例
    timestamp = 1714754684712
    formatted_time = convert_timestamp_to_datetime(timestamp)
    print(formatted_time)