# ETF Forecasting Dashboard

## Motivation
The goal of this project is to create an interactive dashboard for analyzing and forecasting changes in the Exchange Traded Fund (ETF) market, with the use of machine learning(ML). Visualizing fund performance for all ETFs at once is a valuable tool for analysts to easily identify trends based on sector/issuer. Combined with ML forecasting models for classifying price change direction as well as closing price prediction, the end product is one-stop shopping for beginner and expert investors alike.

## Data Sources
5 years of historical price data provided for free by [IEX](https://iextrading.com/developer/). View IEX’s [Terms of Use](https://iextrading.com/api-exhibit-a/). 
Additional fund information was obtained from Yahoo Finance, ETFdb.com and ETF.com. 

## Methodology
### Classification
The initial approach was (for simplicity's sake) that of a binary classification (will an ETF's price go up or down?) applied to each individual fund. Scikit-learn enabled the training of Random Forest(RF) and Support Vector Machine(SVM) classifiers, and the XGBoost library was utilized for gradient boosted ensemble methods. 5 years of historical pricing corresponded to about 1250 rows of data for each fund, and input features included open, close, high, low, and volume traded. Additional technical indicators were produced, including RSI, MACD, ADX, Lagged returns, 7, 50 and 200 day exponentially weighted moving averages.

These inputs were normalized and split into validation, test and train sets before training the initial RF (with 100 estimators), which gave insight into the importance of the various features. SVM and Logistic Regression models were trained next, to investigate their performance on the same task. Finally, XGBoost achieved some of the best results, after tuning parameters using a GridSearch to find the optimal values for learning rate, max tree depth, and number of learners. 

### Regression

## Visualizations
Bloomberg's fantastic python library [bqplot](https://github.com/bloomberg/bqplot) enabled the creation of the ETF market map, shown below:
![MarketMap](https://github.com/cpease00/etf_forecasting/blob/master/data_science/finance/images/MarketMap.jpg "1-day returns for ETFs by sector")

Matplotlib was used for static graphs, and [Plotly](https://plot.ly/python/candlestick-charts/) was used for dynamic financial charts.

