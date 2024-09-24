import streamlit as st
import plotly.graph_objs as go
import math
from utils import mysql_utils
from plotly.subplots import make_subplots
from logger.exchange_logger import ExchangeLogger
from utils.ps_everpay_utils import get_kline, symbol_to_tag, process_orders


logger = ExchangeLogger("kline")
_db = mysql_utils.MySqlDb(logger)
_exchange_config = {}


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

if exchange_config_item.get("data_from") == "AO":
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
elif exchange_config_item.get("data_from") == "everpay":
    period = 'D'
    token = exchange_config_item.get('code')
    token_tag = symbol_to_tag[token]
    sql = f'''
        SELECT 
            ever_hash,
            address,
            token_in_tag, 
            token_out_tag, 
            token_in_amount, 
            token_out_amount, 
            price, 
            timestamp 
        from ps_everpay_exchange 
        WHERE 
        (
            token_in_tag = '{token_tag}' 
            OR 
            token_out_tag = '{token_tag}'
        )
        AND timestamp > NOW() - INTERVAL 100 DAY
        ORDER BY timestamp DESC;
    '''
    org_orders = _db.select(sql)

    orders = process_orders(org_orders)
    kline = get_kline(orders, token, period)

    trace = go.Candlestick(x=kline.index,
                        open=kline['price']['first'],
                        high=kline['price']['max'],
                        low=kline['price']['min'],
                        close=kline['price']['last'])

    fig = make_subplots(rows=2,
        cols=1,
        row_heights=[0.8, 0.2],
        shared_xaxes=True,
        vertical_spacing=0.02)

    fig.add_trace(trace, row=1, col=1)
    fig.add_trace(go.Bar(x=kline.index, y=kline['volume']['sum'], marker=dict(color='green')),
                row=2,
                col=1)

    fig.update_layout(title = token.upper()+'/USD Klines',
        yaxis1_title = 'Price (usd)',
        yaxis2_title = 'Volume (usd)',
        xaxis2_title = 'Time',
        xaxis1_rangeslider_visible = False,
        xaxis2_rangeslider_visible = False,
        yaxis2_showgrid = False,
        showlegend=False
    )
    st.plotly_chart(fig)