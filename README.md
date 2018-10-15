# ETF Forecasting Dashboard

## Motivation
Exchange Traded Funds are rapidly replacing traditional investment stratgies like mutual funds. But with over a thousand ETFs to chose from, it can be daunting to decide which to buy. The goal of this project is to bring clarity via a Machine Learning driven dashboard for analyzing and forecasting changes in the Exchange Traded Fund (ETF) market. Visualizing fund performance for all ETFs at once is a valuable tool for to easily identify trends based on sector/issuer. Algorithmic classification models (Random Forest, SVM, Gradient Boosting) assist in predicting price change direction while a LSTM neural network produces price forecasts. The result is a helpful dashboard for anyone to make informed investment decisions.

## The Market Map
Bloomberg's fantastic python library [bqplot](https://github.com/bloomberg/bqplot) enabled the creation of the ETF market map shown below:
![MarketMap](https://github.com/cpease00/etf_forecasting/blob/master/data_science/finance/images/market.jpg "1-day returns for ETFs by sector")

Each box represents a different ETF, which when hovered over displays stats about that fund. The bold dividing lines between different sections of the map encompass different 'segments' or types of ETF. For example, large market capitalization ETFs are grouped together. The dropdown allows you to toggle between different options for what the colors represent. When 1 week returns is selected, for example, dark green corresponds to high-performing funds over that time period, while dark red means a drop in price. The scale on the bottom details exactly what the range of changes is for the chosen time period. 

## Data Sources
5 years of historical price data are provided for free by [IEX](https://iextrading.com/developer/). View IEX’s [Terms of Use](https://iextrading.com/api-exhibit-a/). There is no sign up or api key required, so anyone can pull the required data immediately. IEX Finanace provides open, close, high, low and volume for all ETFs, producing 5 years of historical pricing corresponding to about 1250 rows of data for each fund. This was merged with information such as assets under management, expense ratio and segment, obtained from Yahoo Finance, ETFdb.com and ETF.com.

The historical data is best viewed in the form of a candlestick chart, which displays daily price changes as well as the spread in prices thoughout the day. Plotly candlestick charts are interactive, and may be shifted to any desired range. 

![CandleStick](https://github.com/cpease00/etf_forecasting/blob/master/data_science/finance/images/candlestick.jpg "3 years of daily data")

## Feature Engineering/Technical indicators
Financial analysts use a number of technical indicators, which are quantities derived from various ratios of past prices in time-series data. I decided to include them in my analysis, particulary as they assisted in the task of classifying price direction. They are as follows:

• Exponentially Weighted Moving Average (EWMA): A rolling mean of the past closing price, which weights recent prices more than past. This is a good practice as recent price changes are more useful for predicting future ones. EWMA over periods of 7, 50, and 200 days were included in the training data.

• Moving Average Convergence Divergence (MACD): A momentum indicator which is used to identify trends over time. it is a function of the 12 and 26 day EWMAs.

• Relative Strength Index (RSI): A momentum oscillator which ranges from 0 to 100. Funds with over 70 or under 30 are traditionally identified as having strong momentum up or down. The RSI is calculated over a period of 14 days, and is a function of relative strength(RS), a ratio of exponentially smoothed moving averages of up and down periods during this time. 

• Lagged Profits: Price changes over the previous 1-5 day periods were also included in the inputs.

The resulting vectors for a given day is shown below:
![DataVectors](https://github.com/cpease00/etf_forecasting/blob/master/vectors.jpg "5 days of data")
Where the Clf_Target column represents to whether the price has gone up/remained constant(1) or gone down(0)

## Forecasting Methodology
### Classification
The initial approach was (for simplicity's sake) that of a binary classification (will an ETF's price go up or down?) applied to each individual fund. Scikit-learn enabled the training of Random Forest(RF) and Support Vector Machine(SVM) classifiers, and the XGBoost library was utilized for gradient boosted ensemble methods. 

The features described above were normalized using a MinMax scaler before being split into validation, test and train sets. A simple splitting function was created to ensure that all training data predates all validation data, and all validation data occurs before testing. The validation data was used to gague model performance during tuning, and testing data was only used once to assess performance. This separation is crucial, as the models

The Random Forest Classifier was trained first, with 100 estimators), which gave insight into the importance of the various features. RF is a useful tool for investigating how ensemble methods split a population at each node, and has the advantage of being easily interpretable. Following the RF, SVM and Logistic Regression models were trained, to investigate their performance on the same task. Finally, XGBoost achieved some of the best results, after tuning parameters using a GridSearch to find the optimal values for learning rate, max tree depth, and number of learners. It is important to note that all 4 classifiers were trained on data for each fund(1600+), and for XGB there were widely differing sets of parameters that performed best on this classification task. 

### Regression
Model performance was compared to a naive baseline model (assuming price remains the same as the previous day). For each fund analyzed, an ARIMA model is implemented using fbprophet and a LSTM Neural Network is trained using Keras to predict the following day's closing price. Inputs of the LSTM are (at the moment) limited to the five results obtained from iexfinance. A LSTM was chosen instead of a tradional neural network because it is better suited to deal with time-series data. A regular neural network does not retain past inputs, while a LSTM has a loop within each layer which allows previous inputs to perist in memory.

Matplotlib was used for static graphs, and [Plotly](https://plot.ly/python/candlestick-charts/) was used for dynamic financial charts and forecasts as shown below:

![Forecast](https://github.com/cpease00/etf_forecasting/blob/master/data_science/finance/images/forecast.jpg "LSTM predictions vs. Naive Model")

All of this was put together in a Jupyter Dashboard, with many more features yet to come!

## Further Imoprovements
One of the main weaknesses of this forecasting analysis is that it is wholly based on past pricing data. In order to increase sensitivity to state of the economy, statistics from the US Treasury can be included in the analysis. The following scatter matrix shows plots of each of the variables plotted against the other. 

![Scatter](https://github.com/cpease00/etf_forecasting/blob/master/scatter.jpg "Scatter Matrix of US Treasury Variables")
The top row here is useful for looking for relationships with the regression target which we are trying to predict. There are no strong correlations in the variables shown, but future features can be identified through these method, and Quandl has thousands available. It would also be beneficial to construct a relational database to store all these variables, historical prices, underlying stocks and data for each ETF. 

## Relevant Resources

[More on LSTMs](http://colah.github.io/posts/2015-08-Understanding-LSTMs/)

[Overview of Naive Methods](https://otexts.org/fpp2/simple-methods.html)

[Global State of ETFs 2017](https://www.ey.com/Publication/vwLUAssets/ey-global-etf-survey-2017/$FILE/ey-global-etf-survey-2017.pdf)
