# Importing Libraries
import pdb

import pandas as pd
import numpy as np
import warnings
import json, os
import plotly.express as px
import plotly.graph_objects as go

from dash import dcc, dash_table, html, Input, Output, ctx, callback
import dash_bootstrap_components as dbc
from sqlalchemy import create_engine

warnings.filterwarnings("ignore")
current_dir = os.path.dirname(os.path.abspath(__file__))

engine_new = create_engine('sqlite:///sources//hicc.db')
engine_old = create_engine('sqlite:///sources//old_hart.db')

output_1a = pd.read_sql_table('output_1a', engine_new.connect())
output_1b = pd.read_sql_table('output_1b', engine_new.connect())
output_2 = pd.read_sql_table('output_2', engine_new.connect())
output_3 = pd.read_sql_table('output_3', engine_new.connect())
output_4a = pd.read_sql_table('output_4a', engine_new.connect())
output_4b = pd.read_sql_table('output_4b', engine_new.connect())
output_5a = pd.read_sql_table('output_5a', engine_new.connect())
output_5b = pd.read_sql_table('output_5b', engine_new.connect())
output_6 = pd.read_sql_table('output_6', engine_new.connect())
output_7 = pd.read_sql_table('output_7', engine_new.connect())
output_8 = pd.read_sql_table('output_8', engine_new.connect())
output_9 = pd.read_sql_table('output_9', engine_new.connect())
output_10a = pd.read_sql_table('output_10a', engine_new.connect())
output_10b = pd.read_sql_table('output_10b', engine_new.connect())

# Setting a default plot and table which renders before the dashboard is fully loaded

fig1 = px.line(x=['Not Available in CD/Regional level. Please select CSD/Municipal level'],
               y=['Not Available in CD/Regional level. Please select CSD/Municipal level'])
fig2 = px.line(x=['Not Available in CD/Regional level. Please select CSD/Municipal level'],
               y=['Not Available in CD/Regional level. Please select CSD/Municipal level'])

table = pd.DataFrame({'Not Available in CD/Regional level. Please select CSD/Municipal level': [0]})

# Importing Geo Code Information
mapped_geo_code = pd.read_sql_table('geocodes_integrated', engine_old.connect())
# mapped_geo_code = mapped_geo_code.replace(5917056, 5917054).replace('Juan de Fuca (CSD, BC)', 'Juan de Fuca (Part 1) (CSD, BC)')

# Adding missing CSDs from HART file
# add_new_codes = [
#     [5900002, 59, 59, 'Denman Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900003, 59, 59, 'Gabriola Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900004, 59, 59, 'Galiano Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900005, 59, 59, 'Gambier Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900006, 59, 59, 'Hornby Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900007, 59, 59, 'Lasqueti Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900008, 59, 59, 'Mayne Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900009, 59, 59, 'North Pender Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900010, 59, 59, 'Saltspring Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900011, 59, 59, 'Saturna Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900012, 59, 59, 'Thetis Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5900013, 59, 59, 'South Pender Island Trust Area', 'British Columbia (Province)', 'British Columbia (Province)'],
#                     [5949018, 5949, 59, 'Kitimat-Stikine E RDA (CSD, BC)', 'Kitimat-Stikine (CD, BC)', 'British Columbia (Province)']
#                  ]
# missing_codes_df = pd.DataFrame(add_new_codes, columns=mapped_geo_code.columns)
# mapped_geo_code = pd.concat([mapped_geo_code, missing_codes_df])

# Configuration for plot icons

config = {'displayModeBar': True, 'displaylogo': False,
          'modeBarButtonsToRemove': ['zoom', 'lasso2d', 'pan', 'select', 'zoomIn', 'zoomOut', 'autoScale', 'resetScale', 'resetViewMapbox']}

# Colors for map
colors = ['#D7F3FD', '#88D9FA', '#39C0F7', '#099DD7', '#044762']
hh_colors = ['#D8EBD4', '#93CD8A', '#3DB54A', '#297A32', '#143D19']
hh_type_color = ['#002145', '#3EB549', '#39C0F7']
columns_color_fill = ['#F3F4F5', '#EBF9FE', '#F0FAF1']
modebar_color = '#099DD7'
modebar_activecolor = '#044762'

# Map color opacity

opacity_value = 0.2

# Default location in the map

default_value = 'Ottawa CV (CSD, ON)'

