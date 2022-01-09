# -*- coding: utf-8 -*-

# -- Sheet --

from nomics import Nomics
import pandas as pd
from datetime import timezone
from datetime import datetime
import numpy as np
import altair as alt
import tensorflow as tf
from fbprophet import prophet
import matplotlib.pyplot as plt

import streamlit as st

key = st.secrets['nomics-key']['key']
nomics = Nomics(key)



"""
Functions included:

 - load_data: returns data in a standardized format
 - candlestick_chart: creates our candlestick chart
 - get_mape: i have no clue tbh
 - create_forecasting_chart: supposed to create  (you gessued it) a forecasting chart.
    currently doesn't work. not deployed.
 - volatility_chart: creates out volatility chart
 - percent_change: creates our percent change chart
 - rolling_avg_std: returns two charts. rolling average and stdev against time
 - reddit_posts_and_price: returns the reddit viz
 """



def load_data(df):

    #gets the 10 day real volatlilty variance swap and classical ways, and 10-day STD
    def getvol(df, window):
        df = df.sort_values(by=['Date'], ascending=True)
        df[str(window) + '-day STD'] = df['rate'].rolling(10).std()

        df['log_rtn'] = np.log(df['rate']).diff()

        ann_factor = 365/window
        window = window
        # Var Swap (returns are not demeaned)
        df[str(window) + 'real_var'] = np.square(df['log_rtn']).rolling(window).sum() * ann_factor
        df[str(window) + 'real_vol'] = np.sqrt(df[str(window) + 'real_var'])

        # Classical (returns are demeaned, dof=1)
        df[str(window) + 'real_var'] = df['log_rtn'].rolling(window).var() * ann_factor
        df[str(window) + 'real_vol'] = np.sqrt(df[str(window) + 'real_var'])
        df = df.sort_values(by=['Date'], ascending=False)
        return df

    df['rate'] = df['rate'].astype(float)
    df['close'] = df['rate'][1:].shift(-1)
    df['Date'] = pd.to_datetime(pd.to_datetime(df['timestamp']).dt.date)
    df = getvol(df, 10)
    df = df.rename(columns={'rate': 'open'})
    df['percent_change'] = (df['open'] - df['close']) / df['close']
    df['Low'] = df.loc[:,'open':'close'].min(axis=1)
    df['High'] = df.loc[:,'open':'close'].max(axis=1)
    df = df.fillna(method="pad")
    df = df.fillna(method="bfill")

    return df


def candlestick_chart(df):
    """

    Creates the Candle stick chart

    """
    open_close_color = alt.condition("datum.open <= datum.close",
                                    alt.value("#06982d"),
                                    alt.value("#ae1325"))

    base = alt.Chart(df).encode(
            alt.X('Date:T',
                axis=alt.Axis(
                    title='Date',
                    grid = False
                )
            ),
            color=open_close_color,
            tooltip=[alt.Tooltip('Date:T'), alt.Tooltip('open:Q', format='$'),
                    alt.Tooltip('close:Q', format='$')]
        )

    rule = base.mark_rule().encode(
            alt.Y(
                'Low:Q',
                title='Price',
                scale=alt.Scale(zero=False),
            ),
            alt.Y2('High:Q')
        )

    bar = base.mark_bar().encode(
            alt.Y('open:Q'),
            alt.Y2('close:Q')
        )

    all = rule + bar
    return all.properties(title='Price of Currency over Time', width=1500, height=400).interactive()


# Prophet Time series forcasting


def get_mape(actuals, forecasts):
    MAPE = np.mean(np.abs(forecasts - actuals) / (actuals))
    return MAPE


