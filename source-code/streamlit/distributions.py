#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# This is markdown that will be displayed automatically (magic commands)
'''
# Distribution tester

Pick a probability distribution from the list and we shall draw the a
histogram for a random sample from the selected distribution.
'''

# Make some choices for a user to select
keys = ['Normal','Uniform']
dist_key = st.selectbox('Which Distribution do you want to plot?',keys)

# Logic of our program
if dist_key == 'Normal':
    '''
    Select the mean value $\mu$ and the standard deviation $\sigma$ using the
    sliders.
    '''
    mu = st.slider('mu', min_value=-2.0, max_value=2.0, value=0.0, step=0.25)
    sigma = st.slider('sigma', min_value=0.0, max_value=5.0, value=1.0, step=0.25)
    nums = np.random.normal(loc=mu, scale=sigma, size=1000)
elif dist_key == 'Uniform':
    nums = np.random.uniform(0.0, 2.0, size=1000)

# Display data
figure, axes = plt.subplots()
axes.hist(nums, bins=20)
axes.set_xlabel('$x$')
axes.set_ylabel('$P(x)$')

st.pyplot(figure)