layout = html.Div(children=[

    # Store Area/Comparison Area/Clicked area scale info in local storage

    dcc.Store(id='area-scale-store', storage_type='local'),
    dcc.Store(id='main-area', storage_type='local'),
    dcc.Store(id='comparison-area', storage_type='local'),

    # Add the Export to PDF button
    dbc.Button("Export to PDF", id="export-button", className="mb-3", color="primary"),

    html.Div(id='dummy-output', style={'display': 'none'}),

    html.Div(id='page-content-to-print',
             children=[
                 # Introduction
                 html.H3(children=html.Strong('HICC'),
                         id='visualization1'),
                 # Description
                 html.Div([
                     html.H6(children=[
                         """This dashboard is intended to gather and present some data that is requested for in the Housing Needs Assessment (HNA) template created by Housing, Infrastructure and Communities Canada (HICC). Some of the below data points have been created specifically to address the HNA template, while others have been gathered from other sources and presented here to make the data more accessible.
                        Please note that data for smaller communities may be missing, or subject to inconsistencies that result from random rounding rules applied to data derived from the Canadian census.
                        """,
                         html.Br(),
                         html.Br(),

                     ]),  html.Br()
                 ], className='muni-reg-text-lgeo'),

                 
                 html.Div([
                     # Title
                     # 1. HICC Section 3.1.1, data point 1. Output 1a
                     html.H4(children=html.Strong('Households Within 800m and 200m of Rail/Light-rail Transit Station (i.e. High Frequency Transit Stop or Station) '),
                             id='visualization1'),
                     html.H5(children='HICC HNA Template: Section 3.1.1'),
                     # Component Description
                     html.Div([
                         html.H6(
                             'The following table shows the number of households within 800 meters and 200 meters of rail/light-rail transit station respectively. '
                             'It also shows the percentage of households within the community that are within 800 or 200 meters of a station. The number of households comes from the 2021 census. ',),
                             #style={'fontFamily': 'Open Sans, sans-serif'}),
                         dbc.Button("Export", id="export-table-15", className="mb-3", color="primary"),
                         dash_table.DataTable(
                         id='output_1a',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }

                     ), html.Div(id='output_1a-container'),
                     html.Br()
                     ], className='pg2-output1a-lgeo'
                 ),


                 # 1. HICC Section 3.1.1, data point 1. Output 1b
                     html.Div([
                         html.H6("The following table shows the number of households within 800 meters and 200 meters of existing and under construction"
                                 " rail/light-rail transit station respectively. It also shows the percentage of households within the community that are "
                                 "within 800 or 200 meters of an existing or under construction station. The number of households comes from the 2021 census, but the location of rail stations include all that serve commuter rail networks."),
                         dbc.Button("Export", id="export-table-16", className="mb-3", color="primary"),
                         dash_table.DataTable(
                         id='output_1b',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ), html.Div(id='output_1b-container'),
                     html.Br()
                     ], className='pg2-output1b-lgeo'


                 ),

                 # 2. HICC Section 3.3, data point 9 and 10. Output 9
                 html.Div([
                     html.H4(children=html.Strong('Changes in Head of Household rates by age between 2016 and 2021'),
                             id='visualization9'),
                     html.H5(children='HICC HNA Template: Section 3.3'),
                     html.H6(
                         f'	The following chart visualizes the Headship Rate for each age group in 2016 and 2021.',
                         # style={'fontFamily': 'Open Sans, sans-serif'}
                     ),
                     dcc.Graph(id='graph_9_1',
                                   figure=fig1,
                                   config=config,
                                   ),
                     html.H6(children='The following chart shows the change in Headship Rate for each age group between '
                                      '2016 and 2021 (i.e. Headship Rate in 2021 minus Headship Rate in 2016).',
                             # style={'fontFamily': 'Open Sans, sans-serif'}
                             ),
                     dcc.Graph(id='graph_9_2',
                               figure=fig2,
                               config=config,
                               ),
                    html.H6('The following table shows the change in Headship Rate by age group between 2016 and 2021. Headship rate is the number of Primary Household Maintainers (i.e. the first person in the household identified '
                            'as someone who pays the shelter costs for the dwelling in the census questionnaire) divided by the Population (i.e. total number of people in the given geography).',
                            # style={'fontFamily': 'Open Sans, sans-serif'}
                            ),


                     dbc.Button("Export", id="export-table-12", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_9',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ),
                     html.H6('*Note that the data for small geographies may show there to be more primary household maintainers'
                             ' in a given age range than there are people. This happens in a few geographies where the population is low. This is not a realistic result and can be attributed to Statistics Canada’s random rounding of cell counts.'
                             ' In these cases, the headship rate has been set to equal 100% of the age group.',
                             # style={'fontFamily': 'Open Sans, sans-serif'}
                             ),
                     html.Div(id='output_9-container')
                 ], className='pg2-output9-lgeo'
                 ),

                 # 2. HICC Section 3.3, data point 9 and 10. Table 9
                 html.Div([
                     html.H4(html.Strong("Estimated Household Suppression by age of Primary Household Maintainers")),
                     html.H5("HICC HNA Template: Section 3.3"),
                     # Tables
                     html.H6(children=[
                             f'The following two tables show the estimated number of Suppressed Households (households that would have formed if not for housing affordability challenges) according to the methodology used in the Province of '
                             f'British Columbia’s HNR Method, specifically Component C: housing units and suppressed household formation. ',
                             html.A("(Link to Housing Needs Report Technical Guidance).", href='https://www2.gov.bc.ca/assets/gov/housing-and-tenancy/tools-for-government/uploads/hnr_method_technical_guidelines.pdf', target="_blank"),

                     ]),

                 ], className='pg2-bar9-lgeo'),

                 # 2. HICC Section 3.3, data point 9 and 10. Output 10a
                 html.Div([
                     dbc.Button("Export", id="export-table-13", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_10a',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ),
                     html.H6('*Note that the data for small geographies may show there to be more primary household maintainers '
                             'in a given age range than there are people. This happens in a few geographies where the population is low. '
                             'This is not a realistic result and can be attributed to Statistics Canada’s random rounding of cell counts. '
                             'In these cases, the headship rate has been set to equal 100% of that age group.'),
                     html.H6('**Note that the “75 and older” category is used here because data from 2006 uses these categories and does not have an “85 and older” category. For 2021, this category represents the sum of categories “75 to 84” and “85 and older".'),
                     html.Div(id='output_10a-container')
                 ], className='pg2-output10a-lgeo'
                 ),

                 # 2. HICC Section 3.3, data point 9 and 10. Output 10b
                 html.Div([
                     dbc.Button("Export", id="export-table-14", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_10b',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ),
                     html.H6('*Note that the “75 and older” category is used here because data from 2006 uses these categories '
                             'and does not have an “85 and older” category. For 2021, this category represents the sum of categories “75 to 84” and “85 and older”.'),
                     html.Div(id='output_10b-container'),
                     html.Br()
                 ], className='pg2-output10b-lgeo'
                 ),

                 # 3. HICC Section 4.1, data point 11. TO BE Received in round 2


                 # Data point 6 primary and secondary rental units HICC HNA Template: Section 5.2.1
                 html.Div([
                     html.H4(children=html.Strong(f'Number of Primary and Secondary Rental Units')),
                     html.H5(children=html.Strong('HICC HNA Template: Section 5.2.1'),
                             id='visualization6'),
                     html.H6(
                         f'The following chart shows the relative size of the primary and secondary rental markets as a share of the whole rental market.',
                         # style={'fontFamily': 'Open Sans, sans-serif'}
                     ),
                     dcc.Graph(id='graph_6',
                              figure=fig1,
                              config=config,
                     ),
                     html.H6('The following table shows the number of primary secondary rental units. Primary rental units are dwellings originally intended to supply the rental market, and are identified by CMHC’s Rental Market Survey. Secondary rental units are condominium apartments or other privately-owned dwellings that are rented out. Secondary '
                             'rental units are calculated as the total number of rental households in 2021 per the census less the number of primary rental units identified by CMHC in 2021.'),

                     dbc.Button("Export", id="export-table-9", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_6',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ), html.Div(id='output_6-container'),
                     html.Br()
                 ], className='pg2-output6-lgeo'
                 ),



                 # output 13 TO BE RECEIVED TODO in round 2

                 # 6. HICC Section 5.4, data point 2. Output 2a
                 html.Div([
                     html.H4(children=[html.Strong('The Change in Average Rents between 2016 and 2023.')],
                             id='visualization2a'),
                     html.H5("HICC HNA Template: Section 5.4",
                             # style={'fontFamily': 'Open Sans, sans-serif'}
                             ),
                     html.H6('The following table shows the average monthly rent for all primary rental units per CMHC’s '
                             'Rental Market Survey (i.e. all occupied and vacant rental units). These values reflect data collected in October of each year.',
                             # style={'fontFamily': 'Open Sans, sans-serif'}
                             ),

                     dbc.Button("Export", id="export-table-1", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_2a',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ),


                     html.H6(
                         f'The following chart shows the change in average monthly rent between years as a dollar amount.',
                         # style={'fontFamily': 'Open Sans, sans-serif'}
                     ),
                     # Plot
                     html.Div([

                         dcc.Graph(id='graph_2b_1',
                                   figure=fig1,
                                   config=config,

                                   ),
                         html.H6(
                             f'The following chart shows the percentage change in average monthly rent between years.',
                             # style={'fontFamily': 'Open Sans, sans-serif'}
                         ),
                         dcc.Graph(id='graph_2b_2',
                                   figure=fig2,
                                   config=config,

                                   ),
                         html.Div(id='graph_2b-container')  # is this necessary?
                     ]),

                      html.Div(id='output_2a-container')
                 ], className='pg2-output2a-lgeo'
                 ),

                 # 6. HICC Section 5.4, data point 2. Output 2b
                 html.Div([
                     html.H6('The following table shows the yearly change in monthly rent for primary rental units (captured annually in October) as a dollar amount and as a percentage.',
                             # style={'fontFamily': 'Open Sans, sans-serif'}
                             ),
                     dbc.Button("Export", id="export-table-2", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_2b',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ), html.Div(id='output_2b-container'),
                     html.Br()
                 ], className='pg2-output2b-lgeo'
                 ),



                 # output 3 charts
                 html.Div([
                 html.H4(children=html.Strong('The Change in Vacancy Rates Between 2016 and 2023'),
                         id='visualization3a'),
                 html.H5(
                     f'HICC HNA Template: Section 5.5',
                     # style={'fontFamily': 'Open Sans, sans-serif'}
                 ),
                 html.H6('The following chart shows the vacancy rate for each year.', style={'fontFamily': 'Open Sans, sans-serif'}),

                 # Plot
                 html.Div([
                     dcc.Graph(id='graph_3a',
                               figure=fig1,
                               config=config,
                               ),
                     html.H6(f'The following chart shows the change in the vacancy rate between years as percentage points.',
                     # style={'fontFamily': 'Open Sans, sans-serif'}
                     ),
                     dcc.Graph(id='graph_3b',
                               figure=fig2,
                               config=config,
                               ),
                     html.Div(id='graph_3-container')  # is this necessary?
                 ]),

                 #TABLES
                 html.H6('The following table shows the vacancy rate among primary rental units per CMHC’s Rental Market Survey. '
                         'These values reflect data collected in October of each year.',
                         #style={'fontFamily': 'Open Sans, sans-serif'}
                         ),

                 dbc.Button("Export", id="export-table-3", className="mb-3", color="primary"),
                 dash_table.DataTable(
                     id='output_3a',
                     merge_duplicate_headers=True,
                     style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'},
                     style_cell={'font-family': 'Bahnschrift',
                                 'height': 'auto',
                                 'whiteSpace': 'normal',
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'
                                 },
                     style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                   }
                    ),
                 html.H6('The following table shows the yearly change in vacancy rate for primary rental units in percentage points.',
                         #style={'fontFamily': 'Open Sans, sans-serif'}
                         ),
                 dbc.Button("Export", id="export-table-4", className="mb-3", color="primary"),

                 dash_table.DataTable(
                     id='output_3b',
                     merge_duplicate_headers=True,
                     style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'},
                     style_cell={'font-family': 'Bahnschrift',
                                 'height': 'auto',
                                 'whiteSpace': 'normal',
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'
                                 },
                     style_header={'textAlign': 'center', 'fontWeight': 'bold',
                                   }
                     ),html.Div(id='output_3ab-container'),
                     html.Br()
                 ], className='pg2-output3a-lgeo'
                 ),



                 # HICC Section 5.6, data point 5.
                 html.Div([
                 html.H4(children=[html.Strong('Change in Core Housing Need Over Time (2016 to 2021) Between Both Tenant/Renter and Owner-Occupied Households'),
                                   ],
                         #style={'fontFamily': 'Open Sans, sans-serif'},
                         id='visualization5'),
                 html.H5("HICC HNA Template: Question 5.6"),
                 html.H6(
                     f'The following chart shows the number of households in CHN among owner-occupied and tenant-occupied households in 2016 and 2021.',
                     #style={'fontFamily': 'Open Sans, sans-serif'}
                 ),
                 # output 5 bar charts
                 html.Div([
                     # Plot
                     html.Div([

                         dcc.Graph(id='graph_5a',
                                   figure=fig1,
                                   config=config,

                                   ),
                         html.H6(
                             f'The following chart shows the rate of CHN among owner-occupied and tenant-occupied households in 2016 and 2021. ',
                             #style={'fontFamily': 'Open Sans, sans-serif'}
                         ),
                         dcc.Graph(id='graph_5b',
                                   figure=fig1,
                                   config=config,

                                   ),
                         html.Div(id='graph_5-container')  # is this necessary?
                     ]),

                 ], className='pg2-bar5-lgeo'
                 ),

                 # TABLES
                 html.H6("The following table shows the number of households in core housing need (CHN) among owner-occupied and "
                         "tenant-occupied households in 2016 and 2021. Please note this calculation does not differentiate between the primary and secondary rental market.",
                         #style={'fontFamily': 'Open Sans, sans-serif'}
                         ),
                 dbc.Button("Export", id="export-table-7", className="mb-3", color="primary"),
                 dash_table.DataTable(
                     id='output_5a',
                     merge_duplicate_headers=True,
                     style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'},
                     style_cell={'font-family': 'Bahnschrift',
                                 'height': 'auto',
                                 'whiteSpace': 'normal',
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'
                                 },
                     style_header={'textAlign': 'center', 'fontWeight': 'bold',
                                   }
                    ),
                 html.H6(
                     f'The following table shows the rate of CHN among owner-occupied and tenant-occupied households in 2016 and 2021, '
                     f'where the rate of CHN equals the number of households in CHN divided by the number of households examined for CHN.',
                     #style={'fontFamily': 'Open Sans, sans-serif'}
                 ),
                 dbc.Button("Export", id="export-table-8", className="mb-3", color="primary"),
                 dash_table.DataTable(
                     id='output_5b',
                     merge_duplicate_headers=True,
                     style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'},
                     style_cell={'font-family': 'Bahnschrift',
                                 'height': 'auto',
                                 'whiteSpace': 'normal',
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'
                                 },
                     style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                   }
                     ),html.Div(id='output_5ab-container'),
                     html.Br()
                 ], className='pg2-output5-lgeo'
                 ),

                 # 9. HICC Section 5.7.1, data point 7. Output 7
                 html.Div([
                     html.H4(children=html.Strong('Number of rental housing units that are subsidized or not subsidized'),
                             id='visualization7'),
                     html.H5(html.Strong("HICC HNA Template: Section 5.7.1")),
                     html.H6(
                         f'The following chart shows the relative size of the subsidized and private (i.e. (unsubsidized) rental units as a share of all rental units.',
                         # style={'fontFamily': 'Open Sans, sans-serif'}
                     ),
                     dcc.Graph(id='pie_7',
                               figure=fig1,
                               config=config,
                               ),

                     #tables
                     html.H6("The following table shows the number of rental housing units that received a housing subsidy in 2021, as well as those that were renting in the private rental market, per the census. "
                             "Subsidized housing includes rent geared to income, social housing, public housing, government-assisted housing, non-profit housing, rent supplements and housing allowances."),
                     dbc.Button("Export", id="export-table-10", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_7',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ), html.Div(id='output_7-container'),
                     html.Br()
                 ], className='pg2-output7-lgeo'
                 ),



                 # 10. HICC Section 5.7.1, data point 8. Output 8
                 html.Div([
                     html.H4(children=html.Strong('Number of housing units that are below-market rent in the private market'),
                             id='visualization8'),
                     html.H5(html.Strong("HICC HNA Template: Section 5.7.1")),
                     html.H6('The following table shows the number of private (i.e. unsubsidized) occupied rental housing units with '
                             'below-market rent in 2021, per the census. It also shows the percentage of occupied housing units with a '
                             'below-market rent as a percentage of all private occupied rental housing units.',
                             #style={'fontFamily': 'Open Sans, sans-serif'}
                             ),
                     html.H6('We define “below-market rent” as any shelter cost that would be affordable to a household who earned 80% of area median '
                             'household income (AMHI), where affordable means that the household pays no more than 30% of it’s pre-tax income on shelter costs.',  style={'fontFamily': 'Open Sans, sans-serif'}),
                     html.H6(  "Example: If the community's AMHI was $90,000 per year, a household earning 80% "
                            "of AMHI would be earning $72,000 per year. They can afford a shelter cost of 30% of their income, which is $21,600 per year or $1800 per month. "
                               "We then say that any unsubsidized renter household whose shelter cost was less than $1800 per month had a below market rent.",
                               #style={'fontFamily': 'Open Sans, sans-serif'}
                               ),
                     dbc.Button("Export", id="export-table-11", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_8',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                       }
                     ), html.Div(id='output_8-container'),
                     html.Br()
                 ], className='pg2-output8-lgeo'
                 ),

                 #11. HICC Section 5.7.1, data point 12. TODO in round 2

                 # HICC Section 5.9.2, data point 4a and 4b tables
                 html.Div([
                     html.H4(children=html.Strong('Housing starts by structural type and tenure')),
                     html.H5(children=html.Strong('HICC HNA Template: Section 5.9.2')),
                     html.H6(
                         f'The following chart shows the number of housing starts by the structural type of building, for each calendar year 2016 to 2023.',
                         #style={'fontFamily': 'Open Sans, sans-serif'}
                     ),
                 # 4a graph stacked bar
                 html.Div([

                     # Plot
                     html.Div([
                         html.H6(
                             f'The following graph shows Housing starts by structural type',
                             #style={'fontFamily': 'Open Sans, sans-serif'}
                         ),
                         dcc.Graph(id='graph_4a',
                                   figure=fig1,
                                   config=config,

                                   ),
                         html.Div(id='graph_4a-container')
                     ]),

                 ], className='pg2-bar4a-1-lgeo'
                 ),
                 html.H6("The following table shows the number of housing starts by the structural type of building, for each calendar year 2016 to 2023. "
                         "Data is from CMHC’s “Housing Starts: By Dwelling Type” report, and does not necessarily reflect completed homes in any given year or span of time.",
                         #style={'fontFamily': 'Open Sans, sans-serif'}
                         ),

                 # TABLE
                 dbc.Button("Export", id="export-table-5", className="mb-3", color="primary"),
                 dash_table.DataTable(
                     id='output_4a',
                     merge_duplicate_headers=True,
                     style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'},
                     style_cell={'font-family': 'Bahnschrift',
                                 'height': 'auto',
                                 'whiteSpace': 'normal',
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'
                                 },
                     style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                   }
                 ),
                 html.H6("The following chart shows the number of housing starts by tenure for each calendar year 2016 to 2023.",
                         #style={'fontFamily': 'Open Sans, sans-serif'}
                         ),

                 # 4b graph stacked bar
                 html.Div([
                     # Plot
                     html.Div([
                         dcc.Graph(id='graph_4b',
                                   figure=fig1,
                                   config=config,
                                   ),
                         html.Div(id='graph_4a-container')
                     ]),

                 ], className='pg2-bar4a-1-lgeo'
                 ),

                 html.H6("The following table shows the number of housing starts by tenure (i.e. intended market), for each calendar year 2016 to 2023. ",), # style={'fontFamily': 'Open Sans, sans-serif'}),

                 # TABLE
                 dbc.Button("Export", id="export-table-6", className="mb-3", color="primary"),
                 dash_table.DataTable(
                     id='output_4b',
                     merge_duplicate_headers=True,
                     style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'},
                     style_cell={'font-family': 'Bahnschrift',
                                 'height': 'auto',
                                 'whiteSpace': 'normal',
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis'
                                 },
                     style_header={'textAlign': 'center', 'fontWeight': 'bold',

                                   }
                 ), html.Div(id='output_4ab-container')
             ], className='pg2-output4-lgeo'
             ),


                 # LGEO

                 html.Footer([
                     html.Img(src='.\\assets\\Footer for HNR Calc.png', className='footer-image')
                 ], className='footer'),

             ], className='dashboard-pg2-lgeo'
             ),
    
             ], className='content-container-fullpage'
            ),
         ], className='pg2-output1-plot-box-lgeo'
)



def generate_style_data_conditional(data):
    data_style = []

    for i in range(len(data)):
        row_style = {
            'if': {'row_index': i},
            'backgroundColor': '#74d3f9' if i % 2 != 0 else '#b0e6fc',
            'color': '#000000',
            'border': '1px solid #002145'
        }

        data_style.append(row_style)

    return data_style


def generate_additional_data_style(data, data_columns):
    first_and_last_columns_ids = [data_columns[0]['id'], data_columns[-1]['id']]
    new_data_style = [
                         {
                             'if': {'row_index': len(data) - 1, 'column_id': j['id']},
                             'backgroundColor': '#39C0F7',
                             'color': '#000000',
                             'border-left': 'none',
                             'fontWeight': 'bold'

                         } for j in data_columns[1:-1]

                     ] + [
                         {
                             'if': {'row_index': len(data) - 1, 'column_id': col_id},
                             'fontWeight': 'bold',
                             'backgroundColor': '#39C0F7',
                             'color': '#000000',
                             "maxWidth": "200px"
                         } for col_id in first_and_last_columns_ids
                     ]
    return new_data_style


def generate_style_header_conditional(columns):
    style_conditional = []

    for index, col in enumerate(columns):
        header_style = {
            'if': {'header_index': index},
            'backgroundColor': '#002145' if index == 0 else '#39C0F7',
            'color': '#FFFFFF' if index == 0 else '#000000',
            'border': '1px solid #002145',
        }

        # Remove bottom border if sub-header is empty
        if col[1] == '':
            header_style['border-bottom'] = 'none'

        style_conditional.append(header_style)

    return style_conditional
#TODO: Use this if alignment is required as per the doc
# def generate_style_header_conditional(data, multi_header=False, extend=False):
#     style_conditional = []

#     for index, col in enumerate(data):
#         header_style = {
#             'if': {'header_index': index},
#             'backgroundColor': '#002145' if index == 0 else '#39C0F7',
#             'color': '#FFFFFF' if index == 0 else '#000000',
#             'border': '1px solid #002145',
#         }

#         # Remove bottom border if sub-header is empty
#         if col[1] == '':
#             header_style['border-bottom'] = 'none'
        
#         style_conditional.append(header_style)

#         if extend:
#             if (multi_header) and (not data.empty):
#                 table_columns = [{"name": ['geo', col1, col2], "id": f"{col1}_{col2}"} for col1, col2 in data.columns]
#             else:
#                 table_columns = [{"name": ['geo', col], "id": col} for col in data.columns]

#             print(table_columns)
#             new_header_style = [
#             {
#             'if': {'column_id': col['id']},  
#             'textAlign': 'left' if col['id'] == data[0]['id'] else 'right'
#             }
#             for col in table_columns
#             ]

#             style_conditional.extend(new_header_style)

#     return style_conditional

#TODO: Use this if alignment is required as per the doc
# def generate_style_cell_conditional(columns, generic_style=0):
#     style_cell_conditional = [
#                                 {
#                                     'if': {'column_id': columns[i]['id']},
#                                     'backgroundColor': columns_color_fill[1],
#                                     'textAlign': 'left' if i < 1 else 'right',  
#                                 }
#                                 for i in range(len(columns))
#                             ]
#     return style_cell_conditional

def get_filtered_geo(geo, geo_c, scale, selected_columns=None):
    # Single area mode
    if geo == geo_c or geo_c == None or (geo == None and geo_c != None):

        # When no area is selected
        if geo == None and geo_c != None:
            geo = geo_c
        elif geo == None and geo_c == None:
            geo = default_value

        # Area Scaling up/down when user clicks area scale button on page 1
        if "to-geography-1" == scale:
            geo = geo
        elif "to-region-1" == scale:
            geo = mapped_geo_code.loc[mapped_geo_code['Geography'] == geo, :]['Region'].tolist()[0]
        elif "to-province-1" == scale:
            geo = mapped_geo_code.loc[mapped_geo_code['Geography'] == geo, :]['Province'].tolist()[0]
        else:
            geo = geo
        return geo


def table_generator(geo, df, table_id):
    geoid = mapped_geo_code.loc[mapped_geo_code['Geography'] == geo, :]['Geo_Code'].tolist()[0]

    filtered_df = df[df['ALT_GEO_CODE_EN'] == f'{geoid}']
    # print(filtered_df)
    if table_id == 'output_2b':
        filtered_df = filtered_df[filtered_df['Metric'].isin(['% Change in Avg Rent', 'Change in Avg Rent'])].rename(
            columns={'2017': '2016-2017', '2018': '2017-2018',
                     '2019': '2018-2019', '2020': '2019-2020',
                     '2021': '2020-2021', '2022': '2021-2022',
                     '2023': '2022-2023'}
        )
        filtered_df.drop('2016', axis=1, inplace=True)
    elif table_id == 'output_3a':
        filtered_df = filtered_df[filtered_df['Metric']== 'Vacancy Rate']

    elif table_id == 'output_3b':
        filtered_df = filtered_df[filtered_df['Metric'] == 'Change in Vacancy Rate'].rename(
            columns={'2017': '2016 to 2017', '2018': '2017 to 2018',
                     '2019': '2018 to 2019', '2020': '2019 to 2020',
                     '2021': '2020 to 2021', '2022': '2021 to 2022',
                     '2023': '2022 to 2023'}
        )  #.rename('Change in Vacancy Rate', 'Change in Vacancy Rate (percentage points')
        filtered_df.drop('2016', axis=1, inplace=True)
        for col in filtered_df.columns[6:]:
            filtered_df[col] = filtered_df[col] * 100

    elif table_id == 'output_6':
        filtered_df = filtered_df[filtered_df['Metric'].isin(['Primary Rental Units', 'Secondary Rental Units'])]
        filtered_df['Header to be deleted'] = 'Number of primary and secondary rental units in 2021'

    elif ((table_id == 'output_9') or (table_id == 'output_10a') or (table_id == 'output_10b')):
        rate_columns = filtered_df.columns[filtered_df.columns.str.endswith('Rate')]
        # Update headship rate to 1, if greater than 1
        filtered_df[rate_columns] = filtered_df[rate_columns].mask(filtered_df[rate_columns] > 1, 1)

        if (table_id == 'output_10a') or (table_id == 'output_10b'):
            new_header = ['Household Suppression by age of Primary household maintainer -\
                       following BC HNR methodology'] * (len(filtered_df.columns))
            filtered_df = filtered_df.replace('75plus', '75 and older')
        else:
            filtered_df['Change in Headship Rate between 2016 and 2021'] = filtered_df['Change in Headship Rate between 2016 and 2021'] * 100
            new_header = ['Changes in Headship rate of Primary Household Maintainer (PHM) \
                          by age between 2016 and 2021'] * (len(filtered_df.columns))
            filtered_df = filtered_df[filtered_df['Age']!= '75plus'].replace('75to84', '75-84').replace('85plus', '85 and older')

        filtered_df.columns = pd.MultiIndex.from_tuples(zip(new_header, filtered_df.columns))
        filtered_df = filtered_df.replace('15to24', '15-24').replace('25to34', '25-34'). \
            replace('35to44', '35-44').replace('45to54', '45-54').replace('55to64', '55-64'). \
            replace('65to74', '65-74')
        
    elif ((table_id == 'output_4a') or (table_id == 'output_4b')):
        if table_id == 'output_4a':
            new_header = ['Housing starts by structural type (2016-2023)'] * (len(filtered_df.columns))
        else:
            new_header = ['Housing starts by tenure (2016-2023)'] * (len(filtered_df.columns))

        filtered_df.columns = pd.MultiIndex.from_tuples(zip(new_header, filtered_df.columns))

    elif table_id == 'output_8':
        filtered_df = filtered_df.melt(id_vars=filtered_df.columns[:5], var_name="Metric", value_name="2021")

    else:
        filtered_df = filtered_df

    if (table_id == 'output_1a') or (table_id == 'output_1b'):
        table = filtered_df.iloc[:, 2:]
    else:
        table = filtered_df.iloc[:, 5:]

    for index, row in table.iterrows():
        if any('Total' in str(cell) or 'Average' in str(cell) for cell in row.values):
            continue
        else:
            table.loc[index] = row.fillna('n/a')

    return table


def number_formatting(df, col_list, precision, conditions={}):
    def format_row(row):
        if all(conditions[col](row[col]) for col in conditions if col in row):
            for col in col_list:
                if precision == 0:
                    row[col] = '{0:,.0f}'.format(row[col]) if pd.notnull(row[col]) and row[col] != 'n/a' else row[col]
                elif precision == 1:
                    row[col] = '{0:,.1f}'.format(row[col]) if pd.notnull(row[col]) and row[col] != 'n/a' else row[col]    
                else:
                    row[col] = '{0:,.2f}'.format(row[col]) if pd.notnull(row[col]) and row[col] != 'n/a' else row[col]
        return row

    return df.apply(format_row, axis=1)


def percent_formatting(df, col_list, mult_flag, conditions={}):
    def format_row(row):
        # Check if row meets all conditions before applying formatting
        if all(conditions[col](row[col]) for col in conditions if col in row):
            for col in col_list:
                if mult_flag == 0:
                    row[col] = f"{row[col]:.0f}%" if pd.notna(row[col]) and row[col] != 'n/a' else row[col]
                elif mult_flag == 1:
                    row[col] = f"{row[col] * 100:.1f}%" if pd.notna(row[col]) and row[col] != 'n/a' else row[col]
                elif mult_flag == 2:
                    row[col] = f"{row[col]:.1f}%" if pd.notna(row[col]) and row[col] != 'n/a' else row[col]
                else:
                    row[col] = f"{row[col] * 100:.2%}" if pd.notnull(row[col]) and row[col] != 'n/a' else row[col]
        return row

    return df.apply(format_row, axis=1)


# Callback for storing selected areas and area scale level

@callback(
    Output('output_1a', 'columns'),
    Output('output_1a', 'data'),
    Output('output_1a', 'style_data_conditional'),
    Output('output_1a', 'style_cell_conditional'),
    Output('output_1a', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_1a', 'selected_columns'),
)
def update_output_1a(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_1a, 'output_1a')
    
    table.drop_duplicates(inplace=True)
    percent_conditions = {'Data': lambda x: x == 'Percentage of all HHs'}
    table = percent_formatting(table, ['Value'], mult_flag=1, conditions=percent_conditions)

    number_conditions = {'Data': lambda x: x == 'Total'}
    table = number_formatting(table, ['Value'], 0, conditions=number_conditions)

    table = table[['Characteristic', 'Data', 'Value']].sort_values(
        by=['Characteristic', 'Data'], ascending=False).replace('a ', 'an existing ', regex=True)
    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    #TODO: Use this if alignment is required as per the doc
    # style_cell_conditional = [
    #                             {
    #                                 'if': {'column_id': table_columns[i]['id']},
    #                                 'backgroundColor': columns_color_fill[1],
    #                                 'textAlign': 'left' if i < 2 else 'right',  # Left align for first 2 columns, right for the 3rd
    #                                 'maxWidth': max_width
    #                             }
    #                             for i, max_width in enumerate(["100px", "50px", "25px"])
    #                         ]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    
    new_data_style = [
            {
                'if': {'row_index': i, 'column_id': 'Characteristic'},
                'backgroundColor': '#b0e6fc',
                'color': '#b0e6fc',
                'border-top': 'none',
                'rowSpan': 2

            } for i in [1, 3]
        ]
    
    #TODO: Use this if alignment is required as per the doc
    # new_header_style = [
    #     {
    #     'if': {'column_id': col['id']},  
    #     'textAlign': 'right' if col['id'] == table_columns[-1]['id'] else 'left'
    #     }
    #     for col in table_columns
    # ]

    style_data_conditional.extend(new_data_style)
    # style_header_conditional.extend(new_header_style)

    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional

@callback(
    Output('output_1b', 'columns'),
    Output('output_1b', 'data'),
    Output('output_1b', 'style_data_conditional'),
    Output('output_1b', 'style_cell_conditional'),
    Output('output_1b', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_1b', 'selected_columns'),
)
def update_output_1b(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_1b, 'output_1b')
    
    table.drop_duplicates(inplace=True)
    percent_conditions = {'Data': lambda x: x == 'Percentage of all HHs'}
    table = percent_formatting(table, ['Value'], mult_flag=1, conditions=percent_conditions)

    number_conditions = {'Data': lambda x: x == 'Total'}
    table = number_formatting(table, ['Value'], 0, conditions=number_conditions)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)

    table = table[['Characteristic', 'Data', 'Value']].sort_values(
        by=['Characteristic', 'Data'], ascending=False).replace('a ', 'an existing or under construction ', regex=True)
    

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    #TODO: Use this if alignment is required as per the doc
    # style_cell_conditional = [
    #                             {
    #                                 'if': {'column_id': table_columns[i]['id']},
    #                                 'backgroundColor': columns_color_fill[1],
    #                                 'textAlign': 'left' if i < 2 else 'right',  # Left align for first 2 columns, right for the 3rd
    #                                 'maxWidth': max_width
    #                             }
    #                             for i, max_width in enumerate(["100px", "50px", "25px"])
    #                         ]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    new_data_style = [
            {
                'if': {'row_index': i, 'column_id': 'Characteristic'},
                'backgroundColor': '#b0e6fc',
                'color': '#b0e6fc',
                'border-top': 'none',
                'rowSpan': 2

            } for i in [1, 3]
        ]
    
    #TODO: Use this if alignment is required as per the doc
    # new_header_style = [
    #     {
    #     'if': {'column_id': col['id']},  
    #     'textAlign': 'right' if col['id'] == table_columns[-1]['id'] else 'left'
    #     }
    #     for col in table_columns
    # ]


    style_data_conditional.extend(new_data_style)
    # style_header_conditional.extend(new_header_style)

    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('output_2a', 'columns'),
    Output('output_2a', 'data'),
    Output('output_2a', 'style_data_conditional'),
    Output('output_2a', 'style_cell_conditional'),
    Output('output_2a', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_2a', 'selected_columns'),
)
def update_output_2a(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_2, 'output_2a')
    table = table[table['Metric'] == 'Avg Monthly Rent']
    
    table.drop_duplicates(inplace=True)

    if not table.empty:
        table.loc[table['Metric'] == 'Avg Monthly Rent', table.columns[1:]] = \
        table.loc[table['Metric'] == 'Avg Monthly Rent', table.columns[1:]].applymap(lambda x: f"${x:,.0f}")

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': ''}).replace('Avg Monthly Rent' , 'Avg Monthly Rent ($)')

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "50px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('output_2b', 'columns'),
    Output('output_2b', 'data'),
    Output('output_2b', 'style_data_conditional'),
    Output('output_2b', 'style_cell_conditional'),
    Output('output_2b', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_2b', 'selected_columns'),
)
def update_output_2b(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_2, 'output_2b')

    table.drop_duplicates(inplace=True)
    percent_conditions = {'Metric': lambda x: x == '% Change in Avg Rent'}
    table = percent_formatting(table, table.columns[1:], mult_flag=2, conditions=percent_conditions)

    if not table.empty:
        table.loc[table['Metric'] == 'Change in Avg Rent', table.columns[1:]] = \
        table.loc[table['Metric'] == 'Change in Avg Rent', table.columns[1:]].applymap(
        lambda x: f"+${x:,.0f}" if x > 0 else (f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}")
        )
        table.loc[table['Metric'] == '% Change in Avg Rent', table.columns[1:]] = \
            table.loc[table['Metric'] == '% Change in Avg Rent', table.columns[1:]].applymap(
            lambda x: f"+{x}" if float(x[:-1]) > 0 else f"{x}"
        )
    print(table.dtypes, table)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': ''}).replace('% Change in Avg Rent',
                                                         'Percentage change in Average Monthly Rent (%)').replace(
        'Change in Avg Rent', 'Change in Average Monthly Rent ($)'
    ).sort_values(by=[''], ascending=True)

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('graph_2b_1', 'figure'),
    Output('graph_2b_2', 'figure'),

    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_2b', 'selected_columns'),
)
def update_geo_figure_2b(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale, refresh)

    # Generating table
    table = table_generator(geo, output_2, 'output_2b')
    table.drop_duplicates(inplace=True)

    fig1 = go.Figure()
    y_vals1 = table.loc[table['Metric'] == "Change in Avg Rent"].values.flatten().tolist()[1:]

    fig1.add_trace(go.Bar(
        x=table.columns[1:],
        y=y_vals1,
        marker_color='#39c0f7',
        customdata=[f"+${x:,.0f}" if x > 0 else (f"-${abs(x):,.0f}" if x < 0 else f"${x:,.0f}") for x in y_vals1],
        hovertemplate=' Year: %{x} <br> ' + '%{customdata}<extra></extra>'
    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        showlegend=False,
        legend=dict(font=dict(size=9)),
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Change in Average Monthly Rent ($) (2016-2023) {geo}',
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=10)
    )
    fig1.update_yaxes(
        tickfont=dict(size=10),
        tickformat = ".0f",
        tickprefix="$",  # Adds % sign to each tick
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Change in Average Monthly Rent ($)'
    )

    y_vals2 = table.loc[table['Metric'] == "% Change in Avg Rent"].values.flatten().tolist()[1:]
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=table.columns[1:],
        y=y_vals2,
        marker_color='#3eb549',
        customdata = [f"+{x:.1f}%" if x > 0 else f"{x:.1f}%" for x in y_vals2],
        hovertemplate=' Year: %{x} <br> ' + '%{customdata}<extra></extra>'
    ))

    # Plot layout settings
    fig2.update_layout(
        # width = 900,
        showlegend=False,
        legend=dict(font=dict(size=9)),
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Percentage change in Average Monthly Rent ($) (2016-2023) {geo}',
        legend_title="Income",
    )
    fig2.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=10)
    )
    fig2.update_yaxes(
        tickfont=dict(size=10),
        tickformat = ".0f",
        ticksuffix="%",  # Adds % sign to each tick
        # fixedrange = True,
        title='Percentage change in Average Monthly Rent ($)'
    )

    return fig1, fig2




