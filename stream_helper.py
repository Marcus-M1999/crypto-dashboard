

import pandas as pd
from datetime import timezone
from datetime import datetime
import numpy as np
import altair as alt
import streamlit.components.v1 as components
from PIL import Image
from nomics import Nomics
import time
import requests



def smart_num(n):

    """for printing out large numbers. Anything above 100k will be put into units.
    1500000 will become 1.5M, and then billion and then trillion etc etc etc"""

    n = float(n)
    ab = abs(n)
    if ab<1000000:
        n = round(n,2)
        return '{:,}'.format(n)

    # millions i think
    if ab<1000000000:
        z = n/1000000
        z = round(z,2)
        return str(z)+"M"

    if ab < 10**12:
        z = n/(10**9)
        z = round(z,2)
        return str(z)+"B"

    z = n / (10**12)
    z = round(z,2)
    return str(z)+"T"