def create_forecasting_chart(df):

    #Forecasts coin data in prophet
    #takes in dataframe in form of pandas df
    #helper fcn to create_forecasting_chart
    def get_prophet_data(df):
        print(df)
        crypto_prophet = Prophet()
        experiment_df = pd.DataFrame({})
        experiment_df['ds'] = pd.to_datetime(df['timestamp']).dt.date
        experiment_df['y'] = df['close']
        train_data = experiment_df[pd.to_datetime(experiment_df['ds']) <= '2021-10-01']
        valid_data = experiment_df[pd.to_datetime(experiment_df['ds']) > '2021-10-01']
        # Fit the model on the time series.
        m_prophet = crypto_prophet.fit(train_data)
        # Create a DataFrame of future dates to create forecasts for
        future_prophet = crypto_prophet.make_future_dataframe(periods = 30)
        # Create forecast
        prophet_forecast = crypto_prophet.predict(future_prophet)
        #create data
        prophet_forecast['y'] = experiment_df['y']
        prophet_forecast['low'] = prophet_forecast.loc[:,'yhat':'y'].min(axis=1)
        prophet_forecast['high'] = prophet_forecast.loc[:,'yhat':'y'].max(axis=1)
        prophet_forecast['error'] = prophet_forecast['yhat_upper'] - prophet_forecast['yhat_lower']
        prophet_forecast['midpoint'] = prophet_forecast['low'] + abs((prophet_forecast['y'] - prophet_forecast['yhat']) / 2)
        return prophet_forecast
    prophet_forecast = get_prophet_data(df)
    difference = alt.condition("datum.yhat > datum.y",
                                      alt.value("#06982d"),
                                      alt.value("#ae1325"))
    diff2= alt.condition("datum.yhat > datum.y",
                                      alt.value("#06982d"),
                                      alt.value("#ae1325"))

    base = alt.Chart(prophet_forecast).encode(
      x=alt.X('ds:T', title='Date')

      )
    bar = base.mark_bar().encode(
      alt.Y('y:Q'),
      alt.Y2('yhat:Q'), color = difference)
    area = base.mark_area(opacity = 0.2, color='steelblue').encode(
      alt.Y('yhat_upper:Q'),
      alt.Y2('yhat_lower:Q'))

    line = base.mark_line(color='black').encode(
      alt.Y('midpoint:Q')
      )


    all = bar + area + line
    return all.properties(width=800, height=600).interactive()


def volatlilty_chart(df, vol):
    vol = alt.Chart(df).mark_line(tooltip=True).encode(
            x=alt.X('Date:T', title='Date', axis=alt.Axis( grid = False)),
            y=alt.Y(vol, title='Volatlilty', axis=alt.Axis(labels=True, tickSize=0))
            )

    price = alt.Chart(df).mark_area(opacity = 0.5, color='red').encode(
      alt.Y('open:Q', axis=alt.Axis(labelAngle=-45)))

    total = vol + price
    return total.properties(width=750, height=500).interactive()




def percent_change(df):
    chart = alt.Chart(df).mark_bar().encode(
        alt.X("Date:T"),
        alt.Y("percent_change:Q", title='Percentage Change'),
        color=alt.condition("datum.percent_change < 0",
                                    alt.value("#ae1325"),
                                    alt.value("#06982d")),
        tooltip= ['Date:T', 'percent_change']
    ).properties(height=500, width=750)

    return chart.properties(title='Percentage Change of Currency Over Time', width=750, height=500).interactive()

#percent_change(sample_df)

# Rolling avg and std chart:
def rolling_avg_std(df):
    chart1 = alt.Chart(df).mark_line().encode(
        alt.X("Date:T"),
        alt.Y("close:Q", title='Close'),
        tooltip= ['Date:T', 'close:Q']
    ).properties(height=500, width=750, title='Closing Price Over Time with Moving Average')

    moving_avg = alt.Chart(df).mark_line(
        color='red',
        size=3
    ).transform_window(
        rolling_mean='mean(close)'
    ).encode(
        x='Date:T',
        y='rolling_mean:Q',
        tooltip = ['Date:T','mean(close)']
    )

    chart2 = alt.Chart(df).mark_line().encode(
        alt.X("Date:T"),
        alt.Y("close:Q", title='Close'),
        tooltip= ['Date:T', 'close:Q']
    ).properties(height=500, width=750, title='Closing Price Volatility Based on Moving Standard Deviation')

    moving_std = alt.Chart(df).mark_line(
        color='lightblue',
        size=3
    ).transform_window(
        rolling_std='stdev(close)'
    ).encode(
        x='Date:T',
        y='rolling_std:Q',
        tooltip = ['Date:T', 'rolling_std:Q']
    )

    return (chart1 + moving_avg).interactive(), (chart2 + moving_std).interactive()