@callback(
    Output('output_3a', 'columns'),
    Output('output_3a', 'data'),
    Output('output_3a', 'style_data_conditional'),
    Output('output_3a', 'style_cell_conditional'),
    Output('output_3a', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_3a', 'selected_columns'),
)
def update_output_3a(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)
    # Generating table
    table = table_generator(geo, output_3, 'output_3a')
    #table.drop_duplicates(inplace=True)
    table = percent_formatting(table, table.columns[1:], 1)
    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': ''}).replace('Vacancy Rate','Vacancy Rate %')
    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [  # put in function?
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    return table_columns, table.to_dict('records'), style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('output_3b', 'columns'),
    Output('output_3b', 'data'),
    Output('output_3b', 'style_data_conditional'),
    Output('output_3b', 'style_cell_conditional'),
    Output('output_3b', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_3b', 'selected_columns'),
)
def update_output_3b(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)
    # Generating table
    table = table_generator(geo, output_3, 'output_3b')

    if not table.empty:
        table.loc[:, table.columns[1:]] = table.loc[:, table.columns[1:]].applymap(
            lambda x: f"+{x:,.1f}" if x > 0 else f"{x:,.1f}"
        )

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': ''}).replace('Change in Vacancy Rate','Change in Vacancy Rate (percentage points)')
    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [  # put in function?
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    return table_columns, table.to_dict('records'), style_data_conditional, style_cell_conditional, style_header_conditional

# 2 bar charts for output 3
@callback(
    Output('graph_3a', 'figure'),
    Output('graph_3b', 'figure'),

    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_3a', 'selected_columns'),
)
def update_geo_figure_3ab(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale)
    # Generating table
    table_VacancyRate = table_generator(geo, output_3, 'output_3a')
    table_ChangeInVacancyRate = table_generator(geo, output_3, 'output_3b')

    # Generating plot
    fig1 = go.Figure()
    y_vals1 = [y * 100 for y in table_VacancyRate.values.flatten().tolist()[1:]]
    y_vals2 = table_ChangeInVacancyRate.values.flatten().tolist()[1:]

    fig1.add_trace(go.Bar(
        x=table_VacancyRate.columns[1:],
        y=y_vals1,
        marker_color='#39c0f7',
        hovertemplate=' Year: %{x} <br> ' + '%{y:,.2f}%<extra></extra>'
    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        showlegend=False,
        legend=dict(font=dict(size=9)),
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Vacancy Rates (2016-2023) {geo}',
        legend_title="TBD",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=10)
    )
    fig1.update_yaxes(
        tickfont=dict(size=10),
        tickformat = ".0f",
        ticksuffix="%",  # Adds % sign to each tick
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Vacancy Rates (%)'
    )

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=table_ChangeInVacancyRate.columns[1:],
        y=y_vals2,
        marker_color='#3eb549',
        customdata = [f"+{x:,.1f}" if x > 0 else f"{x:,.1f}" for x in y_vals2],
        hovertemplate=' Year: %{x} <br> ' + '%{customdata}<extra></extra>' 
    ))

    # Plot layout settings
    fig2.update_layout(
        # width = 900,
        showlegend=False,
        legend=dict(font=dict(size=9)),
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Change in Vacancy Rates (percentage points) (2016-2023) {geo}',
    )
    fig2.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=10)
    )
    fig2.update_yaxes(
        tickfont=dict(size=10),
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Change in vacancy rates (pp)'
    )

    return fig1, fig2

