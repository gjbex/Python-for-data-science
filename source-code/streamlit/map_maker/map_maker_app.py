#!/usr/bin/env python

import altair_saver
from map_maker_lib import create_topo_data, read_file, validate_data, \
        create_plot, DATA_TYPES, DELIMITERS, COLOR_SCHEMES
import streamlit as st


BE_GEO_URL = 'https://gist.githubusercontent.com/jandot/ba7eff2e15a38c6f809ba5e8bd8b6977/raw/eb49ce8dd2604e558e10e15d9a3806f114744e80/belgium_municipalities_topojson.json'
BE_MUNICIPALITIES_FEATURE = 'BE_municipalities'


if __name__ == '__main__':
    '''# Map Maker
    '''

    file_column1, file_column2 = st.beta_columns(2)
    with file_column1:
        data_file = st.file_uploader('Data file')
    with file_column2:
        encoding = st.selectbox('File encoding', ('utf-8', 'iso-8859-1'))
        delimiter = DELIMITERS[st.selectbox('Data delimiter',
                                             list(DELIMITERS.keys()))]

    topo_municipalities = create_topo_data(BE_GEO_URL, BE_MUNICIPALITIES_FEATURE)

    if data_file:
        file_name = data_file.name
        bytes_array = data_file.read()
        data = read_file(file_name, bytes_array, encoding=encoding, delimiter=delimiter)
        validate_data(data) 

        data_column1, data_column2, data_column3 = st.beta_columns(3)
        with data_column1:
            column_name = st.selectbox('Data column',
                                       [column for column in data.columns
                                        if column not in ('nis_code',)])
        with data_column2:
            data_type = DATA_TYPES[st.selectbox('Data type', list(DATA_TYPES.keys()))]
        with data_column3:
            color_scheme = st.selectbox('Color scheme', COLOR_SCHEMES)
        tooltip_names = st.multiselect('Tooltip columns',
                                       [column for column in data.columns
                                        if column not in ('nis_code',)])
        plot = create_plot(topo_data=topo_municipalities, data=data,
                           column_name=column_name, data_type=data_type,
                           tooltip_columns=tooltip_names, scheme=color_scheme)
        st.write(plot)
