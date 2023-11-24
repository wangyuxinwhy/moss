"""
plot tickers using yfinance and plotly.

Examples:
    >>> import stock_data
    >>> stock_data.plot_tickers(['AAPL', 'MSFT'], datetime(2021, 1, 1), datetime(2021, 6, 1))
    >>> stock_data.plot_tickers(['AAPL'], datetime(2021, 1, 1), datetime(2021, 6, 1))
    >>> stock_data.plot_tickers(['AAPL', 'MSFT'], datetime(2021, 1, 1), datetime(2021, 6, 1))
"""
from datetime import datetime
from typing import List

import plotly.graph_objs as go
import yfinance as yf


def plot_tickers(tickers: List[str], start_date: datetime, end_date: datetime) -> None:
    yf_tickers = [yf.Ticker(ticker) for ticker in tickers]
    if len(yf_tickers) == 1:
        stock_data = yf_tickers[0].history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
        ticker_name = yf_tickers[0].info['longName']
        trace = go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close'],
        )
        layout = go.Layout(title=f'{ticker_name} Prices - Last 1 Year', xaxis={'title': 'Date'}, yaxis={'title': 'Price (USD)'})
        fig = go.Figure(data=[trace], layout=layout)
        fig.show()
    else:
        fig = go.Figure()
        for ticker in yf_tickers:
            stock_data = ticker.history(start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))
            ticker_name = ticker.info['longName']
            fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name=ticker_name))
        fig.update_layout(
            title='Comparison of Stock Prices - Selected Date Range',
            xaxis_title='Date',
            yaxis_title='Stock Price (USD)',
            xaxis_rangeslider_visible=False,
        )
        fig.show()
