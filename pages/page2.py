# Importing Libraries
import pdb

import pandas as pd
import numpy as np
import warnings
import json, os
import plotly.express as px
import plotly.graph_objects as go
import math
from dash import dcc, dash_table, html, Input, Output, ctx, callback
from dash.dash_table.Format import Format, Scheme, Group
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
output_11 = pd.read_sql_table('output_11', engine_new.connect())
output_12 = pd.read_sql_table('output_12', engine_new.connect())
output_13 = pd.read_sql_table('output_13', engine_new.connect())
cma_output_14a = pd.read_sql_table('cma_output_14a', engine_new.connect())
cma_output_14b = pd.read_sql_table('cma_output_14b', engine_new.connect())
cma_output_16 = pd.read_sql_table('cma_output_16', engine_new.connect())

province_code_map = {10 : 'NL', 11 : 'PEI', 12 : 'NS', 13 : 'NB',
                     24 : 'QC', 35 : 'ON', 46: 'MB', 47 : 'SK',
                     48: 'AL', 59: 'BC', 60: 'YT', 61 : 'NT', 62 : 'NU'}

# fetch required data from HART database
df_partners = pd.read_sql_table('partners', engine_old.connect()) #raw table
df_income = pd.read_sql_table('income', engine_old.connect())
updated_csd = pd.read_sql_table('csd_hh_projections', engine_old.connect()).rename(columns=
                                                                                   {'Geo_Code': 'ALT_GEO_CODE_EN'})  # CSD level projections
updated_csd['ALT_GEO_CODE_EN'] = updated_csd['ALT_GEO_CODE_EN'].fillna(0).astype(int).astype(str)


# Fetching province, CD and CSD ids from geography names
df_income['CD_ids'] = df_income['Geography'].str.findall(r"\b\d{4}\b")
df_income['P_ids'] = df_income['Geography'].str.findall(r"\b\d{2}\b")
df_income['CSD_ids'] = df_income['Geography'].str.findall(r"\b\d{7}\b")

# Concatenating all ids for easy join
df_income['ALT_GEO_CODE_EN'] = df_income['CD_ids'].fillna('') + \
                                        df_income['CSD_ids'].fillna('') + \
                                        df_income['P_ids'].fillna('')

df_income['ALT_GEO_CODE_EN'] = df_income['ALT_GEO_CODE_EN'].str[0]
df_income['ALT_GEO_CODE_EN'] = df_income['ALT_GEO_CODE_EN'].fillna(0).astype(str)
df_income.loc[df_income['Geography'].str.contains('Canada', case=False, na=False), 'ALT_GEO_CODE_EN'] = '1'


income_category = df_income.drop(['Geography'], axis=1)
income_category = income_category.rename(columns = {'Formatted Name': 'Geography'})

joined_df = income_category.merge(df_partners, how='left', on='Geography')



# variables for table 14a, 14b
x_base =['Very Low Income', 'Low Income', 'Moderate Income', 
    'Median Income', 'High Income']
x_columns = ['Rent 20% of AMHI', 'Rent 50% of AMHI', 'Rent 80% of AMHI',
             'Rent 120% of AMHI', 'Rent 120% of AMHI']
amhi_range = ['20% or under of AMHI', '21% to 50% of AMHI', '51% to 80% of AMHI', 
    '81% to 120% of AMHI', '121% and more of AMHI']
income_ct = [x + f" ({a})" for x, a in zip(x_base, amhi_range)]



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
cma_long_name_mapping = {'Campbellton (New Brunswick part / partie du Nouveau-Brunswick)': 'Campbellton (NB part)',
                         'Campbellton (partie du Québec / Quebec part)': 'Campbellton (QC part)',
                         'Hawkesbury (partie du Québec / Quebec part)': 'Hawkesbury (QC part)',
                         "Hawkesbury (Ontario part / partie de l'Ontario)": "Hawkesbury (ON part)",
                         "Ottawa - Gatineau (partie du Québec / Quebec part)": "Ottawa - Gatineau (QC part)",
                         "Ottawa - Gatineau (Ontario part / partie de l'Ontario)": "Ottawa - Gatineau (ON part)",
                         "Lloydminster (Saskatchewan part / partie de la Saskatchewan)": "Lloydminster (SK part)",
                         "Lloydminster (Alberta part / partie de l'Alberta)": "Lloydminster (AL part)"
                         }


cma_data = pd.read_sql_table('cma_data', engine_new.connect())
cma_data = cma_data[cma_data['CMAPUID'].notna()]
cma_data['CMAPUID'] = pd.to_numeric(cma_data['CMAPUID'], errors='coerce').astype('Int64').astype(str)
cma_data["CMANAME"] = cma_data["CMANAME"].map(cma_long_name_mapping).fillna(cma_data["CMANAME"])

# cma_data["CMAUID"] = cma_data["CMAUID"].astype(str).str.zfill(3)
cma_data['PRUID'] = cma_data['PRUID'].astype(int)
cma_data['CDUID'] = cma_data['CSDUID'].str[:4].astype(int)

df_region_list = pd.read_sql_table('regioncodes', engine_old.connect())
df_region_list.columns = ['Geo_Code', 'Geography']
df_province_list = pd.read_sql_table('provincecodes', engine_old.connect())
df_province_list.columns = ['Geo_Code', 'Geography']

cma_data["CMANAME"] = cma_data["CMANAME"] + " (CMA, " + cma_data["PRUID"].map(province_code_map) + ")"

cma_data_for_dropdown = cma_data[['CMAPUID', 'CMANAME', 'PRUID', 'CDUID']].merge(df_province_list,
                                                                       left_on='PRUID', right_on='Geo_Code',
                                                                       how='left').rename(columns={
                                                                           'Geo_Code': 'Province_Code', 'Geography': 'Province'
                                                                           })


required_cma_data = cma_data_for_dropdown[['CMAPUID', 'CMANAME', 'CDUID', 'Province_Code', 'Province']].merge(
    df_region_list, left_on='CDUID', right_on='Geo_Code', how='left'
).rename(columns={'CMAPUID': 'Geo_Code', 'CMANAME': 'Geography', 'Geo_Code': 'Region_Code', 'Geography': 'Region'
                  }).drop_duplicates().drop('CDUID', axis=1)

required_cma_data['Province_Code'] = required_cma_data['Province_Code'].astype(str)
required_cma_data['Region_Code'] = required_cma_data['Region_Code'].astype(str)

mapped_geo_code = pd.concat([mapped_geo_code, required_cma_data], axis=0)


cma_output_14 = cma_output_14a.merge(cma_output_14b, on=['Geography', 'ALT_GEO_CODE_EN'],
                                     how='left').merge(required_cma_data[['Geo_Code', 'Province_Code']], 
                                                       left_on='ALT_GEO_CODE_EN', right_on='Geo_Code', how='left') 

cma_output_14["Geography"] = cma_output_14["Geography"] + " (CMA, " + cma_output_14["Province_Code"].astype(int).map(province_code_map) + ")"

cma_output_16["ALT_GEO_CODE_EN"] = cma_output_16["ALT_GEO_CODE_EN"].astype(int).astype(str)
cma_output_16 = cma_output_16.merge(required_cma_data[['Geo_Code', 'Province_Code']], 
                                                       left_on='ALT_GEO_CODE_EN', right_on='Geo_Code', how='left') 

cma_output_16["Geography"] = cma_output_16["Geography"] + " (CMA, " + cma_output_14["Province_Code"].astype(int).map(province_code_map) + ")"

projection_with_cma = pd.concat([updated_csd, cma_output_16], axis=0) #Added cma projection data
# projection_with_cma.to_csv(r"C:\Users\himal\Documents\projected_cma.csv")


final_joined_df = pd.concat([joined_df, cma_output_14], axis=0) # old hart data with CMAs




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

