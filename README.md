# ETF Forecasting Dashboard

## Motivation
The goal of this project is to create an interactive dashboard for analyzing and forecasting changes in the Exchange Traded Fund (ETF) market, with the use of machine learning(ML). Visualizing fund performance for all ETFs at once is a valuable tool for analysts to easily identify trends based on sector/issuer. Combined with ML forecasting models for classifying price change direction as well as closing price prediction, the end product is one-stop shopping for beginner and expert investors alike.

## Data Sources

5 years of historical price data provided for free by [IEX](https://iextrading.com/developer/). View IEX’s [Terms of Use](https://iextrading.com/api-exhibit-a/). Additional fund information was obtained via Yahoo Finance, ETFdb.com and ETF.com. 

## Visualizations
Bloomberg's fantastic python library [bqplot](https://github.com/bloomberg/bqplot) enabled the creation of the ETF market map, shown below:
![MarketMap](https://github.com/cpease00/etf_forecasting/blob/master/data_science/finance/images/MarketMap.jpg "1-day returns for ETFs by sector")

Matplotlib was used for static graphs, and [Plotly](https://plot.ly/python/candlestick-charts/) was used for dynamic financial charts.
