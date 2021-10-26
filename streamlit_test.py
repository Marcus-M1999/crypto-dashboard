import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

ADA_data = pd.read_csv("Final_Project/ADA-USD.csv")
print(ADA_data)

option = st.selectbox(\
    'Which coin do you like best?', ["ADA","BTC","ETH"])

'You selected: ', option

# EXPERIMENTING (alternative representation of price per currency)
#Create a selection that chooses the nearest point & selects based on x-value
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['date_MDY'], empty='none')

# The basic line
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

# Put the five layers into a chart and bind the data
chart = alt.layer(line, selectors, points, rules, text,
                       data=ADA_data, 
                       width=800, height=400,title='Cryptocurrency Price History')
                       
                       
chart