default_value = 'Canada'

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
                         """This dashboard is intended to gather and present some data that is requested for in the Housing Needs Assessment (HNA) template """
                         """created by Housing, Infrastructure and Communities Canada (HICC). Some of the below data points have been created specifically """
                         """to address the HNA template, while others have been gathered from other sources and presented here to make the data more accessible. """
                        """Please note that data for smaller communities may be missing, or subject to inconsistencies that result from random rounding rules """
                        """applied to data derived from the Canadian census. If data is missing from graphs or tables for your selected community, we """
                        """recommend moving up to the next geography level (such as the CD).
                        
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
                             'It also shows the percentage of households within the community that are within 800 or 200 meters of a station. The number of households comes from the 2021 census, but the location of rail stations include all that serve commuter rail networks as of the end of 2024. ',),
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

                                       },
                         style_table={'width': '70%', 'margin': 'left'},
                         css=[{
                                'selector': 'tr:nth-child(2)',
                                'rule':'''
                                        display: None;
                                '''
                              }],

                     ), html.Div(id='output_1a-container'),
                     html.Br()
                     ], className='pg2-output1a-lgeo'
                 ),


                 # 1. HICC Section 3.1.1, data point 1. Output 1b
                     html.Div([
                         html.H6("The following table shows the number of households within 800 meters and 200 meters of existing and under construction rail/light-rail transit stations respectively."
                                 " It also shows the percentage of households within the community that are within 800 or 200 meters of an existing or under construction station. "
                                 "The number of households comes from the 2021 census, but the location of rail stations include all that serve commuter rail networks."),
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
                                       },
                         style_table={'width': '70%', 'margin': 'left'},
                         css=[{
                                'selector': 'tr:nth-child(2)',
                                'rule':'''
                                        display: None;
                                '''
                              }],

                     ), html.Div(id='output_1b-container'),
                     html.Br()
                     ], className='pg2-output1b-lgeo'


                 ),

                 # 2. HICC Section 3.3, data point 9 and 10. Output 9
                 html.Div([
                     html.H4(children=html.Strong('Changes in Head of Household Rates by Age Between 2016 and 2021'),
                             id='visualization9'),
                     html.H5(children='HICC HNA Template: Section 3.3'),
                     html.H6(
                         f'The following chart visualizes the Headship Rate for each age group in 2016 and 2021. Headship rates represent the percentage of people in each age group who were identified as maintaining their household. ',
                         # style={'fontFamily': 'Open Sans, sans-serif'}
                     ),
                     dcc.Graph(id='graph_9_1',
                                   figure=fig1,
                                   config=config,
                                   ),
                     html.H6(children='The following chart shows the change in Headship Rate for each age group between 2016 and 2021 (i.e. Headship Rate in 2021 minus Headship Rate in 2016) by percentage point change. For example, if a headship rate was 10% in 2016 and 9% in 2021, the change would be -1 percentage point.',
                             # style={'fontFamily': 'Open Sans, sans-serif'}
                             ),
                     dcc.Graph(id='graph_9_2',
                               figure=fig2,
                               config=config,
                               ),
                     html.Br(),
                     html.H6('The following table shows the detailed figures for 2016 and 2021, as well as the percentage point change in Headship Rate by age group between 2016 and 2021. '
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
                     html.P(html.I('*Note that the data for small geographies may show there to be more primary household maintainers'
                             ' in a given age range than there are people. This happens in a few geographies where the population is low. This is not a realistic result and can be attributed to Statistics Canada’s random rounding of cell counts.'
                             ' In these cases, the headship rate has been set to equal 100% of the age group.')
                             ),
                     html.Div(id='output_9-container')
                 ], className='pg2-output9-lgeo'
                 ),

                 # 2. HICC Section 3.3, data point 9 and 10. Table 9
                 html.Br(),
                 html.Div([
                     html.H4(html.Strong("Estimated Household Suppression by Age of Primary Household Maintainers")),
                     html.H5("HICC HNA Template: Section 3.3"),
                     # Tables
                     html.H6(children=[
                             f'This section calculates the estimated number of Suppressed Households (households that would have formed if not for housing affordability challenges) according to the methodology used in the ',
                             html.A("Province of British Columbia’s HNR Method,", href='https://www2.gov.bc.ca/assets/gov/housing-and-tenancy/tools-for-government/uploads/hnr_method_technical_guidelines.pdf', target="_blank"),
                             ' specifically Component C: housing units and suppressed household formation.',

                     ]),
                     html.H6('The following table shows the underlying data of Headship rates in 2006 and 2021, which informs the calculation for Suppressed Households in the second table.'),

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

                                       },
                         style_table={'width': '80%', 'margin': 'left'},
                     ),
                     html.P(html.I('''*Note: The data for small geographies may show there to be more primary household maintainers in a given age range than there are people. This happens in a few geographies where the population is low. This is not a realistic result and can be attributed to Statistics Canada’s random rounding of cell counts. In these cases, the headship rate has been set to equal 100% of that age group.''')),
                     html.P(html.I('**Note: The “75 and older” category is used here because data from 2006 uses these categories and does not have an “85 and older” category. For 2021, this category represents the sum of categories “75 to 84” and “85 and older”.')),
                     html.Div(id='output_10a-container')
                 ], className='pg2-output10a-lgeo'
                 ),

                 # 2. HICC Section 3.3, data point 9 and 10. Output 10b
                 html.Br(),
                 html.H6("The following table calculates the estimated Household Suppression by age group in 2021."),
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

                                       },
                         style_table={'width': '80%', 'margin': 'left'},
                     ),
                     html.P(html.I('*Note: The “75 and older” category is used here because data from 2006 uses these categories and does not have an “85 and older” category. For 2021, this category represents the sum of categories “75 to 84” and “85 and older”.')),
                     html.Div(id='output_10b-container'),
                     html.Br()
                 ], className='pg2-output10b-lgeo'
                 ),

                # 3. HICC Section 3.6, data point 14a. Income Cats and Affordable Shelter costs
                html.Div([
                     html.H4(children=html.Strong(f'Core Housing Need')),
                     html.H5(children=html.Strong(f'HICC HNA Template: Section 3.6')),
                     html.H5(children=html.Strong('Income Categories and Affordable Shelter Costs, 2021'),
                             id='visualization14a'),
                     html.H6("Income categories are determined by their relationship with each geography's Area Median Household Income (AMHI). "
                             " The following table shows the range of household incomes and affordable housing costs that make up each income category, in 2020 dollar values. "
                             "It also shows what the portion of total households that fall within each category."),
                     html.H6("Please note that HART does not have the AMHI for CMAs so the income range and affordable shelter cost range for "
                             "each income category is left blank. Households within a CMA are assigned to a given income category based on the "
                             "AMHI of the CSD that the household lives within, which may be different between CSDs."),

                     dbc.Button("Export", id="export-table-20", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_14a',
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
                     html.Div(id='output_14a-container'),
                     html.Br()
                 ], className='pg2-output14a-lgeo'
                 ), 


                # 3. HICC Section 3.6, data point 14b. Affordable Housing deficit
                html.Div([
                     html.H5(children=html.Strong('Percentage of Households in Core Housing Need, by Income Category and HH Size, 2021'),
                             id='visualization14b'),
                     html.H6("The following chart examines those households in CHN and shows their relative distribution by household size "
                             "(i.e. the number of individuals in a given household for each household income category. "
                             "When there is no bar for an income category, it means that either there are no households in CHN "
                             "within an income category, or that there are too few households to report."),

                     dcc.Graph(id='graph_14b',
                               figure=fig2,
                               config=config,
                               ),

                     html.Br(),

                     html.H5(children=html.Strong('2021 Affordable Housing Deficit')),
                     html.H6("The following table shows the total number of households in CHN by household size and income category, "
                             "which may be considered as the existing deficit of housing options in the community."),

                     dbc.Button("Export", id="export-table-21", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_14b',
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

                                       },
                        style_table={'width': '80%', 'margin': 'left'},
                     ),
                     html.Div(id='output_14b-container'),
                     html.Br()
                 ], className='pg2-output14b-lgeo'
                 ), 


                # 3. HICC Section 4.1, data point 11.
                html.Div([
                     html.H4(children=html.Strong(f'Priority groups by Core Housing Need status')),
                     html.H5(children=html.Strong('HICC HNA Template: Section 4.1'),
                             id='visualization6'),
                     html.H6('The following table show the number of households in Core Housing Need (CHN) for certain population groups, along with the percentage of households in CHN  for each group. '
                             'Rate of CHN is calculated as the number of households in CHN divided by the number of households examined for CHN*. '),

                     dbc.Button("Export", id="export-table-17", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_11',
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

                                       },
                         style_table={'width': '80%', 'margin': 'left'},
                     ),
                     html.I(children= [
                         "*Please note that Statistics Canada employs rounding and suppression for small populations, and so a zero count "
                         "may not necessarily represent zero ",
                         html.Br(),
                         "households, but too few to report.The census does not evaluate all households for Core Housing Need – ",
                         html.A("see more here", href="https://www23.statcan.gc.ca/imdb/p3Var.pl?Function=DEC&Id=1230313", target='_blank')
                     ]),
                     html.Br(),
                     html.H6(
                         f'The following graph illustrates the above table, displaying the percentage of households in CHN for each population group.',
                     ),
                     dcc.Graph(id='graph_11',
                              figure=fig1,
                              config=config,
                     ),

                     html.Div(id='output_11-container'),
                     html.Br()
                 ], className='pg2-output11-lgeo'
                 ),


                 # Data point 6 primary and secondary rental units HICC HNA Template: Section 5.2.1
                 html.Div([
                     html.H4(children=html.Strong(f'Number of Primary and Secondary Rental Units')),
                     html.H5(children=html.Strong('HICC HNA Template: Section 5.2.1'),
                             id='visualization6'),
                     html.H6(
                         f'The following chart shows the relative size of the primary (i.e. purpose-built rental) and secondary rental markets as a share of the whole rental market.',
                     ),
                     html.H6("Please note that the number of Secondary Rental units is estimated here as the difference between the number "
                             "of renter households in the 2021 Census of Population and the number of primary rental units identified in CMHC's "
                             "Rental Market Survey in 2021. Due to the differing survey frames between the Census and the Rental Market Survey, "
                             "most community/social housing units will be grouped within the Secondary Rental units estimate."),
                             
                     dcc.Graph(id='graph_6',
                              figure=fig1,
                              config=config,
                              # style={"font-weight": "bold"}

                     ),
                     html.H6('The following table shows the number of primary secondary rental units in the community.'),

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
                                       },
                         style_table={'width': '70%', 'margin': 'left'},

                     ), html.Div(id='output_6-container'),
                     html.Br()
                 ], className='pg2-output6-lgeo'
                 ),


                 # output 13
                 html.Div([
                     html.H4(children=html.Strong(f'Number of Affordable Rental Units for Low and Very Low-Income Households Built, and the Number Lost')),
                     html.H5(children=html.Strong('HICC HNA Template: Section 5.3'),
                             id='visualization6'),
                     html.H6(children=[
                         "The following tables estimates the number of rental dwellings affordable to low and very-low income households built and "
                         "lost between 2016 and 2021. We define low and very-low income rental households as those rental households whose income "
                         "is equal to or less than 50% of the area median household income in a given year. "
                         ]),
                     
                     html.H6([
                         "To understand how we calculated affordable units gained or lost, see our ",
                         html.A("methodology.", href='https://hart.ubc.ca/federal-hna-template-methodology/', target="_blank"),
                     ]),

                     html.H6("In some cases, affordable units from existing stock (built prior 2016) are gained. This can be due to factors such as "
                             "stagnating rents in aging buildings or increases to household incomes. Gains in affordable units are represented by negative values."),

                    html.Br(),

                    html.H6("The following table shows the number and net change of affordable rentals for "
                            "Very Low- and Low-Income households (i.e. households earning less than 50% of AMHI)."),

                     dbc.Button("Export", id="export-table-18", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_13a',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis',
                                     'textAlign': 'right'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',
                                       },
                         style_table={'width': '70%', 'margin': 'left'},
                         css=[{
                                'selector': 'tr:nth-child(2)',
                                'rule':'''
                                        display: None;
                                '''
                              }],

                     ),
                     
                    html.Br(),
                    
                    html.H6("The following table shows the number and net change of affordable rentals for "
                            "Very Low-Income households (i.e. households earning less than 20% of AMHI)."),
                    dbc.Button("Export", id="export-table-23", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_13b',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis',
                                     'textAlign': 'right'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',
                                       },
                         style_table={'width': '70%', 'margin': 'left'},
                         css=[{
                                'selector': 'tr:nth-child(2)',
                                'rule':'''
                                        display: None;
                                '''
                              }],

                     ),

                    html.Br(),
                    
                    html.H6("The following table shows the number and net change of affordable rentals for Low-Income households "
                            "(i.e. households earning 20-50% of AMHI)."),
                    dbc.Button("Export", id="export-table-24", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_13c',
                         merge_duplicate_headers=True,
                         style_data={'whiteSpace': 'normal', 'overflow': 'hidden',
                                     'textOverflow': 'ellipsis'},
                         style_cell={'font-family': 'Bahnschrift',
                                     'height': 'auto',
                                     'whiteSpace': 'normal',
                                     'overflow': 'hidden',
                                     'textOverflow': 'ellipsis',
                                     'textAlign': 'right'
                                     },
                         style_header={'textAlign': 'center', 'fontWeight': 'bold',
                                       },
                         style_table={'width': '70%', 'margin': 'left'},
                         css=[{
                                'selector': 'tr:nth-child(2)',
                                'rule':'''
                                        display: None;
                                '''
                              }],

                     ),
                     html.I(children=[
                         "*Note: Due to differences in available responses used in the long-form census between 2016 and 2021 regarding period of construction, ",
                         html.Br(),
                         'this estimate of units lost will double-count any units built between January 1, 2016 and May 10, 2016 (i.e. census day 2016). The 2016 ',
                         html.Br(),
                         'long-form census uses the period "2011-2016" as an option for '
                         "the dwelling's period of construction while the 2021 long-form census ",
                         html.Br(),
                         'uses the periods "2011-2015," "2016-2020," and "2021" as the possible options.',
                          
                        ]),
                    

                     html.Div(id='output_13-container'),
                     html.Br()
                 ], className='pg2-output13-lgeo'
                 ),


                 # 6. HICC Section 5.4, data point 2. Output 2a
                 html.Div([
                     html.H4(children=[html.Strong('Change in Average Rents Between 2016 and 2023')],
                             id='visualization2a'),
                     html.H5("HICC HNA Template: Section 5.4",
                             # style={'fontFamily': 'Open Sans, sans-serif'}
                             ),
                     html.H6(children=['The following table shows the average monthly rent for all ',
                                       html.U('primary'),
                                       ' rental units per ',
                             html.A("CMHC’s Rental Market Survey", href='https://hart.ubc.ca/federal-hna-template-methodology/', target="_blank"),
                                       ' (all occupied and vacant rental units). These values reflect data collected in October of each year.'

                         ]
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
                     html.Br(),
                     html.Br(),
                     html.H6(
                         "The following chart shows the change in average monthly rent for the primary rental market (both occupied and vacant units) between years as a dollar amount."),

                     # Plot
                     html.Div([

                         dcc.Graph(id='graph_2b_1',
                                   figure=fig1,
                                   config=config,

                                   ),
                         html.H6(
                             f'The following chart shows the percentage change in average monthly rent for the primary rental market (both occupied and vacant units) between years.',
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
                     html.H6('The following table shows the annual change in monthly rent for primary rental units (both occupied and vacant units) both as a dollar amount and as a percentage.',
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
                 html.H4(children=html.Strong('Change in Vacancy Rates Between 2016 and 2023'),
                         id='visualization3a'),
                 html.H5(
                     f'HICC HNA Template: Section 5.5',
                     # style={'fontFamily': 'Open Sans, sans-serif'}
                 ),
                 # TABLES
                 html.H6(
                     'The following table shows the vacancy rate among primary rental units per CMHC’s Rental Market Survey. '
                     'These values reflect data collected in October of each year.',
                     # style={'fontFamily': 'Open Sans, sans-serif'}
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
                 html.Br(),
                 html.H6('The following graph illustrates the above table, displaying the vacancy rate of primary rental units as a percentage each year.'),

                 # Plot
                 html.Div([
                     dcc.Graph(id='graph_3a',
                               figure=fig1,
                               config=config,
                               ),

                 html.H6('The following table shows the yearly change in vacancy rate for primary rental units by percentage points.',
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
                     ),
                 html.Br(),
                 # Second graph change in vacancy rates
                 html.H6(f'The following graph illustrates the above table, displaying the change in the vacancy rate of primary rental units between years as percentage points.',
                     ),
                 dcc.Graph(id='graph_3b',
                           figure=fig2,
                           config=config,
                           ),
                 html.Div(id='graph_3-container')
                 ]),


                 html.Div(id='output_3ab-container'),
                     html.Br()
                 ], className='pg2-output3a-lgeo'
                 ),



                 # HICC Section 5.6, data point 5.
                 html.Div([
                 html.H4(children=[html.Strong('Change in Core Housing Need Over Time (2016-2021) by Tenure'),
                                   ],
                         #style={'fontFamily': 'Open Sans, sans-serif'},
                         id='visualization5'),
                 html.H5("HICC HNA Template: Question 5.6"),

                 # TABLE
                 html.H6("The following table shows the number of households in Core Housing Need (CHN) among owner-occupied and tenant-occupied households in 2016 and 2021. Please note that tenant-occupied includes both primary and secondary rental market households.",
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
                                 'textOverflow': 'ellipsis',
                                 },
                     style_header={'textAlign': 'center', 'fontWeight': 'bold',
                                   },
                     style_table={'width': '70%', 'margin': 'left'},
                    ),
                 html.Br(),
                 html.H6(
                     f"The following chart illustrates the above table, displaying the number of households in CHN among owner-occupied and tenant-occupied households in 2016 and 2021.",
                 ),
                 # output 5 bar charts
                 html.Div([
                     # Plot
                     html.Div([

                         dcc.Graph(id='graph_5a',
                                   figure=fig1,
                                   config=config,

                                   ),
                                   html.Div(id='graph_5a-container'),
                         #table
                 html.Br(),
                 html.H6(
                     f'The following table shows the rate of CHN among owner-occupied and tenant-occupied households in 2016 and 2021.',
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
                                   },
                     style_table={'width': '70%', 'margin': 'left'},
                     ),
                 html.Br(),

                 html.H6(
                     f'The following chart illustrates the above table, displaying the rate of CHN among owner-occupied and tenant-occupied households in 2016 and 2021.',
                     #style={'fontFamily': 'Open Sans, sans-serif'}
                 ),
                 dcc.Graph(id='graph_5b',
                           figure=fig1,
                           config=config,
                           ),
                 html.Div(id='graph_5b-container')
                 ]),

                 ], className='pg2-bar5-lgeo'
                 ),


                 html.Div(id='output_5ab-container'),
                     html.Br()
                 ], className='pg2-output5-lgeo'
                 ),

                 # 9. HICC Section 5.7.1, data point 7. Output 7
                 html.H4(html.Strong("Number of Rental Housing Units that are Subsidized or Unsubsidized")),
                 html.H5(html.Strong("HICC HNA Template: Section 5.7.1")),
                 # tables
                 html.H6(
                     "The following table shows the number of rental housing units in 2021 that were subsidized or unsubsidized, per the census. "
                     "Subsidized housing includes rent geared to income, social housing, public housing, government-assisted housing, non-profit housing, rent supplements and housing allowances. Unsubsidized housing is in the private rental market without rent assistance."),
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
                                   },
                     style_table={'width': '70%', 'margin': 'left'}
                 ),
                 html.Br(),
                 html.Div([
                     html.H6(
                         f'The following chart shows the relative size of the subsidized and unsubsidized rental units as a share of all rental units.',
                     ),
                     dcc.Graph(id='pie_7',
                               figure=fig1,
                               config=config,
                               ),

                  html.Div(id='output_7-container'),
                     html.Br()
                 ], className='pg2-output7-lgeo'
                 ),



                 # 10. HICC Section 5.7.1, data point 8. Output 8
                 html.Div([
                     html.H4(children=html.Strong('Number of Housing Units that are Below-Market Rent in the Private Market'),
                             id='visualization8'),
                     html.H5(html.Strong("HICC HNA Template: Section 5.7.1")),
                     html.H6("The following table shows the number of unsubsidized occupied rental housing units with below-market* rent in 2021, per the census. It also shows the percentage of occupied housing units with a below-market* rent as a percentage of all private occupied rental housing units."),
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

                                       },
                         style_table={'width': '70%', 'margin': 'left'}
                     ),
                     html.P(children=[
                         html.I('*Note: There are varying definitions of "below market"; we have calculated this figure by calculating shelter that is '
                                'affordable to households earning 80% of Area Median Household Income. Across Canada, median household incomes for renters '
                                'in 2020 were only slightly over half (54%) of median household income for homeowners. Therefore, it should be noted '
                                'that a renter household making 80% of AMHI in 2020 should be considered relatively high-income, and this value should '
                                'not be considered a proxy for how many homes are affordable. Read more in our '),
                         html.A(html.I("methodology."), href='https://hart.ubc.ca/federal-hna-template-methodology/', target="_blank")
                     ]),

                     html.Div(id='output_8-container'),
                     html.Br()
                 ], className='pg2-output8-lgeo'
                 ),

                 #11. HICC Section 5.7.1, data point 12.
                 html.Div([
                     html.H4(children=html.Strong('Number of co-operative housing units')),
                     html.H5(children=html.Strong('HICC HNA Template: Section 5.7.1')),
                     html.H6(
                         f'The following table shows the number of co-operative housing units who were registered with the Co-operative Housing Federation of Canada (CHF Canada) with an address within the selected geography in 2024. '),
                     # TABLE for output 12
                     dbc.Button("Export", id="export-table-19", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_12',
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
                                       },
                         style_table={'width': '50%', 'margin': 'left'},
                     ),
                     html.I("*Data represents co-ops registered with the Co-operative Housing Federation of Canada (CHF Canada) extracted as of December 5, 2024 and may not include all co-ops."),
                     html.Br(),
                     html.Br()
                 ], className='pg2-output12-lgeo'),

                 # HICC Section 5.9.2, data point 4a and 4b tables
                 html.Div([
                     html.H4(children=html.Strong('Housing Starts by Structural Type and Tenure')),
                     html.H5(children=html.Strong('HICC HNA Template: Section 5.9.2')),
                 html.H6("The following table shows the number of housing starts by structural type, for each calendar year from 2016 to 2023. Data does not necessarily reflect or predict completed homes in any given year or span of time.",
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
                 html.Br(),
                 html.H6(f'The following chart illustrates the above table, displaying the number of housing starts by structural type for each calendar year from 2016 to 2023.'),
                 # 4a graph stacked bar
                 html.Div([

                     # Plot
                     html.Div([
                         dcc.Graph(id='graph_4a',
                                   figure=fig1,
                                   config=config,

                                   ),
                         html.Div(id='graph_4a-container')
                     ]),

                 ], className='pg2-bar4a-1-lgeo'
                 ),

                 html.Br(),
                 html.H6("The following table shows the number of housing starts by tenure for each calendar year from 2016 to 2023.",),

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
                 ),
                 html.Br(),

                 html.H6("The following chart illustrates the above table, displaying the number of housing starts by tenure for each calendar year from 2016 to 2023.",
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


                 html.Div(id='output_4ab-container')
             ], className='pg2-output4-lgeo'
             ),

             # 3. HICC Section 6.1.1, data point 16.
                html.Div([
                     html.H4(children=html.Strong(f'2031 Projected Households by Household Size and Income Category')),
                     html.H5(children=html.Strong('HICC HNA Template: Section 6.1.1'),
                             id='visualization16'),
                     html.H6("The following table shows the projected total number of households in 2031 by household size and income category."),
                     
                     html.H6("In this table, we project forward using the line of best fit to the combined income and household size category. "
                     "Since the combined categories have unique values, and are also subject to Statistics Canada’s random rounding, "
                     "the resulting Totals here may not match the sum of all when projecting households by either income or household size alone."),

                     dbc.Button("Export", id="export-table-22", className="mb-3", color="primary"),
                     dash_table.DataTable(
                         id='output_16',
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

                                       },
                         style_table={'width': '80%', 'margin': 'left'},
                     ),
                     html.Br(),
                     
                     html.Div(id='output_16-container'),
                     html.Br()
                 ], className='pg2-output16-lgeo'
                 ), 

             html.Br(),
             html.Br(),


                 # LGEO

                 html.Footer([
                     html.Img(src='.\\assets\\HNA Template Footer.png', className='footer-image'),
                 html.Br(),
                 html.Br(),
                 html.Br(),
                 html.Br()
                 ],

                 className='footer'),

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


def generate_style_header_conditional(columns, text_align=None):
    style_conditional = []
    if text_align == 'right':
        for index, col in enumerate(columns):
            style_header = {'if': {'header_index': index},
                            'backgroundColor': '#002145' if index == 0 else '#39C0F7',
                            'color': '#FFFFFF' if index == 0 else '#000000',
                             'textAlign': 'center' if index == 0 else 'right',
                            'border': '1px solid #002145',
                            }
            style_conditional.append(style_header)


    else:
        for index, col in enumerate(columns):
            header_style = {
                'if': {'header_index': index},
                'backgroundColor': '#002145' if index == 0 else '#39C0F7',
                'color': '#FFFFFF' if index == 0 else '#000000',
                'border': '1px solid #002145',
                # 'textAlign': 'right',
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


# Defining different table generator for HART tables because the code structure is different
def table_14a_generator(geo, df):
    geoid = mapped_geo_code.loc[mapped_geo_code['Geography'] == geo, :]['Geo_Code'].tolist()[0]
    
    try:
        filtered_df = df[df['ALT_GEO_CODE_EN'] == f'{geoid}'].drop_duplicates()
    except TypeError:
        filtered_df = df[df['ALT_GEO_CODE_EN'] == f'{geoid}']

    if filtered_df.empty:
            return pd.DataFrame(columns=[
                'Income Category', '% of Total HHs ', 'Annual HH Income ',
                'Affordable Shelter Cost '
            ])
    
    shelter_range = [i+'.1' for i in amhi_range]

    # pdb.set_trace()
    portion_of_total_hh = []
    for x in x_base:
        portion_of_total_hh.append(round(filtered_df[f'Percent of Total HH that are in {x}'].tolist()[0] * 100, 2))

    amhi_list = []
    shelter_list = []

    if len(str(geoid)) == 5: #append n/a for CMAs
        amhi_list = ["n/a"] * len(amhi_range)
        shelter_list = ["n/a"] * len(shelter_range)
    else:
        for a in amhi_range:
            amhi_list.append(filtered_df[a].tolist()[0])
        
        for s in shelter_range:
            shelter_list.append(filtered_df[s].tolist()[0])

    # pdb.set_trace()

    try:
        filtered_df_geo_index = filtered_df.set_index(geo)
    except KeyError:
        filtered_df_geo_index = filtered_df.set_index("Geography")

    if len(str(geoid)) == 5: #append n/a for CMAs
        median_income = "n/a"
        median_rent = "n/a"
    else:
        median_income = '${:0,.0f}'.format(float(val)) if (val := filtered_df_geo_index.at[geo, 'Median income of household ($)']) not in [None, np.nan] and pd.notna(val) else np.nan
        median_rent = '${:0,.0f}'.format(float(val)) if (val := filtered_df_geo_index.at[geo, 'Rent AMHI']) not in [None, np.nan] and pd.notna(val) else np.nan

    if all(pd.isna(x) for x in portion_of_total_hh):
        table = pd.DataFrame(columns=['Income Category', '% of Total HHs ', 'Annual HH Income ', 'Affordable Shelter Cost '])
    else:
        table = pd.DataFrame({'Income Category': income_ct, '% of Total HHs ': portion_of_total_hh, 'Annual HH Income ': amhi_list, 'Affordable Shelter Cost ': shelter_list})
        table['% of Total HHs '] = np.where(table['% of Total HHs '].notna(), table['% of Total HHs '].astype(str) + '%', np.nan)


    return table, median_income, median_rent


# Defining different table generator for HART tables because the code structure is different
def table_14b_generator(geo, df):
    geoid = mapped_geo_code.loc[mapped_geo_code['Geography'] == geo, :]['Geo_Code'].tolist()[0]
    
    try:
        filtered_df = df[df['ALT_GEO_CODE_EN'] == f'{geoid}'].drop_duplicates()
    except TypeError:
        filtered_df = df[df['ALT_GEO_CODE_EN'] == f'{geoid}']

    if filtered_df.empty:
        return pd.DataFrame(columns=[
            'Income Category (Max. affordable shelter cost)', '1 Person HH', '2 Person HH',
            '3 Person HH', '4 Person HH', '5+ Person HH', 'Total'
        ])

    table = pd.DataFrame({'Income Category': income_ct})

    # print(filtered_df[f'Total - Private households by presence of at least one or of the combined activity limitations (Q11a, Q11b, Q11c or Q11f or combined)-1-Households with income 20% or under of area median household income (AMHI)-Households in core housing need'])

    h_hold_value = []
    hh_p_num_list = [1, 2, 3, 4, '5 or more']
    income_lv_list = ['20% or under', '21% to 50%', '51% to 80%', '81% to 120%', '121% or more']

    for h in hh_p_num_list:
        h_hold_value = []
        if h == 1:
            h2 = '1 person'
        elif h == '5 or more':
            h2 = '5 or more persons household'
        else:
            h2 = f'{str(h)} persons'
        for i in income_lv_list:
            if i == '20% or under':
                column = f'Total - Private households by presence of at least one or of the combined activity limitations (Q11a, Q11b, Q11c or Q11f or combined)-{h2}-Households with income {i} of area median household income (AMHI)-Households in core housing need'
                h_hold_value.append(filtered_df[column].tolist()[0])

            else:
                column = f'Total - Private households by presence of at least one or of the combined activity limitations (Q11a, Q11b, Q11c or Q11f or combined)-{h2}-Households with income {i} of AMHI-Households in core housing need'
                # print(column)
                h_hold_value.append(filtered_df[column].tolist()[0])
            # print(h_hold_value)
        
        if h == 1:        
            table[f'{h} Person HH'] = h_hold_value
        elif h == '5 or more':
            table[f'5+ Person HH'] = h_hold_value
        else:
            table[f'{h} Person HH'] = h_hold_value

    x_list = []

    i = 0
    for b, c in zip(x_base, x_columns):
        value = filtered_df[c].tolist()[0]
        if i < 4:
            # x = b + " ($" + str(int(float(filtered_df[c].tolist()[0]))) + ")"
            if len(str(geoid)) == 5: #append "-" for CMAs
                x = b + " (-)"
            else:
                x = b + (" ($" + '{0:,.0f}'.format(float(value)) + ")" if pd.notna(value) else "-")
            x_list.append(x)
        else:
            # x = b + " (>$" + str(int(float(filtered_df[c].tolist()[0]))) + ")"
            if len(str(geoid)) == 5: #append "-" for CMAs
                x = b + " (-)"
            else:
                x = b + (" (>$" + '{0:,.0f}'.format(float(value)) + ")" if pd.notna(value) else "-")
            x_list.append(x)
        i += 1

    table['Income Category (Max. affordable shelter cost)'] = x_list
    table['Income Category'] = ['Very low Income', 'Low Income', 'Moderate Income',
                                'Median Income', 'High Income']
    
    numeric_cols = table.columns.difference(['Income Category', 'Income Category (Max. affordable shelter cost)'])
    all_zero_or_na = table[numeric_cols].apply(pd.to_numeric, errors='coerce').fillna(0).sum().sum() == 0

    if all_zero_or_na:
        return pd.DataFrame(columns=[
        'Income Category (Max. affordable shelter cost)', '1 Person HH', '2 Person HH',
        '3 Person HH', '4 Person HH', '5+ Person HH', 'Total'
        ])

    table['Total'] = table.sum(axis = 1)
    row_total_csd = table.sum(axis=0)
    row_total_csd[0] = 'Total'
    table.loc[len(table['Income Category']), :] = row_total_csd
    table.loc[5, 'Income Category (Max. affordable shelter cost)'] = 'Total'

    return table

# Defining different table generator for HART tables because the code structure is different
def graph_14b_generator(geo, df):
    geoid = mapped_geo_code.loc[mapped_geo_code['Geography'] == geo, :]['Geo_Code'].tolist()[0]

    filtered_df = df[df['ALT_GEO_CODE_EN'] == f'{geoid}']
    # pdb.set_trace()
    if filtered_df.empty:
        return pd.DataFrame(columns=[
            'HH_Size', 'Income_Category', 'Percent'
        ])
    
    x_list = []

    i = 0
    for c in x_columns:
        value = filtered_df[c].tolist()[0]
        if i < 4:
            if len(str(geoid)) == 5: #append "-" for CMAs
                x = "(-)"
            else:
                x = (" ($" + '{0:,.0f}'.format(float(value)) + ") " if pd.notna(value) else "")
            x_list.append(x)
        else:
            if len(str(geoid)) == 5: #append "-" for CMAs
                x = "(-)"
            else:
                x = (" (>$" + '{0:,.0f}'.format(float(value)) + ") " if pd.notna(value) else "")
            x_list.append(x)
        i += 1

    income_lv_list = ['20% or under', '21% to 50%', '51% to 80%', '81% to 120%', '121% or more']
    # x_list = [sub.replace('$$', '$') for sub in x_list]
    # x_list = [sub.replace('.0', '') for sub in x_list]

    h_hold_value = []
    hh_p_num_list_full = []
    hh_column_name = ['1 Person', '2 Person', '3 Person', '4 Person', '5+ Person']
    hh_p_num_list = [1, 2, 3, 4, '5 or more']

    for h, hc in zip(hh_p_num_list, hh_column_name):
        for i in income_lv_list:
            column = f'Per HH with income {i} of AMHI in core housing need that are {h} person HH'
            h_hold_value.append(filtered_df[column].tolist()[0])
            hh_p_num_list_full.append(hc)

    if all(pd.isna(x) for x in hh_p_num_list_full):
        plot_df = pd.DataFrame(columns=['HH_Size', 'Income_Category', 'Percent'])
    else:
        plot_df = pd.DataFrame({'HH_Size': hh_p_num_list_full, 'Income_Category': x_base * 5, 'Percent': h_hold_value})
    
    return plot_df


# Defining different table generator for HART tables because the code structure is different
def table_16_generator(geo, df):
    geoid = mapped_geo_code.loc[mapped_geo_code['Geography'] == geo, :]['Geo_Code'].tolist()[0]
    filtered_df = df[df['ALT_GEO_CODE_EN'] == f'{geoid}']

    if filtered_df.empty:
        return pd.DataFrame(columns=[
            'HH Income Category', '1 Person', '2 Person', '3 Person', '4 Person', '5+ Person', 'Total '
        ])

    # variables for table 16
    ahmi_projected_range = ['20% or under of area median household income (AMHI)',
                    '21% to 50% of AMHI', '51% to 80% of AMHI', '81% to 120% of AMHI',
                    '121% or over of AMHI']
    pp_list = ['1pp', '2pp', '3pp', '4pp', '5pp']

    # income_l = []
    # pp_l = []
    result_csd_l = []
    # pdb.set_trace()

    for i in ahmi_projected_range:
        for p in pp_list:
            col_format = f'2031 Projected {p} HH with income {i}'
            # income_l.append(i)
            # pp_l.append(p)
            result_csd_l.append(filtered_df[col_format].tolist()[0])

    income_l = [level for level in ['Very Low Income', 'Low Income', 'Moderate Income', 'Median Income', 'High Income'] for _ in range(5)]
    hh_l = ['1 Person', '2 Person', '3 Person', '4 Person', '5+ Person']

    table = pd.DataFrame({'Income Category': income_l, 'HH Category': hh_l * 5, 'value': np.round(result_csd_l, 0)})
    table = table.fillna(0)
    table = table.replace([np.inf, -np.inf], 0)

    table_csd = table.pivot_table(values='value', index=['Income Category'], columns=['HH Category'], sort=False)
    table_csd = table_csd.reset_index()

    row_total_csd = table_csd.sum(axis=0)
    row_total_csd[0] = 'Total'
    table_csd.loc[5, :] = row_total_csd

    table_csd.columns = ['HH Income Category', '1 Person', '2 Person', '3 Person', '4 Person', '5+ Person']
    table_csd['Total '] = table_csd.sum(axis=1)

    return table_csd



def table_generator(geo, df, table_id):
    geoid = mapped_geo_code.loc[mapped_geo_code['Geography'] == geo, :]['Geo_Code'].tolist()[0]
    # print(geo)

    filtered_df = df[df['ALT_GEO_CODE_EN'] == f'{geoid}']
    # pdb.set_trace()
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
            columns={'2017': '2016-2017', '2018': '2017-2018',
                     '2019': '2018-2019', '2020': '2019-2020',
                     '2021': '2020-2021', '2022': '2021-2022',
                     '2023': '2022-2023'}
        )  #.rename('Change in Vacancy Rate', 'Change in Vacancy Rate (percentage points')
        filtered_df.drop('2016', axis=1, inplace=True)
        for col in filtered_df.columns[4:]:
            filtered_df[col] = filtered_df[col] * 100

    elif table_id == 'output_6':
        filtered_df = filtered_df[filtered_df['Metric'].isin(['Primary Rental Units', 'Secondary Rental Units'])]
        filtered_df['Header to be deleted'] = 'Number of primary and secondary rental units '

    elif ((table_id == 'output_9') or (table_id == 'output_10a') or (table_id == 'output_10b')):
        rate_columns = filtered_df.columns[filtered_df.columns.str.endswith('Rate')]
        # Update headship rate to 1, if greater than 1
        filtered_df[rate_columns] = filtered_df[rate_columns].mask(filtered_df[rate_columns] > 1, 1)

        if (table_id == 'output_10a') or (table_id == 'output_10b'):
            new_header = ['Household Suppression by age of Primary Household Maintainer -\
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
        #print("output_4a HEADER", filtered_df.columns[0])

    elif table_id == 'output_8':
        filtered_df = filtered_df.melt(id_vars=filtered_df.columns[:3], var_name="Metric", value_name="2021")

    elif table_id == 'output_11':
        # melt into format where marginal group is in the rows and colums = 'Number of  Households in CHN' 'Rate of CHN'
        melted_rates = filtered_df.melt(id_vars=filtered_df.columns[:3], 
                                        value_vars= ["Youth_Rate of CHN", "SameGender_Rate of CHN", 
                                                      "MentalHealth_Rate of CHN", "Veteran_Rate of CHN", 
                                                      "SingleMother_Rate of CHN", "Women_Rate of CHN",
                                                      "IndigenousHH_Rate of CHN", "VisibleMinority_Rate of CHN",
                                                      "Black_Rate of CHN", "RecentImmigrant_Rate of CHN",
                                                      "Refugee_Rate of CHN", "Under24_Rate of CHN",
                                                      "Over65_Rate of CHN", "Over85_Rate of CHN",
                                                      "Physical-AL_Rate of CHN", "Cognitive-Mental-Addictions-AL_Rate of CHN",
                                                      "TransNonBinary_Rate of CHN", "Total_Rate of CHN"], 
                                                      var_name= 'Priority Populations', value_name="Rate of CHN" )
        melted_rates_col = melted_rates['Rate of CHN']

        melted_hh_in_CHN = filtered_df.melt(id_vars=filtered_df.columns[:3], 
                                            value_vars=['2021_CHN_Youth' , '2021_CHN_SameGender', 
                                                        '2021_CHN_MentalHealth', '2021_CHN_Veteran', 
                                                        '2021_CHN_SingleMother', '2021_CHN_Women',
                                                        '2021_CHN_IndigenousHH', '2021_CHN_VisibleMinority',
                                                        '2021_CHN_Black', '2021_CHN_RecentImmigrant',
                                                        '2021_CHN_Refugee', '2021_CHN_Under24',
                                                        '2021_CHN_Over65', '2021_CHN_Over85',
                                                        '2021_CHN_Physical-AL', '2021_CHN_Cognitive-Mental-Addictions-AL',
                                                        '2021_CHN_TransNonBinary', '2021_CHN_Total'], 
                                                        var_name='Priority Populations', value_name="Number of Households in CHN" )
        filtered_df = pd.concat([melted_hh_in_CHN, melted_rates_col ], axis=1)
        priority_pops = [x.split("_")[2] for x in filtered_df['Priority Populations'].values]
        filtered_df['Priority Populations'] = priority_pops


        new_header = ['Households in Core Housing Need (CHN) by priority population, 2021'] * (len(filtered_df.columns))
        filtered_df.columns = pd.MultiIndex.from_tuples(zip(new_header, filtered_df.columns))

    elif ((table_id == 'output_13a') or (table_id == 'output_13b') or (table_id == 'output_13c')):
        # melt into longer format
        if table_id == 'output_13b':
            melted_counts = filtered_df.melt(id_vars=filtered_df.columns[:3], 
                                            value_vars=['2016to2021_AffordableUnits_Built_VeryLowOnly', '2016to2021_AffordableUnits_Lost_VeryLowOnly', 
                                                        'Net Change in Affordable Units Very Low'], var_name= 'delete_me', value_name = 'totals')
        elif table_id == 'output_13c':
            melted_counts = filtered_df.melt(id_vars=filtered_df.columns[:3], 
                                            value_vars=['2016to2021_AffordableUnits_Built_LowOnly', '2016to2021_AffordableUnits_Lost_LowOnly', 
                                                        'Net Change in Affordable Units Low'], var_name= 'delete_me', value_name = 'totals')
        else:
            melted_counts = filtered_df.melt(id_vars=filtered_df.columns[:3], 
                                            value_vars=['2016to2021_AffordableUnits_Built', '2016to2021_AffordableUnits_Lost', 
                                                        'Net Change in Affordable Units'], var_name= 'delete_me', value_name = 'totals')
        filtered_df = melted_counts
    else:

        filtered_df = filtered_df

    if (table_id == 'output_1a') or (table_id == 'output_1b'):
        # if filtered_df["Value"].fillna(0).sum() == 0:
        #     table = pd.DataFrame(columns=filtered_df.columns[2:])
        # else: # if want to keep tables blank
        table = filtered_df.iloc[:, 2:]
    else:
        table = filtered_df.iloc[:, 3:]


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
    table = number_formatting(table, ['Value'], 0, conditions=number_conditions).fillna(0)

    table = table[['Characteristic', 'Data', 'Value']].sort_values(
        by=['Characteristic', 'Data'], ascending=False).replace('a ', 'an existing ', regex=True)
    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align='right')

    # Generating callback output to update table
    #print("table 1", table)
    table = table.replace('Total', 'Total HHs (#)')
    table['Characteristic'] = table['Characteristic'].replace('Households within 800m of an existing rail/light-rail transit station (#)', 'Households within 800m of an existing rail/light-rail transit station')
    table['Characteristic'] = table['Characteristic'].replace('Households within 200m of an existing rail/light-rail transit station (#)', 'Households within 200m of an existing rail/light-rail transit station')

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
                                     'textAlign': 'right',
                                     "width": "65%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     
                                 } for c in table_columns[1:]
                             ]
    new_data_style = [
            {
                'if': {'row_index': i, 'column_id': 'Characteristic'},
                'backgroundColor': '#39c0f7',
                'color': '#39c0f7',
                'border-top': 'none',
                'rowSpan': 2,
                "maxWidth": "190px",
                'textAlign': 'right'


            } for i in [1, 3]
        ] + [{
            'if': {'row_index': i, 'column_id': 'Characteristic'},
            'backgroundColor': '#39c0f7',
        } for i in [0, 2]
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
    table = number_formatting(table, ['Value'], 0, conditions=number_conditions).fillna(0)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align='right')

    table = table[['Characteristic', 'Data', 'Value']].sort_values(
        by=['Characteristic', 'Data'], ascending=False).replace('a ', 'an existing or under construction ', regex=True)
    

    # Generating callback output to update table
    table = table.replace('Total', 'Total HHs (#)')
    table['Characteristic'] = table['Characteristic'].replace(
        'Households within 800m of an existing or under construction rail/light-rail transit station (#)',
        'Households within 800m of an existing or under construction rail/light-rail transit station')
    table['Characteristic'] = table['Characteristic'].replace(
        'Households within 200m of an existing or under construction rail/light-rail transit station (#)',
        'Households within 200m of an existing or under construction rail/light-rail transit station')

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
                                     'textAlign': 'right',
                                     "width": "65%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     
                                 } for c in table_columns[1:]
                             ]
    new_data_style = [
            {
                'if': {'row_index': i, 'column_id': 'Characteristic'},
                'backgroundColor': '#39c0f7',
                'color': '#39c0f7',
                'border-top': 'none',
                'rowSpan': 2,
                "maxWidth": "190px",
                'textAlign': 'right'


            } for i in [1, 3]
        ] + [{
            'if': {'row_index': i, 'column_id': 'Characteristic'},
            'backgroundColor': '#39c0f7',
        } for i in [0, 2]
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
    # pdb.set_trace()
    table = table[table['Metric'] == 'Avg Monthly Rent']
    
    table.drop_duplicates(inplace=True)

    if not table.empty:
        table.loc[table['Metric'] == 'Avg Monthly Rent', table.columns[1:]] = \
        table.loc[table['Metric'] == 'Avg Monthly Rent', table.columns[1:]].applymap(
            lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) else x)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align='right')
    table = table.rename(columns={'Metric': ''}).replace('Avg Monthly Rent' , 'Avg Monthly Rent ($)')

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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
        lambda x: f"+${x:,.1f}" if isinstance(x, (int, float)) and x > 0 
        else f"-${abs(x):,.1f}" if isinstance(x, (int, float)) and x < 0 
        else f"${x:,.1f}" if isinstance(x, (int, float)) 
        else x
        )
        table.loc[table['Metric'] == '% Change in Avg Rent', table.columns[1:]] = \
            table.loc[table['Metric'] == '% Change in Avg Rent', table.columns[1:]].applymap(
            lambda x: f"+{x}" if isinstance(x, str) and x.endswith('%') and x[:-1].replace('.', '', 1).isdigit() and float(x[:-1]) > 0 
        else x
        )
    

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align='right')
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
                                     'textAlign': 'right',
                                     "maxWidth": "190px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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
        customdata=[f"+${x:,.1f}" if isinstance(x, (int, float)) and x > 0 
        else f"-${abs(x):,.1f}" if isinstance(x, (int, float)) and x < 0 
        else f"${x:,.1f}" if isinstance(x, (int, float)) 
        else x for x in y_vals1],
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
        plot_bgcolor='#FFFFFF',
        title=f'Change in Average Monthly Rent ($) (2016-2023) {geo}',
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=12)
    )
    fig1.update_yaxes(
        tickfont=dict(size=12),
        tickformat = "$.0f",
    #tickprefix="$",  # Adds % sign to each tick
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Change in Average Monthly Rent'
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
        plot_bgcolor='#FFFFFF',
        title=f'Percentage Change in Average Monthly Rent ($) (2016-2023) {geo}',
        legend_title="Income",
    )
    fig2.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=12)
    )
    fig2.update_yaxes(
        tickfont=dict(size=12),
        tickformat = ".0f",
        ticksuffix="%",  # Adds % sign to each tick
        # fixedrange = True,
        title='% Change in Average Monthly Rent ($)'
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
    style_header_conditional = generate_style_header_conditional(table, text_align='right')
    table = table.rename(columns={'Metric': ''}).replace('Vacancy Rate','Vacancy Rate %')
    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [  # put in function?
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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
            lambda x: f"+{x:,.1f}" if isinstance(x, (int, float)) and x > 0 else (f"{x:,.1f}" if isinstance(x, (int, float)) else x)
        )

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align='right')
    table = table.rename(columns={'Metric': ''}).replace('Change in Vacancy Rate','Change in Vacancy Rate (percentage points)')
    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [  # put in function?
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "maxWidth": "200px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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
        plot_bgcolor='#FFFFFF',

        #paper_bgcolor= '#A8A8A8',
        title=f'Vacancy Rate (2016-2023) {geo}',

    ),
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=12),

    )
    fig1.update_yaxes(
        tickfont=dict(size=12),
        tickformat = ".0f",
        ticksuffix="%",  # Adds % sign to each tick
        title='Vacancy Rate (%)'
    )

    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=table_ChangeInVacancyRate.columns[1:],
        y=y_vals2,
        marker_color='#3eb549',
        customdata = [f"+{x:,.1f}" if isinstance(x, (int, float)) and x > 0 else \
                      (f"{x:,.1f}" if isinstance(x, (int, float)) else x) for x in y_vals2],
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
        plot_bgcolor='#FFFFFF',
        title=f'Change in Vacancy Rate (percentage points) (2016-2023) {geo}',
    )
    fig2.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=12)
    )
    fig2.update_yaxes(
        tickfont=dict(size=12),

        # range = [min(table['']),100]
        # fixedrange = True,
        title='Change in vacancy rate (pp)'
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
                                     'textAlign': 'right',
                                     "maxWidth": "50px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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

    for index, col in enumerate(table):  #set all columns to right align
        header_style = {  'if': {'header_index': 2 },
            'textAlign': 'right',
        }
        style_header_conditional.append(header_style)

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
                                     'textAlign': 'right',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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

    for index, col in enumerate(table):  #set all columns to right align
        header_style = {  'if': {'header_index': 2 },
            'textAlign': 'right',
        }
        style_header_conditional.append(header_style)
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
        plot_bgcolor='#FFFFFF',
        title=f'Housing Starts by Structure Type (2016-2023) {geo}',
        legend_title="Structure Type",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=12)
    )
    fig1.update_yaxes(
        tickfont=dict(size=12),
        tickformat = ",.0f",
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Housing Starts (# of units)'
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
        marker_color= hh_colors[4],
        hovertemplate=' %{x} Owner - <br>' + ' %{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals2,
        name='Rental',
        marker_color= hh_colors[3],
        hovertemplate=' %{x} Rental - <br>' + ' %{y:,.0f}<extra></extra>'

    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals3,
        name='Condo',
        marker_color= hh_colors[2],
        hovertemplate=' %{x} Condo - <br>' + ' %{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals4,
        name='Co-op',
        marker_color= hh_colors[1],
        hovertemplate=' %{x} Co-op - <br>' + ' %{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=list(table.columns.get_level_values(1))[1:],
        y=y_vals5,
        name='N/A',
        marker_color= hh_colors[0],
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
        plot_bgcolor='#FFFFFF',
        title=f'Housing Starts by Tenure (2016-2023) {geo}',
        legend_title="Tenure",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Year',
        tickfont=dict(size=12)
    )
    fig1.update_yaxes(
        tickfont=dict(size=12),
        tickformat = ",.0f",
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Housing Starts (# of units)'
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
            lambda x: (
            x if isinstance(x, str) and x.lower() == "n/a"  # Keep "n/a" as it is
            else f"+{x:,.0f}" if isinstance(x, (int, float)) and x > 0 
            else f"-{abs(x):,.0f}" if isinstance(x, (int, float)) and x < 0 
            else f"{x:,.0f}" if isinstance(x, (int, float)) 
            else x  # Fallback for other unexpected values
        )
        )
        #lambda x: f"+{x:,.0f}" if x > 0 else (f"-{abs(x):,.0f}" if x < 0 else f"{x:,.0f}"
    table.drop_duplicates(inplace=True)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align= "right")
    table = table.rename(columns={'Metric': 'Number of households in CHN', 
                                   '2021 - 2016': 'Change 2016-2021'}
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
                                     'textAlign': 'right',
                                    #  "maxWidth": "180px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     'width': '20%'
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
                                     'textAlign': 'right',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]

    for index, col in enumerate(table):
        header_style = {
            'if': {'header_index': index},
            'backgroundColor': '#002145' if index == 0 else '#39C0F7',
            'color': '#FFFFFF' if index == 0 else '#000000',
            'border': '1px solid #002145',
            'textAlign': 'right' if index == 1 else 'center',
        }
        # Remove bottom border if sub-header is empty
        if col[1] == '':
            header_style['border-bottom'] = 'none'

        style_header_conditional.append(header_style)
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
    table = table.replace("Owner", "Owner-occupied").replace("Renter", "Renter-occupied")
    # Generating plot
    fig1 = go.Figure()
    y_vals1 = table['2016'].values.flatten().tolist()
    y_vals2 = table['2021'].values.flatten().tolist()

    fig1.add_trace(go.Bar(
        x=["Owner-occupied", "Renter-occupied"],
        y=y_vals1,
        name= '2016',
        marker_color='#39c0f7',
        hovertemplate='2016 %{x} - <br>' + '%{y:,.0f}<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=["Owner-occupied", "Renter-occupied"],
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
        plot_bgcolor='#FFFFFF',
        title=f'Number of Households in CHN by tenure {geo}',
        legend_title="Year",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Tenure',
        tickfont=dict(size=12)
    )
    fig1.update_yaxes(
        tickfont=dict(size=12),
        tickformat = ",.0f",
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Number of Households in CHN (#)'
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
    y_vals1 = [y * 100 for y in table['2016'].values.flatten().tolist() if y != "n/a"]
    y_vals2 = [y * 100 for y in table['2021'].values.flatten().tolist() if y != "n/a"]
    

    fig1.add_trace(go.Bar(
        x=["Owner-occupied", "Renter-occupied"],
        y=y_vals1 * 100,
        name= '2016',
        marker_color= '#39c0f7',
        hovertemplate='2016 %{x} - <br>' + '%{y:.1f}%<extra></extra>'
    ))
    fig1.add_trace(go.Bar(
        x=["Owner-occupied", "Renter-occupied"],
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
        plot_bgcolor='#FFFFFF',
        title=f'Rate of CHN by tenure {geo}',
        legend_title="Year",
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Tenure',
        tickfont=dict(size=12)
    )
    fig1.update_yaxes(
        tickfont=dict(size=12),
        tickformat = ".0f",
        ticksuffix="%",  # Adds % sign to each tick
        # range = [min(table['']),100]
        # fixedrange = True,
        title='% of Households in CHN'
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
    style_header_conditional = generate_style_header_conditional(table,text_align='right')

    table = table[['Header to be deleted', 'Metric', '2021']]
    table = table.rename(columns={'Metric': '', 'Header to be deleted': ' '}).replace(' Rental Units', '', regex=True)

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "maxWidth": "130px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]
    style_data_conditional = []
    for i in range(len(table)):
        row_style = {
            'if': {'row_index': i},
            'backgroundColor': '#b0e6fc',  # change to "74d3f9" if secondary row
            'color': '#000000',
            'border': '1px solid #002145'
        }
        if i == 1:
            row_style = {
                'if': {'row_index': i},
                'backgroundColor': '#74d3f9',  # change to "74d3f9" if secondary row
                'color': '#000000',
                'border': '1px solid #002145'
            }

        style_data_conditional.append(row_style)


    new_data_style = [
            {
                'if': {'row_index': 1, 'column_id': ' '},
                'backgroundColor': '#39c0f7',
                'color': '#39c0f7',
                'border-top': 'none',
                'rowSpan': 2

            }
        ] + [{
            'if': {'row_index': i, 'column_id': ' '},
            'backgroundColor': '#39c0f7',
        } for i in [0, 1, 2]
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
                        hovertemplate=' %{label}</b><br>' + 'Value: %{value:,.0f}<br>' + '<extra></extra>',
                        
                ))

    # Plot layout settings
    fig1.update_layout(
                    # width = 900,
                    showlegend = True,
                    legend=dict(font = dict(size = 12)), #check tracegroupgap=50
                    # yaxis=dict(autorange="reversed"),

                    modebar_color = modebar_color,
                    modebar_activecolor = modebar_activecolor,
                    plot_bgcolor='#F8F9F9',
                    title = f'Share of Primary and Secondary Rental units {geo}',
                    legend_title = "Share",

                    )
    fig1.update_traces(textfont=dict(size=16, family='Arial Black', color='black'),
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
    style_header_conditional = generate_style_header_conditional(table, text_align='right')
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
                                     'textAlign': 'right',
                                     "maxWidth": "50px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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
    table = table.replace("Private rental market housing units", "Unsubsidized rental housing units")
    fig1 = go.Figure()

    fig1.add_trace(go.Pie(
        labels= table['Metric'],
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
    fig1.update_traces(textfont=dict(size=16, family='Arial Black', color='black'))

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
    style_header_conditional = generate_style_header_conditional(table, text_align='right')
    table = table.rename(columns={'Metric': ''}).replace(
        'Renters (unsubsidized)',
        'Number of occupied housing units that are below-market rent* in the private market').replace(
        '% of Total (Unsubsidized)', 'Percentage of occupied housing units that are below-market rent* in the private market')

    # Generating callback output to update table

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "width": "80%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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
            lambda x: f"+{x:,.1f}" if isinstance(x, (int, float)) and x > 0 else (f"{x:,.1f}" if isinstance(x, (int, float)) else x)
        )

    style_data_conditional = generate_style_data_conditional(table)
    #style_header_conditional = generate_style_header_conditional(table)
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
                                     'textAlign': 'right',
                                     "maxWidth": "75px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]
    #TODO: Use this if alignment is required as per the doc
    # style_header_conditional = generate_style_header_conditional(table, multi_header=True, extend=True)
    style_header_conditional = []
    for index, col in enumerate(table):
        style_header = {'if': {'header_index': index},
                        'backgroundColor': '#002145' if index == 0 else '#39C0F7',
                        'color': '#FFFFFF' if index == 0 else '#000000',
                         'textAlign': 'right' if index == 2 else 'center',
                        'border': '1px solid #002145',
                        }
        style_header_conditional.append(style_header)

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
    # if all(y == "n/a" for y in table[table.columns[3]].tolist()):
    #     y_vals1_1 = []
    # else:
    y_vals1_1 = [y * 100 for y in table[table.columns[3]].tolist() if y != "n/a"]


    # if all(y == "n/a" for y in table[table.columns[3]].tolist()):
    #     y_vals1_2 = []
    # else:
    y_vals1_2 = [y * 100 for y in table[table.columns[6]].tolist() if y != "n/a"]

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
        marker_color= '#3eb549',
        hovertemplate=' Age Group: %{x} <br> ' + '%{y:.1f}%<extra></extra>'
    ))

    # Plot layout settings
    fig1.update_layout(
        # width = 900,
        barmode='group',
        plot_bgcolor='#FFFFFF',
        title=f'Headship rates by Age (2016 & 2021) {geo}',
        legend_title="Headship Rate"
    )
    fig1.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Age Group',
        tickfont=dict(size=12)
    )
    fig1.update_yaxes(
        tickfont=dict(size=12),
        tickformat = ".0f",
        ticksuffix="%",  # Adds % sign to each tick
        # fixedrange = True,
        title='Headship Rate (%)',
    )

    y_vals2 = table[table.columns[7]].tolist()
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=table[table.columns[0]].unique(),
        y=y_vals2,
        marker_color='#39c0f7',
        customdata=[f"+{x:,.1f}" if isinstance(x, (int, float)) and x > 0 else (f"{x:,.1f}" if isinstance(x, (int, float)) else x) for x in y_vals2],
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
        plot_bgcolor='#FFFFFF',
        title=f'Percentage Point Change in headship rates by age (2016 & 2021) {geo}',
        legend_title="Headship rate",
    )
    fig2.update_xaxes(
        # fixedrange = True,
        # range = [0, 1],
        # tickformat =  ',.0%',
        title='Age Group',
        tickfont=dict(size=12)
    )
    fig2.update_yaxes(
        tickfont=dict(size=12),
        # range = [min(table['']),100]
        # fixedrange = True,
        title='Percentage point change in Headship Rate'
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
    # style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Age': 'Age Group'}).replace('75 and older', '75 and older**')
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
                                     'textAlign': 'right',
                                     "maxWidth": "100px"  #CHANGE THIS to update the column width according to doc
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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
    style_header_conditional = []
    for index, col in enumerate(table):
        style_header = {'if': {'header_index': index},
                        'backgroundColor': '#002145' if index == 0 else '#39C0F7',
                        'color': '#FFFFFF' if index == 0 else '#000000',
                        'textAlign': 'right' if index == 2 else 'center',  #'center' if index == 0 else 'right',  #
                        'border': '1px solid #002145',
                        }
        style_header_conditional.append(style_header)
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
    #style_header_conditional = generate_style_header_conditional(table)
    table = table.rename(columns={'Age': 'Age Group'}).replace('Total', '').replace('75 and older', '75 and older*')
    
    # Moving total from 1st column to 3rd column
    table.loc[table[table.columns[0]] == "", table.columns[2]] = "Total Suppressed Households"

    table.columns = pd.MultiIndex.from_tuples(
        [(col[0] + " (table 2 of 2)", col[1]) for col in table.columns]
    )
    
    if all(val == "n/a" for val in table[table.columns[:-1]][:-1]):  # Ignore last row (total row)
        table.loc[table["Age Group"] == "", table.columns[:-1]] = "n/a"
    
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
                                     'textAlign': 'right',
                                     "width": "25%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "width": "25%"
                                 } for c in table_columns[1:]
                             ]
    #new_data_style = generate_additional_data_style(table, table_columns)

    #change last row to be right aligned
    first_and_last_columns_ids = [table_columns[0]['id'], table_columns[-1]['id']]
    new_data_style = [
                         {
                             'if': {'row_index': len(table) - 1, 'column_id': j['id']},
                             'backgroundColor': '#39C0F7',
                             'color': '#000000',
                             'border-left': 'none',
                             'fontWeight': 'bold'

                         } for j in table_columns[1:-1]

                     ] + [
                         {
                             'if': {'row_index': len(table) - 1, 'column_id': col_id},
                             'fontWeight': 'bold',
                             'backgroundColor': '#39C0F7',
                             'color': '#000000',
                             "maxWidth": "200px",
                             'textAlign' :'right',
                         } for col_id in first_and_last_columns_ids
                     ]
    style_data_conditional.extend(new_data_style)

    style_header_conditional = []
    for index, col in enumerate(table):
        style_header = {'if': {'header_index': index},
                        'backgroundColor': '#002145' if index == 0 else '#39C0F7',
                        'color': '#FFFFFF' if index == 0 else '#000000',
                        'textAlign': 'right' if index == 2 else 'center',  #'center' if index == 0 else 'right',  #
                        'border': '1px solid #002145',
                        }
        style_header_conditional.append(style_header)
    return table_columns, table_data, style_data_conditional, style_cell_conditional, style_header_conditional

# output_11
@callback(
    Output('output_11', 'columns'),
    Output('output_11', 'data'),
    Output('output_11', 'style_data_conditional'),
    Output('output_11', 'style_cell_conditional'),
    Output('output_11', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_11', 'selected_columns'),
)
def update_output_11(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)
    # Generating table
    table = table_generator(geo, output_11, 'output_11')
    #multiply by 100 and % formatting needed
    table.drop_duplicates(inplace=True)
    table = number_formatting(table, [('Households in Core Housing Need (CHN) by priority population, 2021','Number of Households in CHN')], 0)
    table = percent_formatting(table, [('Households in Core Housing Need (CHN) by priority population, 2021', 'Rate of CHN')], mult_flag=1, conditions={})

    style_data_conditional = generate_style_data_conditional(table)
    # style_header_conditional = generate_style_header_conditional(table, text_align='right')
    table = table.replace("Youth", "HH head age 18-29 (Youth-led)").replace(
                          "SameGender", "HH with gender diverse couple or includes a transgender or non-binary person").replace(
                          "MentalHealth",  "HH with person(s) dealing with mental health and addictions activity limitation").replace(
                          "Veteran", "HH with Veteran(s)").replace(
                          "SingleMother", "Single-mother-led HH").replace(
                          "Women", "Women-led HH").replace(
                          "IndigenousHH", "Indigenous HH").replace(
                          "VisibleMinority", "Visible minority HH").replace(
                          "Black", "Black-led HH").replace(
                          "RecentImmigrant", "New migrant-led HH").replace(
                          "Refugee", "Refugee-claimant-led HH").replace(
                          "Under24", "HH head under 25").replace(
                          "Over65", "HH head over 65").replace(
                          "Over85", "HH head over 85").replace(
                          "Physical-AL", "HH with person(s) physical activity limitation").replace(
                          "Cognitive-Mental-Addictions-AL", "HH with person(s) dealing with cognitive, mental or addictions activity limitation").replace(
                          "TransNonBinary", "HH with Transgender or Non-binary person(s)").replace(
                          "Total", "Community (all HHs)")

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
                                     'textAlign': 'right',
                                     "width": "60%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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

    style_header_conditional = []
    for index, col in enumerate(table):
        style_header = {'if': {'header_index': index},
                        'backgroundColor': '#002145' if index == 0 else '#39C0F7',
                        'color': '#FFFFFF' if index == 0 else '#000000',
                        'textAlign': 'right' if index == 2 else 'center',  #'center' if index == 0 else 'right',  #
                        'border': '1px solid #002145',
                        }
        style_header_conditional.append(style_header)

    return table_columns, table_data, style_data_conditional, style_cell_conditional, style_header_conditional

# graph 11
@callback(
    Output('graph_11', 'figure'),

    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_11', 'selected_columns'),
)
def update_geo_figure_11(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale, refresh)

    # Generating table
    table = table_generator(geo, output_11, 'output_11')
    table.drop_duplicates(inplace=True)
    # TODO remove when we get the real data
    #table.loc[table['Priority Populations'].isin(['SameGender', 'TransgenderNonBinary']), 'Rate of CHN'] = 'n/a'
    table = table.replace("Youth", "Youth-led HH").replace(
                          "SameGender", "Same-gender HH").replace(
                          "MentalHealth",  "HH with mental health or addictions activity limitations").replace(
                          "Veteran", "Veteran HH").replace(
                          "SingleMother", "Single mother-led HH").replace(
                          "Women", "Women-led HH").replace(
                          "IndigenousHH", "Indigenous HH").replace(
                          "VisibleMinority", "Visible minority HH").replace(
                          "Black", "Black-led HH").replace(
                          "RecentImmigrant", "New migrant-led HH").replace(
                          "Refugee", "Refugee claimant-led HH").replace(
                          "Under24", "HH head under 25").replace(
                          "Over65", "HH head over 65").replace(
                          "Over85", "HH head over 85").replace(
                          "Physical-AL", "HH with physical activity limitation").replace(
                          "Cognitive-Mental-Addictions-AL", "HH with cognitive, mental or addictions activity limitation").replace(
                          "TransNonBinary", "Transgender or Non-binary HH").replace(
                          "Total", "Community (all HHs)")

    find_max = table[('Households in Core Housing Need (CHN) by priority population, 2021','Rate of CHN')].values

    if not table.empty:
        cleaned = [float(x) for x in find_max if isinstance(x, (int, float))]
        max_value = max(cleaned)
    # Generating plot
    fig = go.Figure()
    for i in table[('Households in Core Housing Need (CHN) by priority population, 2021','Priority Populations')]:
        plot_df_frag = table.loc[table[('Households in Core Housing Need (CHN) by priority population, 2021','Priority Populations')] == i, :]
        fig.add_trace(go.Bar(
            y=plot_df_frag[('Households in Core Housing Need (CHN) by priority population, 2021', 'Priority Populations')],
            x=plot_df_frag[('Households in Core Housing Need (CHN) by priority population, 2021', 'Rate of CHN')],
            name=i,
            marker_color="#3EB549" if i == 'Community (all HHs)' else "#39C0F7",
            orientation='h',
            hovertemplate='%{y} - ' + '%{x: .2%}<extra></extra>'
        ))


    # Plot layout settings
    fig.update_layout(
        width=1100,
        height=600,
        showlegend=False,
        legend=dict(font=dict(size=10)),
        yaxis=dict(autorange="reversed"),
        modebar_color=modebar_color,
        modebar_activecolor=modebar_activecolor,
        plot_bgcolor='#FFFFFF',
        title=f'Percentage of Households in Core Housing Need, by Priority Population, 2021<br>{geo}',
        legend_title="Priority Group",
        bargap=0.3
    )

    if not table.empty:
        fig.update_xaxes(
            fixedrange=True,
            tickformat=',.0%',
            title='% of Priority Population HH',
            tickfont=dict(size=12),
            range= [0, math.ceil(max_value * 10) / 10],
        )
        fig.update_yaxes(
            tickfont=dict(size=12),
            fixedrange=True,
            title='Priority Group'
        )

    return fig


# output_12 housing co-ops
@callback(
    Output('output_12', 'columns'),
    Output('output_12', 'data'),
    Output('output_12', 'style_data_conditional'),
    Output('output_12', 'style_cell_conditional'),
    Output('output_12', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_12', 'selected_columns'),
)
def update_output_12(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_12, 'output_12')
    
    if not table.empty:
        table = pd.DataFrame({'remove': 'Number of co-operative housing units*', '2024': table.values[0]})
    table = number_formatting(table, list(table.columns[1:]), 0)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = [] #generate_style_header_conditional(table)
    for index, col in enumerate(table):
        style_header = {  'if': {'header_index': index},
            'backgroundColor': '#002145' if index == 0 else '#39C0F7',
            'color': '#FFFFFF' if index == 0 else '#000000',
            'border-left': 'none',
            'textAlign': 'right' if index == 1 else 'center'

           }
        style_header_conditional.append(style_header)

    table = table.rename(columns={'remove': ' '})
    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "maxWidth": "50px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]

    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


# output_13a
@callback(
    Output('output_13a', 'columns'),
    Output('output_13a', 'data'),
    Output('output_13a', 'style_data_conditional'),
    Output('output_13a', 'style_cell_conditional'),
    Output('output_13a', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_13a', 'selected_columns'),
)
def update_output_13a(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_13, 'output_13a')
    
    table.drop_duplicates(inplace=True)
    

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table[['delete_me', 'totals']]

    table = table.replace("2016to2021_AffordableUnits_Built", "Number of affordable rental units for low and very low-income households built between 2016 and 2021").replace(
                        "2016to2021_AffordableUnits_Lost", "Number of affordable rental units for low and very low-income households lost between 2016 and 2021*").replace(
                        "Net Change in Affordable Units", "Net change in affordable rental units for low and very-low income households between 2016 and 2021")
        
    table = table.rename(columns={'delete_me': '', 'totals': ' '})
    table = number_formatting(table, list(table.columns[1:]), 0)
    # style_header_conditional = []
    # for index, col in enumerate(table):
    #     print('index', index, "col", col)
    #     header_style = {
    #         'if': {'header_index': index},
    #         'backgroundColor': '#002145' if index == 0 else '#39C0F7', #also want #E12FA for third row
    #         'color': '#FFFFFF' if index == 0 else '#000000',
    #         'border': '1px solid #002145',
    #     }
    #     style_header_conditional.append(header_style)


    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "width": "80%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]
    # style_data_conditional = []
    # for i in range(len(table)):
    #     row_style = {
    #         'if': {'row_index': i},
    #         'backgroundColor': '#39C0F7' if i == 0 else '#b0e6fc',
    #         'color': '#000000',
    #         'border': '1px solid #002145'
    #     }
    #     if i == 2:
    #         row_style = {
    #             'if': {'row_index': i},
    #             'backgroundColor': '#E1F2FA',
    #             'color': '#000000',
    #             'border': '1px solid #39C0F7'
    #         }
    #
    #     style_data_conditional.append(row_style)

    for index, col in enumerate(table):
        if index == 0:
            header_style = {
                'if': {'header_index': index},
                'backgroundColor': '#002145', #if index == 0 else 'transparent',
                'color': '#FFFFFF', #if index == 0 else 'transparent',
                # 'border-left': 'none',
                # 'border-right': 'none',
                'textAlign': 'center'

            }
            style_header_conditional.append(header_style)

        if index == 1:
            header_style = {
                'if': {'header_index': index},
                'backgroundColor': 'transparent',
                'color': 'transparent',
                'border-left': 'none',
                'border-right': 'none',
                'display': 'none'

            }
            style_header_conditional.append(header_style)


    # blank_row_style = [
    #     {
    #         'if': {'header_index': index},
    #         'color': 'transparent',
    #         'backgroundColor': 'transparent',
    #         'border-left': 'none',
    #         'border-right': 'none'
    #     } for j in table_columns
    # ]
    # style_data_conditional.extend(blank_row_style)
    # for i in range(len(table)):
    #     row_style = {
    #         'if': {'row_index': i},
    #         #'backgroundColor': '#b0e6fc' if i == 1 else '#39C0F7', #also want #E1F2FA for third row
    #         #'backgroundColor' : '#E1F2FA' if i == 2 else '#39C0F7',
    #         **({"backgroundColor": "#E1F2FA"} if i == 2 else {"backgroundColor": "#39C0F7"}),
    #         **({"backgroundColor": "#b0e6fc"} if i == 1 else {"backgroundColor": "#39C0F7"}),
    #         'color': '#000000',
    #         'border': '1px solid #002145'
    #     }
    #
    #     style_data_conditional.append(row_style)


    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional

# output_13b
@callback(
    Output('output_13b', 'columns'),
    Output('output_13b', 'data'),
    Output('output_13b', 'style_data_conditional'),
    Output('output_13b', 'style_cell_conditional'),
    Output('output_13b', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_13b', 'selected_columns'),
)
def update_output_13b(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_13, 'output_13b')
    
    table.drop_duplicates(inplace=True)
    

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table[['delete_me', 'totals']]

    table = table.replace("2016to2021_AffordableUnits_Built_VeryLowOnly", "Number of affordable rental units for very low-income households built between 2016 and 2021").replace(
                            "2016to2021_AffordableUnits_Lost_VeryLowOnly", "Number of affordable rental units for very low-income households lost between 2016 and 2021*").replace(
                            "Net Change in Affordable Units Very Low", "Net change in affordable rental units for very-low income households between 2016 and 2021")
    
        
    table = table.rename(columns={'delete_me': '', 'totals': ' '})
    table = number_formatting(table, list(table.columns[1:]), 0)

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "width": "80%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]

    for index, col in enumerate(table):
        if index == 0:
            header_style = {
                'if': {'header_index': index},
                'backgroundColor': '#002145', #if index == 0 else 'transparent',
                'color': '#FFFFFF', #if index == 0 else 'transparent',
                'textAlign': 'center'

            }
            style_header_conditional.append(header_style)

        if index == 1:
            header_style = {
                'if': {'header_index': index},
                'backgroundColor': 'transparent',
                'color': 'transparent',
                'border-left': 'none',
                'border-right': 'none',
                'display': 'none'

            }
            style_header_conditional.append(header_style)


    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


# output_13c
@callback(
    Output('output_13c', 'columns'),
    Output('output_13c', 'data'),
    Output('output_13c', 'style_data_conditional'),
    Output('output_13c', 'style_cell_conditional'),
    Output('output_13c', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_13c', 'selected_columns'),
)
def update_output_13c(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_generator(geo, output_13, 'output_13c')
    
    table.drop_duplicates(inplace=True)
    

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table)
    table = table[['delete_me', 'totals']]

    table = table.replace("2016to2021_AffordableUnits_Built_LowOnly", "Number of affordable rental units for low-income households built between 2016 and 2021").replace(
                        "2016to2021_AffordableUnits_Lost_LowOnly", "Number of affordable rental units for low-income households lost between 2016 and 2021*").replace(
                        "Net Change in Affordable Units Low", "Net change in affordable rental units for low income households between 2016 and 2021")
    
        
    table = table.rename(columns={'delete_me': '', 'totals': ' '})
    table = number_formatting(table, list(table.columns[1:]), 0)

    table_columns = [{"name": [geo, col], "id": col} for col in table.columns]

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "width": "80%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]

    for index, col in enumerate(table):
        if index == 0:
            header_style = {
                'if': {'header_index': index},
                'backgroundColor': '#002145', 
                'color': '#FFFFFF', 
                'textAlign': 'center'

            }
            style_header_conditional.append(header_style)

        if index == 1:
            header_style = {
                'if': {'header_index': index},
                'backgroundColor': 'transparent',
                'color': 'transparent',
                'border-left': 'none',
                'border-right': 'none',
                'display': 'none'

            }
            style_header_conditional.append(header_style)


    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional


# output_14a
@callback(
    Output('output_14a', 'columns'),
    Output('output_14a', 'data'),
    Output('output_14a', 'style_data_conditional'),
    Output('output_14a', 'style_cell_conditional'),
    Output('output_14a', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_14a', 'selected_columns'),
)
def update_output_14a(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table, median_income, median_rent = table_14a_generator(geo, final_joined_df)
    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align='right')


    table_columns = []

    median_row = ['Area Median Household Income', "", median_income, median_rent]
    for i,j  in zip(list(table.columns), median_row):
        table_columns.append({"name": [geo, i, j], "id": i})

    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]+ [
                                {
                                    'if': {'column_id': 'Affordable Shelter Cost (2020 CAD$)'},
                                    'maxWidth': "120px",

                                }
                            ]+ [
                                {
                                    'if': {'column_id': 'Income Category'},
                                    'maxWidth': "120px",
                                    'width' : '35%'

                                }
                            ]
    
    new_header_style = {
                            'if': {'column_id': table_columns[0]['id'], 'header_index': 2},
                            'borderRight': 'none'
                        }
                    
    style_header_conditional.append(new_header_style)
    
    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional

# Figure 14b
@callback(
    Output('graph_14b', 'figure'),

    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('graph_14b', 'selected_columns'),
)
def update_geo_figure_14b(geo, geo_c, scale, refresh):
    geo = get_filtered_geo(geo, geo_c, scale, refresh)

    # Generating table
    plot_df = graph_14b_generator(geo, final_joined_df)

    fig_14b = go.Figure()

    for h, c in zip(plot_df['HH_Size'].unique(), hh_colors):
        plot_df_frag = plot_df.loc[plot_df['HH_Size'] == h, :]
        fig_14b.add_trace(go.Bar(
                            y = plot_df_frag['Income_Category'],
                            x = plot_df_frag['Percent'],
                            name = h,
                            marker_color = c,
                            orientation = 'h', 
                            hovertemplate= '%{y}, ' + f'HH Size: {h} - ' + '%{x: .2%}<extra></extra>',
                        ))
        
    # Plot layout settings    
    fig_14b.update_layout(
                    legend_traceorder = 'normal', 
                    width = 900,
                    legend=dict(font = dict(size = 9)), 
                    modebar_color = modebar_color, 
                    modebar_activecolor = modebar_activecolor, 
                    yaxis=dict(autorange="reversed"), 
                    barmode='stack', 
                    plot_bgcolor='#F8F9F9', 
                    title = f'Percentage of Households in Core Housing Need, by Income Category and HH Size, 2021<br>{geo}',
                    legend_title = "Household Size"
                    )
    
    fig_14b.update_yaxes(
                        tickfont = dict(size = 12), 
                        fixedrange = True, 
                        title = 'Income Categories<br>(Max. affordable shelter costs)'
                        )
    fig_14b.update_xaxes(
                    fixedrange = True, 
                    tickformat =  ',.0%', 
                    title = '% of HH', 
                    tickfont = dict(size = 12)
                    )

    return fig_14b

# output_14b
@callback(
    Output('output_14b', 'columns'),
    Output('output_14b', 'data'),
    Output('output_14b', 'style_data_conditional'),
    Output('output_14b', 'style_cell_conditional'),
    Output('output_14b', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_14b', 'selected_columns'),
)
def update_output_14b(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_14b_generator(geo, final_joined_df)
    # pdb.set_trace()
    table = table[['Income Category (Max. affordable shelter cost)', '1 Person HH', '2 Person HH',
                        '3 Person HH', '4 Person HH', '5+ Person HH', 'Total']]
    
    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align='right')
    
    table_columns = []
    for i in table.columns:
        table_columns.append({"name": [geo, i],
                                "id": i, 
                                "type": 'numeric', 
                                "format": Format(
                                                group=Group.yes,
                                                scheme=Scheme.fixed,
                                                precision=0
                                                )})
    
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "maxWidth": "100px"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
                                 } for c in table_columns[1:]
                             ]+ [
                                {
                                    'if': {'column_id': 'Income Category (Max. affordable shelter cost)'},
                                    'maxWidth': "120px",

                                }
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

    
    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional

# output_16
@callback(
    Output('output_16', 'columns'),
    Output('output_16', 'data'),
    Output('output_16', 'style_data_conditional'),
    Output('output_16', 'style_cell_conditional'),
    Output('output_16', 'style_header_conditional'),
    Input('main-area', 'data'),
    Input('comparison-area', 'data'),
    Input('area-scale-store', 'data'),
    Input('output_16', 'selected_columns'),
)
def update_output_16(geo, geo_c, scale, selected_columns):
    geo = get_filtered_geo(geo, geo_c, scale, selected_columns)

    # Generating table
    table = table_16_generator(geo, projection_with_cma)

    style_data_conditional = generate_style_data_conditional(table)
    style_header_conditional = generate_style_header_conditional(table, text_align='right')
    
    table_columns = []
    for i in table.columns:
        table_columns.append({"name": [geo, i],
                                "id": i, 
                                "type": 'numeric', 
                                "format": Format(
                                                group=Group.yes,
                                                scheme=Scheme.fixed,
                                                precision=0
                                                )})
    
    style_cell_conditional = [
                                 {
                                     'if': {'column_id': table_columns[0]['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right',
                                     "width": "25%"
                                 }
                             ] + [
                                 {
                                     'if': {'column_id': c['id']},
                                     'backgroundColor': columns_color_fill[1],
                                     'textAlign': 'right'
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

    
    return table_columns, table.to_dict(
        'records'), style_data_conditional, style_cell_conditional, style_header_conditional