# tables for data point 4 housing starts
@callback(
    Output('output_4a', 'columns'),
    Output('output_4a', 'data'),
    Output('output_4a', 'style_data_conditional'),
    Output('output_4a', 'style_cell_conditional'),
    Output('output_4a', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_4a', 'selected_columns'),
)
def update_output_4a(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_4a, 'output_4a')
    table.drop_duplicates(inplace=True)

    table = number_formatting(table, list(table.columns[1:]), 0)
    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': ''})

    # Generating callback output to update table

    table_columns = [{"name": [geo, col1, col2], "id": f"{col1}_{col2}"} for col1, col2 in table.columns]
    table_data = [
        {
            **{f"{x1}_{x2}": y for (x1, x2), y in data},
        }
        for (n, data) in [
            *enumerate([list(x.items()) for x in table.T.to_dict().values()])
        ]
    ]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "50px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    new_data_style = [
                         {
                             'if': {'row_index': len(table) - 1, 'column_id': j['id']},
                             'backgroundColor': '#39C0F7',
                             'color': '#000000',
                             'fontWeight': 'bold'

                         } for j in table_columns

                     ]
    style_data_conditional.extend(new_data_style)

    return table_columns, table_data, style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('output_4b', 'columns'),
    Output('output_4b', 'data'),
    Output('output_4b', 'style_data_conditional'),
    Output('output_4b', 'style_cell_conditional'),
    Output('output_4b', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_4b', 'selected_columns'),
)
def update_output_4b(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)
    # Generating table
    table = table_generator(geo, output_4b, 'output_4b')
    table = number_formatting(table, list(table.columns[1:]), 0)

    table.drop_duplicates(inplace=True)
    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': ''})

    # Generating callback output to update table

    table_columns = [{"name": [geo, col1, col2], "id": f"{col1}_{col2}"} for col1, col2 in table.columns]
    table_data = [
        {
            **{f"{x1}_{x2}": y for (x1, x2), y in data},
        }
        for (n, data) in [
            *enumerate([list(x.items()) for x in table.T.to_dict().values()])
        ]
    ]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    new_data_style = [
                         {
                             'if': {'row_index': len(table) - 1, 'column_id': j['id']},
                             'backgroundColor': '#39C0F7',
                             'color': '#000000',
                             'fontWeight': 'bold'

                         } for j in table_columns

                     ]
    style_data_conditional.extend(new_data_style)

    return table_columns, table_data, style_data_conditional, style_cell_conditional, style_header_conditional


