# ETF Forecasting Dashboard

## Motivation
The goal of this project is to create an interactive dashboard for analyzing and forecasting changes in the Exchange Traded Fund (ETF) market, with the use of machine learning(ML). Visualizing fund performance for all ETFs at once is a valuable tool for analysts to easily identify trends based on sector/issuer. Combined with ML forecasting models for classifying price change direction as well as closing price prediction, the end product is one-stop shopping for beginner and expert investors alike.

## Data Sources
5 years of historical price data provided for free by [IEX](https://iextrading.com/developer/). View IEX’s [Terms of Use](https://iextrading.com/api-exhibit-a/). 
Additional fund information was obtained from Yahoo Finance, ETFdb.com and ETF.com. 

IEX Finanace provides open, close, high, low and volume. 5 years of historical pricing corresponds to about 1250 rows of data for each fund. This was merged with information such as assets under management, expense ratio and segment to create the interactive market overview.

## Feature Engineering/Technical indicators
Financial analysts use a number of technical indicators, which are quantities derived from various ratios of past prices in time-series data. I decided to include them in my analysis, particulary as they assisted in the task of classifying price direction. They are as follows:

• Exponentially weighted moving average (EWMA): A rolling mean of the past closing price, which weight more recent prices more than the past. This is a good practice as recent price changes are more useful for predicting future ones. EWMA over periods of 7, 50, and 200 days were included in the training data.

• Moving Average Convergence Divergence (MACD): A momentum indicator which is used to identify trends over time. it is a function of the 12 and 26 day EWMAs.

• Relative Strength Index (RSI): A Momentum oscillator which ranges from 0 to 100. Funds with over 70 or under 30 are traditionally identified as having strong momentum up or down. The RSI is calculated over a period of 14 days, and is a function of relative strength, a ratio of exponentially smoothed moving averages of up and down periods during this time. 

• Lagged Profits: Price changes over the previous 1-5 day periods were also included in the inputs.

The resulting vectors for a given day is shown below:
![DataVectors](https://github.com/cpease00/etf_forecasting/blob/master/data_science/vectors.jpg "5 days of data")


## Methodology
### Classification
The initial approach was (for simplicity's sake) that of a binary classification (will an ETF's price go up or down?) applied to each individual fund. Scikit-learn enabled the training of Random Forest(RF) and Support Vector Machine(SVM) classifiers, and the XGBoost library was utilized for gradient boosted ensemble methods. 

The features described above were normalized using a MinMax scaler before being split into validation, test and train sets. A simple splitting function was created to ensure that all training data occurs before all validation data, and all validation before testing. The validation data was used to gague model performance during tuning, and testing data was only used once to assess performance.

The Random Forest Classifier was trained first, with 100 estimators), which gave insight into the importance of the various features. The RF is a useful tool for investigating how future ensemble methods will split a population at each node, and has the advantage of being easily interpretable. Following the RF, SVM and Logistic Regression models were trained next, to investigate their performance on the same task. Finally, XGBoost achieved some of the best results, after tuning parameters using a GridSearch to find the optimal values for learning rate, max tree depth, and number of learners. It is important to note that all 4 classifiers were trained on data for each fund(1600+), and for XGB there were widely differing sets of parameters that performed best on this classification task. 

### Regression
Model performance was compared to a naive baseline model (assuming price remains same as previous day). For each fund analyzed, an ARIMA model is implemented using fbprophet and a LSTM Neural Network is trained using Keras to predict the following day's closing price. Inputs of the LSTM are (at the moment) limited to the five results obtained from iexfinance.

The LSTM network is a recurrent neural network, which have loops in them that allow information to persist. 

## Visualizations
Bloomberg's fantastic python library [bqplot](https://github.com/bloomberg/bqplot) enabled the creation of the ETF market map, shown below:
![MarketMap](https://github.com/cpease00/etf_forecasting/blob/master/data_science/finance/images/MarketMap.jpg "1-day returns for ETFs by sector")

Matplotlib was used for static graphs, and [Plotly](https://plot.ly/python/candlestick-charts/) was used for dynamic financial charts, as well as forecasts shown below:

![CandleStick](https://github.com/cpease00/etf_forecasting/blob/master/data_science/finance/images/historical.jpg "3 years of daily data")
![Forecast](https://github.com/cpease00/etf_forecasting/blob/master/data_science/finance/images/forecast.jpg "LSTM predictions vs. Naive Model")

All of this was put together in a Jupyter Dashboard, with many more features to come!

## Further Imoprovements
One of the main weaknesses of this forecasting analysis is that it is wholly based on past pricing data. In order to increase sensitivity to state of the economy, statistics from the US Treasury can be included in the analysis. The following scatter matrix shows plots of each of the variables relative to each other. The top row is useful for looking for relationships with the regression target which we are trying to predict. There are no strong correlations, but future features can be identified through these methods.

![Scatter](https://github.com/cpease00/etf_forecasting/blob/master/data_science/scatter.jpg "Scatter Matrix of US Treasury Variables")

It would also be beneficial to construct a relational database to store historical prices as well as underlying stocks and data for each ETF.
