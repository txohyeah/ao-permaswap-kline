import streamlit as st
import plotly.graph_objs as go
from utils import mysql_utils
from plotly.subplots import make_subplots
from logger.exchange_logger import ExchangeLogger
import math


_db = mysql_utils.MySqlDb()
_exchange_config = {}
logger = ExchangeLogger("kline")


def init():
    results = _db.select("SELECT * FROM exchange_price_config WHERE del_flag = 0;")
    for result in results:
        _exchange_config[result['code']] = result
    logger.info(">>>>>>>>>>>>> finish init exchange config >>>>>>>>>>>>>>>>>")
    logger.info(_exchange_config)
    logger.info(">>>>>>>>>>>>> finish init exchange config >>>>>>>>>>>>>>>>>")


if not _exchange_config:
    init()
    
# 设置选择需要查看KLine的池 的选择框
exchange_code = st.selectbox('Pool', list(_exchange_config.keys()))
exchange_config_item = _exchange_config.get(exchange_code)

ratio = exchange_config_item.get("ratio")
ratio_dimension = math.log10(ratio)
dimension_x = exchange_config_item.get("dimension_x")
dimension_x_with_ratio = dimension_x + ratio_dimension
dimension_y = exchange_config_item.get("dimension_y")
sql = f'''
    SELECT
    id, 
    player_id, 
    x_amount / POW(10, {dimension_x_with_ratio}) x_amount, 
    ROUND({ratio} * (y_amount / POW(10, {dimension_y})) / (x_amount / POW(10, {dimension_x})), 3) y_ratio_amount,
    created_time, 
    sell_flag
    FROM {exchange_code}
    order by created_time desc;
'''
df = _db.select_as_pd(sql)

df['Open'] = df['y_ratio_amount']
df['Close'] = df['y_ratio_amount']
df['Volumn'] = df['x_amount']

# 按照日期分组并计算最高价 (High) 和 最低价 (Low)
daily_data = df.groupby(df['created_time'].dt.date).agg({
    'Open': 'last',
    'Close': 'first',
    'y_ratio_amount': ['min', 'max'],
    'Volumn': 'sum'
}).reset_index()

# 重命名列
# 注意这里需要保持多级索引的结构
daily_data.columns = ['Date', 'Open', 'Close', ('y_ratio_amount', 'min'), ('y_ratio_amount', 'max'), 'Volumn']

# 选择需要的列
daily_data = daily_data[['Date', 'Open', 'Close', ('y_ratio_amount', 'min'), ('y_ratio_amount', 'max'), 'Volumn']]

# 将多级索引扁平化
daily_data.columns = ['Date', 'Open', 'Close', 'Low', 'High', 'Volumn']

title_str = f'''Daily {ratio} {exchange_config_item.get('token_x')} to {exchange_config_item.get('token_y')} Price'''

# 创建 K 线图
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.15,
                    row_width=[0.2, 0.7], specs=[[{"type": "candlestick"}], [{"type": "bar"}]])

# 添加 K 线图
fig.add_trace(go.Candlestick(x=daily_data['Date'],
                            open=daily_data['Open'],
                            high=daily_data['High'],
                            low=daily_data['Low'],
                            close=daily_data['Close']), row=1, col=1)

# 添加成交量条形图
fig.add_trace(go.Bar(x=daily_data['Date'], y=daily_data['Volumn'], name="Volume"), row=2, col=1)

# 更新图表布局
fig.update_layout(height=600, title_text=title_str)

# 显示图表
st.plotly_chart(fig)