# stacked bar chart for output4a
@callback(
    Output('graph_4a', 'figure'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_4a', 'selected_columns'),
)
def update_geo_figure_4a(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale)
    # Generating table
    table = table_generator(geo, output_4a, 'output_4a')
    # Generating plot
    fig1 = go.Figure()
    y_vals1 = table[table[table.columns[0]]=='Apartment'].values.flatten().tolist()[1:]
    y_vals2 = table[table[table.columns[0]]=='Row'].values.flatten().tolist()[1:]
    y_vals3 = table[table[table.columns[0]]=='Semi-detached'].values.flatten().tolist()[1:]
    y_vals4 = table[table[table.columns[0]]=='Single-detached'].values.flatten().tolist()[1:]

    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals1,
        name= 'Apartment',
        marker_color = hh_colors[3],
        hovertemplate=' %{x} Apartments - <br>' + ' %{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals2,
        name='Row',
        marker_color=hh_colors[2],
        hovertemplate=' %{x} Row - <br>' + ' %{y:,.0f}<extra></extra>'

    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals3,
        name='Semi-detached',
        marker_color = hh_colors[1],
        hovertemplate=' %{x} Semi-detached - <br>' + ' %{y:,0f}<extra></extra>'

    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals4,
        name='Single-detached',
        marker_color= hh_colors[0],
        hovertemplate=' %{x} Single-detached - <br>' + ' %{y:,0f}<extra></extra>'

    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        showlegend=True,
        legend=dict(font=dict(size=9)),
        barmode='stack',
        # yaxis=dict(autorange="reversed"),
        #color_discrete_sequence=hh_colors,
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Housing Starts by Structure Type (2016-2023) {geo}',
        legend_title="Structure Type",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=10)
    )
    fig1.update_yaxes(
        tickfont=dict(size=10),
        tickformat = ",.0f",
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Housing Starts'
    )

    return fig1


