import streamlit as st
import pandas as pd
from datetime import timezone
from datetime import datetime
import numpy as np
import altair as alt
import streamlit.components.v1 as components
from PIL import Image




# loads in datasets, filepath is loc of file, token is capped at 3 letters
day_signals = pd.read_csv("ada_signals_day.csv")
hour_signals = pd.read_csv("ada_signals_hour.csv")
usd = pd.read_csv("ADA-USD.csv")
day_signals = pd.read_csv("data_for_viz_project.csv")
img = Image.open("cryptoreview_logo.jpg")
ADA_data = pd.read_csv("ADA-USD.csv")

def pre_processing(df, token, long):
    if long:
        df['Change'] = df['Open'] - df['Adj Close']
        df['Max Close'] = df['Close'].max()
        df['Mean Close'] = df['Close'].mean()
        df['percent_change'] = (df['Adj Close'] - df['Open']) / df['Adj Close']
        df['token'] = token
    else:
        df[token + '_Change'] = df['Open'] - df['Adj Close']
        df[token + '_Max_Close'] = df['Close'].max()
        df[token + '_Mean_Close'] = df['Close'].mean()
        df[token + '_percent_change'] = (df['Adj Close'] - df['Open']) / df['Adj Close']
        df[token + '_Open'] = df['Open']
        df[token + '_Close'] = df['Close']
        df[token + '_Adj Close'] = df['Adj Close']
        df[token + '_high'] = df['High']
        df[token + '_Low'] = df['Low']
        df[token + '_Volume'] = df['Volume']
        df = df.drop(['Open', 'Close', 'Adj Close', 'High', 'Low', 'Volume', 'token'], axis=1)
    return df

#joins data in a "wide" form, adding new columnes for each additional token
def load_wide_data(df, existing_df):
    final_df = existing_df.merge(df, how="inner", on="Date")
    return final_df

#concats columns in a SQL-Union style join
def concatenator(df_list):
    union_df = pd.concat(df_list)
    return union_df

ada_df = pd.read_csv('ADA-USD.csv')
eth_df = pd.read_csv('ETH-USD.csv')
btc_df = pd.read_csv('BTC-USD.csv')
xrp_df = pd.read_csv('XRP-USD.csv')
trx_df = pd.read_csv('TRX-USD.csv')
doge_df = pd.read_csv('DOGE-USD.csv')
ltc_df = pd.read_csv('LTC-USD.csv')
bch_df = pd.read_csv('BCH-USD.csv')
vnq_df = pd.read_csv('VNQ.csv')
spy_df = pd.read_csv('SPY.csv')

dfs = [ada_df, eth_df, btc_df, xrp_df, trx_df, doge_df, ltc_df, bch_df, vnq_df, spy_df]
tokens = ['ADA', 'ETH','BTC', 'XRP', 'TRX', 'DOGE', 'LTC', 'BCH', 'VNQ', 'SPY']

final_union_df = pre_processing(ada_df.copy(), 'ADA', True)
label_list = ['All'] + list(final_union_df['token'].unique())
all_prices_df = pd.DataFrame(ada_df['Date'])



for i, df in enumerate(dfs):
    final_union_df = concatenator([pre_processing(df, tokens[i], True), final_union_df])
    all_prices_df = load_wide_data(pre_processing(df, tokens[i], False), all_prices_df)

st.title("Crypto Dashboard")
st.subheader("Mickey Piekarski, Varun Dashora, Noor Gill, Marcus Manos")

st.sidebar.image(img, use_column_width=True)

st.sidebar.write("Send us some [feedback](https://docs.google.com/forms/d/e/1FAIpQLSeW1-wPirsWOBxF8VSJUxIGd1bM9BnT55cX5EXK6atmzAO3Hw/viewform?usp=sf_link)!")

option = st.selectbox(\
    'Which coin would you like to view', ['Aave','BinanceCoin','Bitcoin','Cardano','ChainLink','Cosmos','Dogecoin','EOS'])

'You selected: ', option

option1 = st.selectbox(\
    'Date range (years)', [0.5,1,2,3,4,5])
'You selected: ', option1


coin = option
trial = 'coins/coin_'+coin+'.csv'
df = pd.read_csv(trial)
df = df.tail(int(364 * option1))

