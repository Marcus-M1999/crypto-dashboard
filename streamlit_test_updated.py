import streamlit as st
import pandas as pd
from datetime import timezone
from datetime import datetime
import numpy as np
import altair as alt
import streamlit.components.v1 as components
from PIL import Image




# loading data
day_signals = pd.read_csv("ada_signals_day.csv")
hour_signals = pd.read_csv("ada_signals_hour.csv")
usd = pd.read_csv("ADA-USD.csv")
day_signals = pd.read_csv("data_for_viz_project.csv")
img = Image.open("cryptoreview_logo.jpg")
ADA_data = pd.read_csv("ADA-USD.csv")


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

# EXPERIMENTING (alternative representation of price per currency)
#Create a selection that chooses the nearest point & selects based on x-value


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
chart

ada_df = pd.read_csv('ADA-USD.csv')
ada_df['token'] = 'ADA'
ada_df['max_close'] = ada_df['Close'].max()
ada_df['mean_close'] = ada_df['Close'].mean()
btc_df = pd.read_csv('BTC-USD.csv')
btc_df['token'] = 'BTC'
btc_df['max_close'] = btc_df['Close'].max()
btc_df['mean_close'] = btc_df['Close'].mean()
eth_df = pd.read_csv('ETH-USD.csv')
eth_df['token'] = 'ETH'
eth_df['max_close'] = eth_df['Close'].max()
eth_df['mean_close'] = eth_df['Close'].mean()

union_df = pd.concat([ada_df, btc_df])
final_union_df = pd.concat([union_df, eth_df])
final_union_df['percent_change'] = (final_union_df['Adj Close'] - final_union_df['Open']) / final_union_df['Adj Close'] 
final_union_df.head()

# New chart 1 by Marcus
all_prices_df = ada_df.merge(btc_df, how="inner", on="Date")
all_prices_df = all_prices_df.merge(eth_df, how="inner", on="Date")
all_prices_df = all_prices_df.drop(['max_close', 'max_close_x', 'max_close_y', 'mean_close', 'mean_close_x', 'mean_close_y'], axis=1)
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

rects + text

# New chart 2 by Marcus
input_dropdown1 = alt.binding_select(options=list(final_union_df['token'].unique()))
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
all.add_selection(token_selector).transform_filter(token_selector).interactive()

input_dropdown = alt.binding_select(options=list(final_union_df['token'].unique()))
token_selector1 = alt.selection_single(name='Token', fields=['token'], bind=input_dropdown)
#token_selector2 = alt.selection_single(name='x_axis', fields=['token'], bind=input_dropdown)
brush = alt.selection(type='interval')

#scales = alt.selection_interval(bind='scales')

# New chart 3
small = alt.Chart(final_union_df).mark_bar(tooltip=True).encode(
    x=alt.X('Date:T', axis=alt.Axis(format='%m/%y', labelAngle=-45), )
    ,y=alt.Y('Date:T', axis=alt.Axis(format='%m/%y', labelAngle=-45))
    ,color=alt.condition(brush, alt.value('red'), alt.value('grey'))
    ).add_selection(brush).properties(width=875, height=100)



#bar height is max price for each token?

large = alt.Chart(final_union_df).mark_circle(tooltip=True).encode(
    x=alt.X('Date:T', axis=alt.Axis(format='%m/%d/%y', labelAngle=-45))
    ,y=alt.Y('percent_change:Q', axis=alt.Axis(format='%',  labels=True, tickSize=0))
    ,color='token'
    #alt.condition(brush, alt.value('red'), alt.value('grey'))
    ).add_selection(
         token_selector1
         ).transform_filter(
             token_selector1).transform_filter(brush).properties(
                     width=875, height=600).interactive()
    


both = alt.vconcat(small, large)
both.configure_legend(
        strokeColor='gray',
    fillColor='#EEEEEE',
    padding=10,
    cornerRadius=10,
    orient='top-right'
)
both

if __name__ == "__main__":
    pass