# stacked bar chart for output4b
@callback(
    Output('graph_4b', 'figure'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_4b', 'selected_columns'),
)
def update_geo_figure_4b(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale)
    # Generating table
    table = table_generator(geo, output_4b, 'output_4b')
    # Generating plot
    fig1 = go.Figure()
    y_vals1 = table[table[table.columns[0]]=='Owner'].values.flatten().tolist()[1:]
    y_vals2 = table[table[table.columns[0]]=='Rental'].values.flatten().tolist()[1:]
    y_vals3 = table[table[table.columns[0]]=='Condo'].values.flatten().tolist()[1:]
    y_vals4 = table[table[table.columns[0]]=='Co-op'].values.flatten().tolist()[1:]
    y_vals5 = table[table[table.columns[0]] == 'N/A'].values.flatten().tolist()[1:]

    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals1,
        name= 'Owner',
        marker_color= '#39c0f7',
        hovertemplate=' %{x} Owner - <br>' + ' %{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals2,
        name='Rental',
        marker_color= "#88d9fa",
        hovertemplate=' %{x} Rental - <br>' + ' %{y:,.0f}<extra></extra>'

    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals3,
        name='Condo',
        marker_color= "#D7f3fd",
        hovertemplate=' %{x} Condo - <br>' + ' %{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals4,
        name='Co-op',
        marker_color= "#099DD7",
        hovertemplate=' %{x} Co-op - <br>' + ' %{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals5,
        name='N/A',
        marker_color= "#044762",
        hovertemplate=' %{x} N/A - <br>' + ' %{y:,.0f}<extra></extra>'
    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        showlegend=True,
        legend=dict(font=dict(size=9)),
        barmode='stack',
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Housing Starts by Tenure (2016-2023) {geo}',
        legend_title="Tenure",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=10)
    )
    fig1.update_yaxes(
        tickfont=dict(size=10),
        tickformat = ",.0f",
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Housing Starts'
    )

    return fig1

