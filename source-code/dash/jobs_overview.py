#!/usr/bin/env python

from argparse import ArgumentParser
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime
import pandas as pd


def generate_overview_table(jobs):
    jobs_summary = jobs[['job_id', 'node']]\
            .drop_duplicates()\
            .groupby('job_id')\
            .count()
    jobs_summary = jobs_summary.merge(jobs.groupby('job_id')[['time']].min(),
                                      on='job_id')
    jobs_summary = jobs_summary.merge(jobs.groupby('job_id')[['time']].max(),
                                      on='job_id')
    jobs_summary.columns = ['nodes', 'start time', 'end time']
    jobs_summary.insert(0, 'job_id', jobs_summary.index)
    return html.Table([
        html.Thead(
            html.Tr([html.Th(column) for column in jobs_summary.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(jobs_summary.loc[job_id][column])
                    for column in jobs_summary.columns])
            for job_id in jobs_summary.index]
        )]
    )

def generate_job_menu(jobs):
    job_list = [{'label': str(job_id), 'value': str(job_id)}
                for job_id in jobs.job_id.unique()]
    if len(job_list):
        return dcc.Dropdown(
            id='job_menu',
            options=job_list,
            value=job_list[0]['value'],
            placeholder='Select a job...',
        )



if __name__ == '__main__':
    arg_parsr = ArgumentParser(description='visualize job performance')
    arg_parsr.add_argument('--job-file', required=True,
                           help='file with job/node information')
    arg_parsr.add_argument('--load-file', required=True,
                           help='file with node/load information')
    options = arg_parsr.parse_args()
    jobs = pd.read_csv(options.job_file, parse_dates=True,
                       date_parser=pd.to_datetime)
    loads = pd.read_csv(options.load_file, parse_dates=True,
                        date_parser=pd.to_datetime)
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(children=[
        html.H1(children='Job overview'),
        html.Div(children=[
            html.Div(children=[generate_overview_table(jobs)],
                     style={'width': '70%', 'display': 'inline-block',
                            'margin': '20pt'}),
            html.Div(children=[
                html.Label('Jobs'),
                generate_job_menu(jobs),
            ], style={'width': '10%', 'float': 'left', 'display': 'inline-block',
                      'margin': '20pt'})
        ]),
        html.Div(children=[
            html.Div(children=[ dcc.Graph(id='cpu_load_graph')],
                     style={'width': '45%', 'display': 'inline-block'}),
            html.Div(children=[dcc.Graph(id='mem_load_graph')],
                     style={'widht': '45%', 'float': 'right', 'display': 'inline-block'})
        ])
    ])

    @app.callback(
        [Output('cpu_load_graph', 'figure'), Output('mem_load_graph', 'figure')],
        [Input('job_menu', 'value')])
    def update(job_id):
        data = loads.merge(jobs.query(f'job_id == {job_id}'), on=['time', 'node'],
                           how='right')
        figures = []
        for quantity in ['cpu', 'mem']:
            nodes_data = []
            for node_df in data.groupby('node'):
                node_data = {
                    'name': node_df[0],
                    'x': node_df[1].time,
                    'y': node_df[1][f'{quantity}_load'],
                    'mode': (['markers', 'line'],),
                }
                nodes_data.append(node_data)
            figures.append({
                'data': nodes_data,
                'layout': dict(
                    xaxis={'title': 'time'},
                    yaxis={'title': f'{quantity} load'},
                    hovermode='closest'),
            })
        return figures


    app.run_server(debug=True)