def display_chart_0():
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['date_MDY'], empty='none')
    line = alt.Chart().mark_line(interpolate='basis').encode(
        alt.X('Date:T', axis=alt.Axis(title='Date')),
        alt.Y('Close:Q', axis=alt.Axis(title='Price (in USD)',format='$f')),
        # color='Cryptocurrency Choice:N'
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = alt.Chart().mark_point().encode(
        x='Date:T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    # Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    # Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=alt.condition(nearest, 'Close:Q', alt.value(' '))
    )

    # Draw a rule at the location of the selection
    rules = alt.Chart().mark_rule(color='gray').encode(
        x='Date:T',
    ).transform_filter(
        nearest
    )

    chart = alt.layer(line, selectors, points, rules, text,
                           data=df,
                           width=800, height=400,title= coin +' Price History')
    st.altair_chart(chart)

# EXPERIMENTING (alternative representation of price per currency)
# Create a selection that chooses the nearest point & selects based on x-value
def display_chart_1():
    alt.data_transformers.disable_max_rows()
    corr_matrix = all_prices_df.corr().reset_index().melt('index')
    base = alt.Chart(corr_matrix).transform_filter(
        alt.datum.index < alt.datum.variable
    ).encode(
        x='index',
        y='variable',
    ).properties(
        width=alt.Step(50),
        height=alt.Step(50)
    )

    rects = base.mark_rect().encode(
        color='value'
    )

    text = base.mark_text(
        size=18
    ).encode(
        text=alt.Text('value', format=".2f"),
        color=alt.condition(
            "datum.value > 0.5",
            alt.value('white'),
            alt.value('black')
        )
    )

    st.altair_chart(rects + text) # CHART MARKER (1)

def display_chart_2():
    label_list = ['All'] + list(final_union_df['token'].unique())

    input_dropdown1 = alt.binding_select(options=[None] + list(final_union_df['token'].unique()), labels=label_list)
    token_selector = alt.selection_single(name='Currency: ', fields=['token'], bind=input_dropdown1)
    #brush = alt.selection(type='interval')

    open_close_color = alt.condition("datum.Open <= datum.Close",
                                     alt.value("#06982d"),
                                     alt.value("#ae1325"))

    #scales = alt.selection_interval(bind='scales')


    base = alt.Chart(final_union_df).encode(
        alt.X('Date:T', 
              axis=alt.Axis(
                  format='%m/%d',
                  labelAngle=-45,
                  title='Date'
              )
        ),
        color=open_close_color, 
        tooltip=[alt.Tooltip('Date:T', format='%m/%d'), alt.Tooltip('Open:Q', format='$'), 
                 alt.Tooltip('Close:Q', format='$'), alt.Tooltip('Volume:Q', format='$'),
                 alt.Tooltip('token:O')]
    )
    #

    rule = base.mark_rule().encode(
        alt.Y(
            'Low:Q',
            title='Price',
            scale=alt.Scale(zero=False),
        ),
        alt.Y2('High:Q')
    )

    bar = base.mark_bar().encode(
        alt.Y('Open:Q'),
        alt.Y2('Close:Q')
    )

    all = rule + bar
    st.altair_chart(all.add_selection(token_selector).transform_filter(token_selector).interactive())

def display_chart_3():
    #test which one they like better: drop down or bar plot with token names
    #consider adding trend line(s)

    label_list = ['All'] + list(final_union_df['token'].unique())

    input_dropdown1 = alt.binding_select(options=[None] + list(final_union_df['token'].unique()), labels=label_list)
    token_selector1 = alt.selection_single(name='Currency: ', fields=['token'], bind=input_dropdown1)
    #token_selector2 = alt.selection_single(name='x_axis', fields=['token'], bind=input_dropdown)
    brush = alt.selection(type='interval')
    multi = alt.selection(type='multi')

    #scales = alt.selection_interval(bind='scales')

    #select time period with this small chart
    small = alt.Chart(final_union_df).mark_bar(tooltip=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%m/%d', labelAngle=-45), )
        #,y=alt.Y('Date:T', axis=alt.Axis(format='%m/%y', labelAngle=-45))
        ,color=alt.condition(brush, alt.value('red'), alt.value('grey'))
        ).add_selection(brush).properties(width=875, height=100)

    #select multiple tokens with this small chart
    tokens = alt.Chart(final_union_df).mark_bar(tooltip=True).encode(
        x=alt.X('token:O', title=None, axis=alt.Axis(labelAngle=-45))
        ,color=alt.condition(brush, alt.value('blue'), alt.value('grey'))
        ).add_selection(brush).properties(width=875, height=100)


    #bar height is max price for each token?

    large = alt.Chart(final_union_df).mark_circle(tooltip=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%m/%d/%y', labelAngle=-45))
        ,y=alt.Y('percent_change:Q', title='Percent Change', axis=alt.Axis(format='%',  labels=True, tickSize=0))
        ,color='token'
        #alt.condition(brush, alt.value('red'), alt.value('grey'))
        ).add_selection(
             token_selector1
             ).transform_filter(
                 token_selector1).transform_filter(brush).properties(
                         width=875, height=600).interactive()
        


    both = alt.vconcat(small, tokens)
    both = alt.vconcat(both, large)
    both.configure_legend(
            strokeColor='gray',
        fillColor='#EEEEEE',
        padding=10,
        cornerRadius=10,
        orient='top-right'
    )
    st.altair_chart(both)

def display_chart_4():
    #test which one they like better: drop down or bar plot with token names
    #consider adding trend line(s)

    label_list = ['All'] + list(final_union_df['token'].unique())

    input_dropdown1 = alt.binding_select(options=[None] + list(final_union_df['token'].unique()), labels=label_list)
    token_selector1 = alt.selection_single(name='Currency: ', fields=['token'], bind=input_dropdown1)
    #token_selector2 = alt.selection_single(name='x_axis', fields=['token'], bind=input_dropdown)
    brush = alt.selection(type='interval')
    brush2 = alt.selection(type='interval')


    #scales = alt.selection_interval(bind='scales')

    #select time period with this small chart
    small = alt.Chart(final_union_df).mark_bar(tooltip=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%m/%d', labelAngle=-45), )
        #,y=alt.Y('Date:T', axis=alt.Axis(format='%m/%y', labelAngle=-45))
        ,color=alt.condition(brush, alt.value('red'), alt.value('grey'))
        ).add_selection(brush).properties(width=875, height=100)

    #select multiple tokens with this small chart
    tokens = alt.Chart(final_union_df).mark_bar(tooltip=True).encode(
        x=alt.X('token:O', title=None, axis=alt.Axis(labelAngle=-45))
        ,color=alt.condition(brush, alt.value('blue'), alt.value('grey'))
        ).add_selection(brush2).properties(width=875, height=100)


    #bar height is max price for each token?

    large = alt.Chart(final_union_df).mark_line(tooltip=True).encode(
        x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%m/%d/%y', labelAngle=-45))
        ,y=alt.Y('percent_change:Q', title='Percent Change', axis=alt.Axis(format='%',  labels=True, tickSize=0))
        ,color='token'
        #alt.condition(brush, alt.value('red'), alt.value('grey'))
        ).add_selection(
             token_selector1
             ).transform_filter(
                 token_selector1).transform_filter(brush).transform_filter(brush2).properties(
                         width=875, height=600).interactive()
        


    both = alt.vconcat(small, tokens)
    both = alt.vconcat(both, large)
    both.configure_legend(
            strokeColor='gray',
        fillColor='#EEEEEE',
        padding=10,
        cornerRadius=10,
        orient='top-right'
    )
    st.altair_chart(both)

def display_chart_5():
    selection = alt.selection_multi(fields=['token'], bind='legend')

    chart = alt.Chart(final_union_df).mark_bar().encode(
        alt.X("Date:T"),
        alt.Y("percent_change:Q", title='Percentage Change'),
        color=alt.condition("datum.percent_change < 0",
                                     alt.value("#ae1325"),
                                     alt.value("#06982d")),
        tooltip= ['Date:T', 'percent_change']
    ).add_selection(
        selection
    ).properties(height=500, width=800, title='Percentage Change of Currency Over Time')

    input_dropdown1 = alt.binding_select(options=[None] + list(final_union_df['token'].unique()), labels=label_list)
    token_selector = alt.selection_single(name='Currency: ', fields=['token'], bind=input_dropdown1)
    st.altair_chart(chart.add_selection(token_selector).transform_filter(token_selector).interactive())

def display_chart_6():
    selection = alt.selection_multi(fields=['token'], name='Currency')

    chart = alt.Chart(final_union_df).mark_circle().encode(
        x=alt.X('yearmonth(Date)', title='Date'),
        y=alt.Y('mean(Close)', axis=alt.Axis(title='Average Closing Price (in USD)')),
        size = alt.Size('mean(Volume):Q',
            legend=alt.Legend(title='Average Volume Traded')
        ),
        tooltip=['yearmonth(Date)', 'mean(Close)', 'mean(Volume)']
    ).properties(title='Price of Currency Over Course of Year With Size Encoded by Volume Traded', width=800, height=500).add_selection(
        selection
    )

    lineplot = alt.Chart(final_union_df).mark_line().encode(
        x=alt.X('yearmonth(Date)', title='Date'),
        y=alt.Y('mean(Close)'),
        tooltip=['yearmonth(Date)', 'mean(Close)', 'mean(Volume)']
    )

    both = chart + lineplot

    input_dropdown1 = alt.binding_select(options=[None] + list(final_union_df['token'].unique()), labels=label_list)
    token_selector = alt.selection_single(name='Currency: ', fields=['token'], bind=input_dropdown1)
    st.altair_chart(both.add_selection(token_selector).transform_filter(token_selector).interactive())

def display_chart_7():
    selection = alt.selection_multi(fields=['token'], bind='legend')

    chart = alt.Chart(final_union_df).mark_line().encode(
        alt.X("Date:T"),
        alt.Y("Close:Q", title='Close'),
        tooltip= ['Date:T', 'Close:Q']
    ).add_selection(
        selection
    ).transform_filter(selection).properties(height=500, width=800, title='Closing Price Over Time')

    moving_avg = alt.Chart(final_union_df).mark_line(
        color='red',
        size=3
    ).transform_window(
        rolling_mean='mean(Close)'
    ).encode(
        x='Date:T',
        y='rolling_mean:Q'
    )

    both = chart + moving_avg

    input_dropdown1 = alt.binding_select(options=[None] + list(final_union_df['token'].unique()), labels=label_list)
    token_selector = alt.selection_single(name='Currency: ', fields=['token'], bind=input_dropdown1)
    st.altair_chart(both.add_selection(token_selector).transform_filter(token_selector).interactive())

if __name__ == "__main__":
    display_chart_0()
    display_chart_1()
    display_chart_2()
    display_chart_3()
    display_chart_4()
    display_chart_5()
    display_chart_6()
    display_chart_7()
    