def reddit_posts_and_price(price, reddit, token):

    def load_reddit(df, token):
        red = df
        red['date'] = pd.to_datetime(red['datetime_hour']).dt.date #get the date
        red = red[red['ticker'] == token]
        red = red.groupby(by=['signal', 'date', 'ticker']).agg({'value_day': 'sum'}) #aggregate by day
        return red.filter(like='reddit_submission_num_posts', axis=0).reset_index() #filter to get submission numbers

    reddit = load_reddit(reddit, token)
    base1 = alt.Chart(price).encode(x=alt.X('Date:T', title='Date'))

    bar = base1.mark_bar(color = 'lightblue').encode(
        alt.Y('close:Q'))

    reddit['date'] = reddit['date'].astype(str)
    base2 = alt.Chart(reddit).encode(x=alt.X('date:T', title=''))

    line = base2.mark_line(color = 'red').encode(
        alt.Y('value_day:Q', title='Posts per day'))

    chart = alt.layer(bar, line).resolve_scale(y='independent').encode(
            tooltip=['Date:T', 'close:Q']
        )

    return chart.properties(height=500, title='Currency Price in Relation to Number of Reddit Posts Over Time. NOTE: Only YTD Data').interactive()




#Forecasts coin data in prophet
#takes in dataframe in form of pandas df
#creates Forecasting chart, calls get_prophet_data
#takes in df- dataframe
def create_forecasting_chart(df):

  #Forecasts coin data in prophet
  #takes in dataframe in form of pandas df
  #helper fcn to
     def get_prophet_data(df):
        crypto_prophet = Prophet()

        experiment_df = pd.DataFrame({})
        experiment_df['ds'] = pd.to_datetime(df['timestamp']).dt.date
        experiment_df['y'] = df['rate']
        train_data = experiment_df[pd.to_datetime(experiment_df['ds']) <= '2021-10-01']
        valid_data = experiment_df[pd.to_datetime(experiment_df['ds']) > '2021-10-01']

        # Fit the model on the time series.
        m_prophet = crypto_prophet.fit(train_data)

        # Create a DataFrame of future dates to create forecasts for.
        future_prophet = crypto_prophet.make_future_dataframe(periods = 30)

        # Create forecast
        prophet_forecast = crypto_prophet.predict(future_prophet)

        #create data
        prophet_forecast['y'] = experiment_df['y']
        prophet_forecast['low'] = prophet_forecast.loc[:,'yhat':'y'].min(axis=1)
        prophet_forecast['high'] = prophet_forecast.loc[:,'yhat':'y'].max(axis=1)
        prophet_forecast['error'] = prophet_forecast['yhat_upper'] - prophet_forecast['yhat_lower']
        prophet_forecast['midpoint'] = prophet_forecast['low'] + abs((prophet_forecast['y'] - prophet_forecast['yhat']) / 2)

        return prophet_forecast

    prophet_forecast = get_prophet_data(df)

    difference = alt.condition("datum.yhat > datum.y",
                                      alt.value("#06982d"),
                                      alt.value("#ae1325"))

    diff2= alt.condition("datum.yhat > datum.y",
                                      alt.value("#06982d"),
                                      alt.value("#ae1325"))

    base = alt.Chart(prophet_forecast).encode(
        x=alt.X('ds:T', title='Date')
      )


    bar = base.mark_bar().encode(
      alt.Y('y:Q'),
      alt.Y2('yhat:Q'), color = difference)

    area = base.mark_area(opacity = 0.2, color='steelblue').encode(
      alt.Y('yhat_upper:Q'),
      alt.Y2('yhat_lower:Q'))

    line = base.mark_line(color='black').encode(
      alt.Y('midpoint:Q')
    )


    all = bar + area + line
    return all.properties(width=750, height=500).interactive()