# tables for data point 5 households in CHN by tenure
@callback(
    Output('output_5a', 'columns'),
    Output('output_5a', 'data'),
    Output('output_5a', 'style_data_conditional'),
    Output('output_5a', 'style_cell_conditional'),
    Output('output_5a', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_5a', 'selected_columns'),
)
def update_output_5a(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_5a, 'output_5a')
    table = number_formatting(table, ['2016', '2021'], 0)

    if not table.empty:
        table.loc[:, ['2021 - 2016']] = table.loc[:, ['2021 - 2016']].applymap(
            lambda x: f"+{x:,.0f}" if x > 0 else (f"-{abs(x):,.0f}" if x < 0 else f"{x:,.0f}")
        )
    table.drop_duplicates(inplace=True)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': 'Number of households in CHN', 
                                   '2021 - 2016': 'Change between 2016 and 2021'}
                                   ).replace('Owner', 'Owner-occupied'
                                             ).replace('Renter', 'Renter-occupied'
                                                       )
    table = table.drop(['% change in # of HH in CHN by tenure'], axis=1)

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "80px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional

# TABLE 5b
@callback(
    Output('output_5b', 'columns'),
    Output('output_5b', 'data'),
    Output('output_5b', 'style_data_conditional'),
    Output('output_5b', 'style_cell_conditional'),
    Output('output_5b', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_5b', 'selected_columns'),
)
def update_output_5b(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)
    # Generating table
    table = table_generator(geo, output_5b, 'output_5b')

    table = percent_formatting(table, ['2016', '2021'], 1)
    table.drop_duplicates(inplace=True)
    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': 'Rate of CHN (%)'}).replace(
        'Owner', 'Owner-occupied HH').replace('Renter', 'Renter-occupied HH')
    
    table = table.drop('2021 - 2016', axis=1)

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


