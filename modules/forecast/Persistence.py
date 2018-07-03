from pandas import DataFrame
from pandas import concat
from pandas import read_csv
from pandas import datetime
import pandas as pd
from sklearn.metrics import mean_squared_error
from math import sqrt
from matplotlib import pyplot


# date-time parsing function for loading the dataset
def parser(x):
    return datetime.strptime('19' + x, '%Y-%m')


# convert time series into supervised learning problem
def series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


# transform series into train and test sets for supervised learning
def prepare_data(series, n_test, n_lag, n_seq):
    # extract raw values
    raw_values = series.values
    raw_values = raw_values.reshape(len(raw_values), 1)
    # transform into supervised learning problem X, y
    supervised = series_to_supervised(raw_values, n_lag, n_seq)
    supervised_values = supervised.values
    # split into train and test sets
    train, test = supervised_values[0:-n_test], supervised_values[-n_test:]
    return train, test


# make a persistence forecast
def persistence(last_ob, n_seq):
    return [last_ob for i in range(n_seq)]


# evaluate the persistence model
def make_forecasts(train, test, n_lag, n_seq):
    forecasts = list()
    for i in range(len(test)):
        X, y = test[i, 0:n_lag], test[i, n_lag:]
        # make forecast
        forecast = persistence(X[-1], n_seq)
        # store the forecast
        forecasts.append(forecast)
    return forecasts


# evaluate the RMSE for each forecast time step
def evaluate_forecasts(test, forecasts, n_lag, n_seq):
    for i in range(n_seq):
        actual = test[:, (n_lag + i)]
        predicted = [forecast[i] for forecast in forecasts]
        rmse = sqrt(mean_squared_error(actual, predicted))
        print('t+%d RMSE: %f' % ((i + 1), rmse))


# plot the forecasts in the context of the original dataset
def plot_forecasts(series, forecasts, n_test, n_lag=1, n_seq=1):
    # plot the entire dataset in blue
    pyplot.plot(series.values)
    # plot the forecasts in red
    for i in range(len(forecasts)):
        off_s = len(series) - n_lag - n_seq + 1 - n_test + i
        off_e = off_s + len(forecasts[i]) + 1
        xaxis = [x for x in range(off_s, off_e)]
        print(series.values[off_s])
        yaxis = [series.values[off_s]] + forecasts[i]
        print(yaxis)
        pyplot.plot(xaxis, yaxis, color='red')
    # show the plot
    pyplot.show()


# load dataset
def get_data_frame(dir):
    df = pd.read_csv(dir)
    df = df.rename(columns={'ef_date': 'date'})
    df.index = pd.to_datetime(df.date, format='%Y%m%d')
    del df['date']
    return df


data_frame = get_data_frame('./data/1.csv')
# preprocess data
new_df = data_frame['2013-08-01':'2017-12-15']
idx = pd.date_range('2013-08-01', '2017-12-15')
new_df = new_df.reindex(idx).interpolate()
# configure
n_lag = 1
n_seq = 4
n_test = 30
# prepare data
train, test = prepare_data(new_df, n_test, n_lag, n_seq)
# make forecasts
forecasts = make_forecasts(train, test, n_lag, n_seq)
# evaluate forecasts
evaluate_forecasts(test, forecasts, n_lag, n_seq)
# plot forecasts
plot_forecasts(new_df, forecasts, n_test, n_lag, n_seq)
