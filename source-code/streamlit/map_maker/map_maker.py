#!/usr/bin/env python

import altair_saver
from argparse import ArgumentParser
from map_maker_lib import create_topo_data, read_data, validate_data, \
        create_plot
import random


BE_GEO_URL = 'https://gist.githubusercontent.com/jandot/ba7eff2e15a38c6f809ba5e8bd8b6977/raw/eb49ce8dd2604e558e10e15d9a3806f114744e80/belgium_municipalities_topojson.json'
BE_MUNICIPALITIES_FEATURE = 'BE_municipalities'


def get_data_type(data_type_str):
    if data_type_str == 'quantitative':
        return 'Q'
    elif data_type_str == 'nominal':
        return 'N'
    else:
        raise ValueError(f'unknown data type "{data_type_str}"')


if __name__ == '__main__':
    arg_parser = ArgumentParser('create maps')
    arg_parser.add_argument('--data-uri', required=True,
                            help='URI for data to plot')
    arg_parser.add_argument('--output', required=True,
                            help='file name for the output')
    arg_parser.add_argument('--encoding', default='utf-8',
                            help='data encoding for CSV data file')
    arg_parser.add_argument('--delimiter', default=',',
                            help='delimiter for CSV data file')
    arg_parser.add_argument('--column-name', required=True,
                            help='name of column to plot')
    arg_parser.add_argument('--data-type', choices=['quantitative', 'nominal'],
                            default='quantitative',
                            help='type of data to be plotted')
    arg_parser.add_argument('--geodata-url', default=BE_GEO_URL,
                            help='URL for GeoJSON data')
    arg_parser.add_argument('--geodata-feature', default=BE_MUNICIPALITIES_FEATURE,
                            help='GeoJSON feature to use')
    arg_parser.add_argument('--stroke', default='lightgrey',
                            help='color of strokes between chloropleths')
    arg_parser.add_argument('--stroke-width', type=float, default=0.5,
                            help='width of strokes between chloropleths')
    arg_parser.add_argument('--legend-title',
                            help='title of the legend, defaults to column name')
    arg_parser.add_argument('--color-scheme', default='reds',
                            help='color scheme for plot')
    options = arg_parser.parse_args()
    topo_municipalities = create_topo_data(options.geodata_url,
                                           options.geodata_feature)
    data = read_data(options.data_uri, encoding=options.encoding,
                     delimiter=options.delimiter)
    validate_data(data)
    plot = create_plot(topo_data=topo_municipalities, data=data,
                       column_name=options.column_name,
                       data_type=get_data_type(options.data_type),
                       stroke=options.stroke, strokeWidth=options.stroke_width,
                       legend_title=options.legend_title, scheme=options.color_scheme)
    plot.save(options.output)