# grouped bar chart for output5a
@callback(
    Output('graph_5a', 'figure'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_5a', 'selected_columns'),
)
def update_geo_figure_5a(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale)
    # Generating table
    table = table_generator(geo, output_5a, 'output_5a')
    # Generating plot
    fig1 = go.Figure()
    y_vals1 = table['2016'].values.flatten().tolist()
    y_vals2 = table['2021'].values.flatten().tolist()

    fig1.add_trace(go.Bar(
        x=["Owner", "Renter"],
        y=y_vals1,
        name= '2016',
        marker_color='#39c0f7',
        hovertemplate='2016 %{x} - <br>' + '%{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=["Owner",  "Renter"],
        y=y_vals2,
        name='2021',
        marker_color='#3eb549',
        hovertemplate='2021 %{x} - <br>' + '%{y:,.0f}<extra></extra>'
    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        showlegend=True,
        legend=dict(font=dict(size=9)),
        barmode='group',
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Number of Households in CHN by tenure {geo}',
        legend_title="Year",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Owners vs. Renters',
        tickfont=dict(size=10)
    )
    fig1.update_yaxes(
        tickfont=dict(size=10),
        tickformat = ",.0f",
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Number of Households'
    )

    return fig1

# grouped bar chart for output5b
@callback(
    Output('graph_5b', 'figure'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_5b', 'selected_columns'),
)
def update_geo_figure_5b(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale)
    # Generating table
    table = table_generator(geo, output_5b, 'output_5b')
    # Generating plot
    fig1 = go.Figure()
    y_vals1 = [y * 100 for y in table['2016'].values.flatten().tolist()]
    y_vals2 = [y * 100 for y in table['2021'].values.flatten().tolist()]
    

    fig1.add_trace(go.Bar(
        x=["Owner", "Renter"],
        y=y_vals1 * 100,
        name= '2016',
        marker_color= '#39c0f7',
        hovertemplate='2016 %{x} - <br>' + '%{y:.1f}%<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=["Owner",  "Renter"],
        y=y_vals2  * 100,
        name='2021',
        marker_color='#3eb549',
        hovertemplate='2021 %{x} - <br>' + '%{y:.1f}%<extra></extra>'
    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        showlegend=True,
        legend=dict(font=dict(size=9)),
        barmode='group',
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Rate of CHN by tenure {geo}',
        legend_title="Year",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Owners vs. Renters',
        tickfont=dict(size=10)
    )
    fig1.update_yaxes(
        tickfont=dict(size=10),
        tickformat = ".0f",
        ticksuffix="%",  # Adds % sign to each tick
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Number of Households'
    )

    return fig1

# TABLE 6
@callback(
    Output('output_6', 'columns'),
    Output('output_6', 'data'),
    Output('output_6', 'style_data_conditional'),
    Output('output_6', 'style_cell_conditional'),
    Output('output_6', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_6', 'selected_columns'),
)
def update_output_6(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)
    # Generating table
    table = table_generator(geo, output_6, 'output_6')

    table = number_formatting(table, ['2021'], 0)
    #table = percent_formatting(table, ['% change in # of HH in CHN by tenure'], 0)
    #table.drop_duplicates(inplace=True)
    #style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)

    table = table[['Header to be deleted', 'Metric', '2021']]
    table = table.rename(columns={'Metric': '', 'Header to be deleted': ' '}).replace(' Rental Units', '', regex=True)

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    style_data_conditional = []
    for i in range(len(table)):
        row_style = {
            'if': {'row_index': i},
            'backgroundColor': '#b0e6fc',
            'color': '#000000',
            'border': '1px solid #002145'
        }

        style_data_conditional.append(row_style)
    new_data_style = [
            {
                'if': {'row_index': 1, 'column_id': ' '},
                'backgroundColor': '#b0e6fc',
                'color': '#b0e6fc',
                'border-top': 'none',
                'rowSpan': 2

            }
        ]
    style_data_conditional.extend(new_data_style)

    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


# pie chart for ouput 6
@callback(
    Output('graph_6', 'figure'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_6', 'selected_columns'),
)
def update_geo_figure_6(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale)
    # Generating table
    table = table_generator(geo, output_6, 'output_6')
    # Generating plot
    fig1 = go.Figure()

    fig1.add_trace(go.Pie(
                        labels = table['Metric'],
                        values = table['2021'],
                        textinfo = 'percent',
                        pull=[0.1, 0],
                        marker_colors=['#39c0f7', '#3eb549'],
                        hovertemplate=' %{label}</b><br>' + 'Value: %{value:,.0f}<br>' + '<extra></extra>'
                ))

    # Plot layout settings
    fig1.update_layout(
                    # width = 900,
                    showlegend = True,
                    legend=dict(font = dict(size = 12)),
                    # yaxis=dict(autorange="reversed"),
                    modebar_color = modebar_color,
                    modebar_activecolor = modebar_activecolor,
                    plot_bgcolor='#F8F9F9',
                    title = f'Share of Primary and Secondary Rental units {geo}',
                    legend_title = "Share",
                    )
    return fig1


@callback(
    Output('output_7', 'columns'),
    Output('output_7', 'data'),
    Output('output_7', 'style_data_conditional'),
    Output('output_7', 'style_cell_conditional'),
    Output('output_7', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_7', 'selected_columns'),
)
def update_output_7(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_7, 'output_7')

    table.drop_duplicates(inplace=True)

    if not table.empty:
        table.loc[len(table)] = ['Total rental units (subsidized + unsubsidized)', table['2021'].sum()]

    table = number_formatting(table, table.columns[1:], 0)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': ''}).replace(
        'Private rental market housing units',
        'Number of private (i.e. unsubsidized) rental market housing units').replace(
        'Subsidized rental housing units', 'Number of rental housing units that are subsidized')
    
    

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "50px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    
    new_data_style = generate_additional_data_style(table, table_columns)
    style_data_conditional.extend(new_data_style)

    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('pie_7', 'figure'),

    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_7', 'selected_columns'),
)
def update_geo_figure_7(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale, refresh)

    # Generating table
    table = table_generator(geo, output_7, 'output_7')
    table.drop_duplicates(inplace=True)

    fig1 = go.Figure()

    fig1.add_trace(go.Pie(
        labels=table['Metric'],
        values=table['2021'],
        textinfo='percent',
        pull=[0.1, 0],
        marker_colors=['#39c0f7', '#3eb549'],
        hovertemplate=' %{label}</b><br>' + 'Value: %{value:,.0f}<br>' + '<extra></extra>'
    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        showlegend=True,
        legend=dict(font=dict(size=12)),
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Share for subsidized vs unsubsidized rental units {geo}',
        legend_title="Share",
    )

    return fig1


@callback(
    Output('output_8', 'columns'),
    Output('output_8', 'data'),
    Output('output_8', 'style_data_conditional'),
    Output('output_8', 'style_cell_conditional'),
    Output('output_8', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_8', 'selected_columns'),
)
def update_output_8(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_8, 'output_8')

    number_conditions = {'Metric': lambda x: x == 'Renters (unsubsidized)'}
    table = number_formatting(table, table.columns[1:], 0, conditions=number_conditions)

    table.drop_duplicates(inplace=True)
    conditions = {'Metric': lambda x: x == '% of Total (Unsubsidized)'}
    table = percent_formatting(table, table.columns[1:], mult_flag=1, conditions=conditions)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Metric': ''}).replace(
        'Renters (unsubsidized)',
        'Number of occupied housing units that are below-market rent in the private market').replace(
        '% of Total (Unsubsidized)', 'Percentage of occupied housing units that are below-market rent in the private market')

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "50px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('output_9', 'columns'),
    Output('output_9', 'data'),
    Output('output_9', 'style_data_conditional'),
    Output('output_9', 'style_cell_conditional'),
    Output('output_9', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_9', 'selected_columns'),
)
def update_output_9(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_9, 'output_9')

    table.drop_duplicates(inplace=True)
    # print(list(table.columns[[1, 2, 4, 5]]))

    table = percent_formatting(table, (table.columns[::3][1:]).tolist(), mult_flag=1)
    table = number_formatting(table, list(table.columns[[1, 2, 4, 5]]), 0)

    if not table.empty:
        table.loc[:, [table.columns[-1]]] = table.loc[:, [table.columns[-1]]].applymap(
            lambda x: f"+{x:,.1f}" if x > 0 else (f"-{abs(x):,.1f}" if x < 0 else f"{x:,.1f}")
        )

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Age': 'Age Group'})
    table.columns = pd.MultiIndex.from_tuples([
        (lvl1, lvl2[:-4] + 'Rate*' if lvl2.endswith('Rate') else lvl2) for lvl1, lvl2 in table.columns
    ])
    # Generating callback output to update table

    table_columns = [{"name": [geo, col1, col2], "id": f"{col1}_{col2}"} for col1, col2 in table.columns]
    table_data = [
        {
            **{f"{x1}_{x2}": y for (x1, x2), y in data},
        }
        for (n, data) in [
            *enumerate([list(x.items()) for x in table.T.to_dict().values()])
        ]
    ]

    #TODO: Use this if alignment is required as per the doc
    # style_cell_conditional = generate_style_cell_conditional(table_columns, generic_style=0)
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "75px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    #TODO: Use this if alignment is required as per the doc
    # style_header_conditional = generate_style_header_conditional(table, multi_header=True, extend=True)
    

    return table_columns, table_data, style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('graph_9_1', 'figure'),
    Output('graph_9_2', 'figure'),

    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_9', 'selected_columns'),
)
def update_geo_figure_9(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale, refresh)

    # Generating table
    table = table_generator(geo, output_9, 'output_9')
    table.drop_duplicates(inplace=True)

    fig1 = go.Figure()
    y_vals1_1 = [y * 100 for y in table[table.columns[3]].tolist()]
    y_vals1_2 = [y * 100 for y in table[table.columns[6]].tolist()]

    fig1.add_trace(go.Bar(
        x=table[table.columns[0]].unique(),
        y=y_vals1_1,
        name='2016',
        marker_color='#39c0f7',
        hovertemplate=' Age Group: %{x} <br> ' + '%{y:.1f}%<extra></extra>'
    ))

    fig1.add_trace(go.Bar(
        x=table[table.columns[0]].unique(),
        y=y_vals1_2,
        name='2021',
        marker_color='#3eb549',
        hovertemplate=' Age Group: %{x} <br> ' + '%{y:.1f}%<extra></extra>'
    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        barmode='group',
        plot_bgcolor='#F8F9F9',
        title=f'Headship rates by A ge (2016 & 2021) {geo}',
        legend_title="Headship Rate"
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Age Group',
        tickfont=dict(size=10)
    )
    fig1.update_yaxes(
        tickfont=dict(size=10),
        tickformat = ".0f",
        ticksuffix="%",  # Adds % sign to each tick
        # fixedrange = True,
        title='Headship Rate'
    )

    y_vals2 = table[table.columns[7]].tolist()
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=table[table.columns[0]].unique(),
        y=y_vals2,
        marker_color='#39c0f7',
        customdata=[f"+{y:.1f}" if y > 0 else f"{y:.1f}" for y in y_vals2],
        hovertemplate=' Age Group: %{x} <br> ' + '%{customdata}<extra></extra>'
    ))

    # Plot layout settings
    fig2.update_layout(
        # width = 900,
        showlegend=False,
        legend=dict(font=dict(size=9)),
        # yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#F8F9F9',
        title=f'Percentage Point Change to headship rates by age (2016 & 2021) {geo}',
        legend_title="Headship rate",
    )
    fig2.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Age Group',
        tickfont=dict(size=10)
    )
    fig2.update_yaxes(
        tickfont=dict(size=10),
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Change in headship rate (pp)'
    )

    return fig1, fig2


@callback(
    Output('output_10a', 'columns'),
    Output('output_10a', 'data'),
    Output('output_10a', 'style_data_conditional'),
    Output('output_10a', 'style_cell_conditional'),
    Output('output_10a', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_10a', 'selected_columns'),
)
def update_output_10a(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_10a, 'output_10a')

    table.drop_duplicates(inplace=True)
    # pdb.set_trace()

    table = percent_formatting(table, (table.columns[::3][1:]).tolist(), mult_flag=1, conditions={})
    table = number_formatting(table, list(table.columns[[1, 2, 4, 5]]), 0)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Age': 'Age Group'})
    table.columns = pd.MultiIndex.from_tuples(
        [(col[0] + " (table 1 of 2)", col[1]) for col in table.columns]
    )

    table.columns = pd.MultiIndex.from_tuples([
        (lvl1, lvl2[:-4] + 'Rate*' if lvl2.endswith('Rate') else lvl2) for lvl1, lvl2 in table.columns
    ])
    # Generating callback output to update table

    table_columns = [{"name": [geo, col1, col2], "id": f"{col1}_{col2}"} for col1, col2 in table.columns]
    table_data = [
        {
            **{f"{x1}_{x2}": y for (x1, x2), y in data},
        }
        for (n, data) in [
            *enumerate([list(x.items()) for x in table.T.to_dict().values()])
        ]
    ]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "50px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    #TODO: Use this if alignment is required as per the doc
    # style_cell_conditional = [
    #                             {
    #                                 'if': {'column_id': table_columns[i]['id']},
    #                                 'backgroundColor': columns_color_fill[1],
    #                                 'textAlign': 'left' if i < 1 else 'right',  
    #                             }
    #                             for i in range(len(table_columns))
    #                         ]
    # new_header_style = [
    #     {
    #     'if': {'column_id': col['id']},  
    #     'textAlign': 'left' if col['id'] == table_columns[0]['id'] else 'right'
    #     }
    #     for col in table_columns
    # ]

    # style_header_conditional.extend(new_header_style)
    return table_columns, table_data, style_data_conditional, style_cell_conditional, style_header_conditional


@callback(
    Output('output_10b', 'columns'),
    Output('output_10b', 'data'),
    Output('output_10b', 'style_data_conditional'),
    Output('output_10b', 'style_cell_conditional'),
    Output('output_10b', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_10b', 'selected_columns'),
)
def update_output_10b(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_10b, 'output_10b')

    table.drop_duplicates(inplace=True)
    # print(table.columns[::3])
    table = number_formatting(table, table.columns[1::2].tolist(), 0)
    table = number_formatting(table, list(table.columns[[2]]), 0)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Age': 'Age Group'}).replace('Total', 'Total Suppressed Households')
    table.columns = pd.MultiIndex.from_tuples(
        [(col[0] + " (table 2 of 2)", col[1]) for col in table.columns]
    )

    # Generating callback output to update table

    table_columns = [{"name": [geo, col1, col2], "id": f"{col1}_{col2}"} for col1, col2 in table.columns]
    table_data = [
        {
            **{f"{x1}_{x2}": y for (x1, x2), y in data},
        }
        for (n, data) in [
            *enumerate([list(x.items()) for x in table.T.to_dict().values()])
        ]
    ]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'left',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'center'
                                 } for c in table_columns[1:]
                             ]
    new_data_style = generate_additional_data_style(table, table_columns)
    style_data_conditional.extend(new_data_style)
    return table_columns, table_data, style_data_conditional, style_cell_conditional, style_header_conditional

