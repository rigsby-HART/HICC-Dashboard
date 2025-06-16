# Importing Libraries
import pdb

import pandas as pd
import numpy as np
import warnings
import json, os
import geopandas as gpd
import fiona
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, ctx, callback
from sqlalchemy import create_engine
from shapely import wkb
import pyproj, time

fiona.supported_drivers
warnings.filterwarnings("ignore")
current_dir = os.path.dirname(os.path.abspath(__file__))

engine_new = create_engine('sqlite:///sources//hicc.db')
engine_old = create_engine('sqlite:///sources//old_hart.db')


mapped_geo_code = pd.read_sql_table('geocodes_integrated', engine_old.connect())

# Mapping Juan De Fuca as requested by Andrew
# mapped_geo_code = mapped_geo_code.replace(5917056, 5917054).replace('Juan de Fuca (CSD, BC)', 'Juan de Fuca (Part 1) (CSD, BC)')

# # Adding missing CSDs from HART file
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

cma_long_name_mapping = {'Campbellton (New Brunswick part / partie du Nouveau-Brunswick)': 'Campbellton (NB part)',
                         'Campbellton (partie du Québec / Quebec part)': 'Campbellton (QC part)',
                         'Hawkesbury (partie du Québec / Quebec part)': 'Hawkesbury (QC part)',
                         "Hawkesbury (Ontario part / partie de l'Ontario)": "Hawkesbury (ON part)",
                         "Ottawa - Gatineau (partie du Québec / Quebec part)": "Ottawa - Gatineau (QC part)",
                         "Ottawa - Gatineau (Ontario part / partie de l'Ontario)": "Ottawa - Gatineau (ON part)",
                         "Lloydminster (Saskatchewan part / partie de la Saskatchewan)": "Lloydminster (SK part)",
                         "Lloydminster (Alberta part / partie de l'Alberta)": "Lloydminster (AL part)"
                         }

province_code_map = {10 : 'NL', 11 : 'PEI', 12 : 'NS', 13 : 'NB',
                     24 : 'QC', 35 : 'ON', 46: 'MB', 47 : 'SK',
                     48: 'AL', 59: 'BC', 60: 'YT', 61 : 'NT', 62 : 'NU'}


cma_data = pd.read_sql_table('cma_data', engine_new.connect())
cma_data = cma_data[cma_data['CMAPUID'].notna()]
cma_data['CMAPUID'] = pd.to_numeric(cma_data['CMAPUID'], errors='coerce').astype('Int64').astype(str)
cma_data["CMANAME"] = cma_data["CMANAME"].map(cma_long_name_mapping).fillna(cma_data["CMANAME"])

# cma_data["CMAUID"] = cma_data["CMAPUID"].astype(str).str.zfill(3)
cma_data['PRUID'] = cma_data['PRUID'].astype(int)
cma_data['CDUID'] = cma_data['CSDUID'].str[:4].astype(int)

cma_data["CMANAME"] = cma_data["CMANAME"] + " (CMA, " + cma_data["PRUID"].map(province_code_map) + ")"

df_geo_list = pd.read_sql_table('geocodes', engine_old.connect())
# pdb.set_trace()

df_region_list = pd.read_sql_table('regioncodes', engine_old.connect())
df_region_list.columns = df_geo_list.columns

df_province_list = pd.read_sql_table('provincecodes', engine_old.connect())
df_province_list.columns = df_geo_list.columns

df_cma_list = cma_data[['CMAPUID', 'CMANAME']].drop_duplicates()
df_cma_list.columns = df_geo_list.columns


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


# pdb.set_trace()



mapped_geo_code = pd.concat([mapped_geo_code, required_cma_data], axis=0)
# pdb.set_trace()

master_parquet_path = f'./sources/mapdata_simplified/cma_data_parquet/combined_cma.parquet'
df_master = pd.read_parquet(master_parquet_path)

# if not isinstance(df_master.geometry.iloc[0], gpd.base.BaseGeometry):
df_master['geometry'] = df_master['geometry'].apply(wkb.loads)

# Step 3: Create GeoDataFrame
gdf_master = gpd.GeoDataFrame(df_master, geometry='geometry', crs="EPSG:3347")
# print(gdf_master.crs)  # Check if the CRS is already set
# print(pyproj.CRS(gdf_master.crs).to_wkt())  # Print detailed CRS info

gdf_master = gdf_master.to_crs("EPSG:4326")

# Importing Province Map

gdf_p_code_added = gpd.read_file('./sources/mapdata_simplified/province.shp')
gdf_p_code_added = gdf_p_code_added.set_index('Geo_Code')
# gdf_p_code_added["rand"] = np.random.randint(1, 100, len(gdf_p_code_added))

# Importing subregions which don't have data

not_avail = pd.read_sql_table('not_available_csd', engine_old.connect())
not_avail['CSDUID'] = not_avail['CSDUID'].astype(str)

# Configuration for plot icons

config = {'displayModeBar': True, 'displaylogo': False,
          'modeBarButtonsToRemove': ['zoom', 'lasso2d', 'pan', 'select', 'autoScale', 'resetScale', 'resetViewMapbox']}

# Colors for map

map_colors_province = ['#1a3758', '#78cb80', '#74d3f9', '#a480bb', '#80c2c0', '#7480dd', '#ffe6d6', '#e98098',
                       '#b6657c', '#490076', '#008481', '#622637']
map_colors_wo_black = ['#7480dd', '#1a3758', '#7480dd', '#b6657c', '#622637', '#80c2c0', '#78cb80', '#ffe6d6',
                       '#e98098', '#a480bb', '#490076', '#008481', '#74d3f9']
map_colors_w_black = ['#000000', '#1a3758', '#7480dd', '#b6657c', '#622637', '#80c2c0', '#78cb80', '#ffe6d6', '#e98098',
                      '#a480bb', '#490076', '#008481', '#74d3f9']

# Map color opacity

opacity_value = 0.2

# Default location in the map

default_value = "Canada" #Montréal (CMA, QC)

# Plot icon colors

modebar_color = '#099DD7'
modebar_activecolor = '#044762'

# Setting orders of areas in dropdown

order = mapped_geo_code.copy()
order['Geo_Code'] = order['Geo_Code'].astype(str)
order = order.sort_values(by=['Province_Code', 'Region_Code', 'Geo_Code'])
# pdb.set_trace()
# Setting a default map which renders before the dashboard is fully loaded

# gdf_r_filtered = gpd.read_file(f'./sources/mapdata_simplified/region_data/{province_code}.shp',
#                                        encoding='UTF-8')

# gdf_r_filtered["rand"] = [i for i in range(0, len(gdf_r_filtered))]


# gdf_r_filtered = gdf_r_filtered.set_index('CDUID')
gdf_p_code_added["rand"] = np.random.randint(1, 100, len(gdf_p_code_added))

fig_m = go.Figure()


fig_m.add_trace(go.Choroplethmapbox(geojson=json.loads(gdf_p_code_added.geometry.to_json()),
                                    locations=gdf_p_code_added.index,
                                    z=gdf_p_code_added.rand,
                                    showscale=False,
                                    hovertext=gdf_p_code_added.NAME,
                                    marker=dict(opacity=opacity_value),
                                    marker_line_width=.5))

fig_m.update_layout(mapbox_style="carto-positron",
                    mapbox_center={"lat": gdf_p_code_added.geometry.centroid.y.mean() + 10,
                                   "lon": gdf_p_code_added.geometry.centroid.x.mean()},
                    height=500,
                    width=1000,
                    mapbox_zoom=1.4,
                    autosize=True)
# fig_m.add_trace(go.Choroplethmapbox(geojson=json.loads(gdf_r_filtered.geometry.to_json()),
#                                          locations=gdf_r_filtered.index,
#                                          z=gdf_r_filtered.rand,
#                                          showscale=False,
#                                          colorscale=map_colors_wo_black,
#                                          text=gdf_r_filtered.CDNAME,
#                                          hovertemplate='%{text} - %{location}<extra></extra>',
#                                          marker=dict(opacity=opacity_value),
#                                          marker_line_width=.5))

# fig_m.update_layout(mapbox_style="carto-positron",
#                          mapbox_center={"lat": gdf_r_filtered['lat'].mean() + 3, "lon": gdf_r_filtered['lon'].mean()},
#                          mapbox_zoom=4.0,
#                          margin=dict(b=0, t=10, l=0, r=10),
#                          modebar_color=modebar_color, modebar_activecolor=modebar_activecolor,
#                          autosize=True)
# Setting layout for dashboard


layout = html.Div(children=[

    # Store Area/Comparison Area/Clicked area scale info in local storage

    dcc.Store(id='area-scale-store', storage_type='local'),
    dcc.Store(id='main-area', storage_type='local'),
    dcc.Store(id='comparison-area', storage_type='local'),
    dcc.Store(id='geo-mode', data=None),
    dcc.Store(id='current_level_store', data=None),

    # Main Layout

    html.Div(children=[

            # Select Area Dropdowns
            html.Div(
                children=[

                html.Div(
                    children=[
                        html.Strong('Select Census Geographic Level'),
                        dcc.RadioItems(
                            id='view_mode_toggle',
                            options=[
                                {'label': 'PT-CD-CSD', 'value': 'PT-CD-CSD'},
                                {'label': 'PT-CMA', 'value': 'PT-CMA'}
                            ],
                            value='PT-CD-CSD',  # default selection
                            # inline=True,
                            labelStyle={'display': 'inline-block', 'padding-right': '15px'},
                            inputStyle={"margin-right": "5px"}
                        )
                    ],
                    className='radio-box-lgeo',
                    style={'margin-bottom': '10px'}
                ),

                # Main Area Dropdown
                html.Div(
                    id='all-geo-dropdown-parent',
                    children=[
                        html.Strong('Select Census Geography'),
                        dcc.Dropdown(order['Geography'].unique(), default_value, id='all-geo-dropdown'),
                    ],
                    className='dropdown-lgeo'
                ),

                

                # Comparison Area Dropdown
                html.Div(
                    id='comparison-geo-dropdown-parent',
                    children=[
                        html.Strong('Select Comparison Census Geography (Optional)'),
                        dcc.Dropdown(order['Geography'].unique(), id='comparison-geo-dropdown'),
                    ],
                    className='dropdown-lgeo', style={'display': 'none'}
                )
            ],
            style={'display': 'flex', 'flexDirection': 'column'},
                className='dropdown-box-lgeo'
            ),

            # Area Scale Buttons
            html.Div(children=[

                html.Div(children=[
                    html.Div(children=[
                        html.Button('Province/Territory', 
                                    title= "'Province' and 'territory' refer to the major political units of Canada. Canada is divided into 10 provinces and 3 territories.",
                                    id='to-province-1', n_clicks=0, className = 'region-button-lgeo'),
                    ], className='region-button-box-lgeo'
                    ),

                    html.Div(children=[
                        html.Button('Census Divisions (Regions)',
                                    title='A provincially legislated area like counties, regional districts or equivalent areas. Census divisions are intermediate geographic areas between the province/territory level and the municipality (census subdivision).',
                                    id='to-region-1', n_clicks=0, className='region-button-lgeo'),
                    ], className='region-button-box-lgeo'
                    ),
                ], style={'display': 'flex', 'gap': '10px'}),


                html.Div(children=[
                    html.Div(children=[
                        html.Button('Census Subdivisions (Municipalities)', 
                                    title= "A provincially-legislated area at the municipal scale, or areas treated as municipal equivalents for statistical purposes (e.g. reserves, settlements and unorganized territories). Municipal status is defined by laws in effect in each province and territory in Canada.",
                                    id='to-geography-1', n_clicks=0, className = 'region-button-lgeo'),
                    ], className='region-button-box-lgeo'
                    ),
                    
                    html.Div(children=[
                        html.Button('Census Metropolitan Areas (Metro Regions)', 
                                    title= "Census metropolitan areas (CMA) are formed of one or more adjacent municipalities that are centred on and have a high degree of integration with a large population centre, known as the core. A CMAis delineated using adjacent census subdivisions (CSDs) as building blocks.",
                                    id='to-cma-1', n_clicks=0, className = 'region-button-lgeo'),
                    ], className='region-button-box-lgeo'
                    ),

                ], style={'display': 'flex', 'gap': '10px', 'marginTop': '10px'}),

            ],    className='scale-button-box-lgeo'
            ),

            # Area Scale Buttons
            # html.Div(children=[

            #     html.Div(children=[
            #         html.Button('Map View PT-CD-CSD',
            #                     title='View Geography Hierarchy from Province to Census Division (CD) to Census Subdivision (CSD)',
            #                     id='pt-cd-csd-btn', n_clicks=0, className='region-button-lgeo'),
            #     ], className='region-button-box-lgeo'
            #     ),
            #     html.Div(children=[
            #         html.Button('Map View PT-CMA',
            #                     title='View Geography Hierarchy from Province to Census Metropolitan Area (CMA)',
            #                     id='pt-cma-btn', n_clicks=0, className='region-button-lgeo'),
            #     ], className='region-button-box-lgeo'
            #     ),
            # ],
            # ),
            # Area Map picker

            html.Div(children=[
                html.Div(
                    dcc.Graph(
                        id='canada_map',
                        figure=fig_m,
                        config=config,
                    ),
                    className='map-lgeo'

                ),

                # Map Reset Button
                html.Div(children=[
                    html.Button('Reset Map', id='reset-map', n_clicks=0),
                ], className='reset-button-lgeo'
                ),

            ], className='map-area-box-lgeo'
            ),

        ], className='dashboard-pg1-lgeo'
    ),
], className='background-lgeo'
)


# Callback for storing selected areas and area scale level

@callback(
    Output('main-area', 'data'),
    Output('comparison-area', 'data'),
    Output('area-scale-store', 'data'),
    Output('geo-mode', 'data'),
    Input('all-geo-dropdown', 'value'),
    Input('comparison-geo-dropdown', 'value'),
    Input('all-geo-dropdown-parent', 'n_clicks'),
    Input('comparison-geo-dropdown-parent', 'n_clicks'),
    Input('to-geography-1', 'n_clicks'),
    Input('to-region-1', 'n_clicks'),
    Input('to-province-1', 'n_clicks'),
    Input('to-cma-1', 'n_clicks'),
    Input('view_mode_toggle', 'value') # radio button functionality
    # Input('pt-cd-csd-btn', 'n_clicks'),
    # Input('pt-cma-btn', 'n_clicks') 

)
def store_geo(geo, geo_c, btn1, btn2, btn3, btn4, btn5, btn6, geo_mode_selected):
    id_name = str(ctx.triggered_id)

    # if id_name == 'pt-cd-csd-btn':
    #     geo_mode = 'PT-CD-CSD'  # Show Province → CD → CSD
    # elif id_name == 'pt-cma-btn':
    #     geo_mode = 'PT-CMA'  # Show Province → CMA
    # else:
    #     geo_mode = None  # No mode selected yet

    return geo, geo_c, id_name, geo_mode_selected


@callback(
    Output('to-province-1', 'disabled'),
    Output('to-region-1', 'disabled'),
    Output('to-geography-1', 'disabled'),
    Output('to-cma-1', 'disabled'),
    Input('all-geo-dropdown', 'value'),
    Input('view_mode_toggle', 'value'),
    Input('current_level_store', 'data'),
    Input('reset-map', 'n_clicks'),
)
def update_button_states(selected_geo, view_mode, current_level, reset_clicks):

    if ctx.triggered_id == 'reset-map':
        return True, True, True, True 

    # All buttons disabled by default
    province_disabled = True
    cd_disabled = True
    csd_disabled = True
    cma_disabled = True

    if (view_mode == "PT-CD-CSD") or (view_mode is None):
        if (current_level == 'province') or ('Province' in selected_geo):
            cd_disabled = False
        elif (current_level == 'cd') or ('CD' in selected_geo):
            province_disabled = False
            csd_disabled = False
        elif (current_level == 'csd') or ('CSD' in selected_geo):
            province_disabled = False
            cd_disabled = False
        elif (current_level == 'reset') or (selected_geo == 'Canada'):
            pass
        

    elif view_mode == "PT-CMA":
        if (current_level == 'province') or ('Province' in selected_geo):
            cma_disabled = False
        elif (current_level == 'cma')  or ('CMA' in selected_geo):
            province_disabled = False
        elif (current_level == 'reset') or (selected_geo == 'Canada'):
            pass


    return province_disabled, cd_disabled, csd_disabled, cma_disabled


@callback(
    Output('current_level_store', 'data'),
    Input('to-province-1', 'n_clicks'),
    Input('to-region-1', 'n_clicks'),
    Input('to-geography-1', 'n_clicks'),
    Input('to-cma-1', 'n_clicks'),
    Input('reset-map', 'n_clicks'),
    prevent_initial_call=True
)
def update_current_level(n1, n2, n3, n4, n5):
    triggered_id = ctx.triggered_id

    if triggered_id == 'to-province-1':
        return 'province'
    elif triggered_id == 'to-region-1':
        return 'cd'
    elif triggered_id == 'to-geography-1':
        return 'csd'
    elif triggered_id == 'to-cma-1':
        return 'cma'
    elif triggered_id == 'reset-map':
        return None

    return None  # fallback


@callback(
    Output('all-geo-dropdown', 'options'),
    Input('view_mode_toggle', 'value')
)
def update_dropdown_options(view_mode):
    if view_mode == 'PT-CMA':
        # Show only CMA, Province, and Canada
        options = mapped_geo_code[
            mapped_geo_code['Geography'].str.contains('CMA|Province|Canada', case=False, na=False)
        ]['Geography'].sort_values().unique().tolist()
    else:
        # Default or PT-CD-CSD: Show Province, CD, CSD, and Canada
        options = mapped_geo_code[
            mapped_geo_code['Geography'].str.contains('Province|CD|CSD|Canada', case=False, na=False)
        ]['Geography'].sort_values().unique().tolist()

    return [{'label': geo, 'value': geo} for geo in options]


# Area Selection Map

# Province Map generator
def province_map(value, random_color):
    clicked_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Province_Code'].tolist()[0]
    gdf_p_code_added['Geo_Code'] = gdf_p_code_added.index

    if random_color == True:
        # gdf_p_code_added["rand"] = 0
        gdf_p_code_added["rand"] = [round(i/(len(gdf_p_code_added) -1)*100) for i in range(0,len(gdf_p_code_added))]
        map_colors = map_colors_province
    else:
        gdf_p_code_added["rand"] = gdf_p_code_added['Geo_Code'].apply(lambda x: 0 if x == int(clicked_code) else 100)
        map_colors = ['#37BB31', '#74D3F9']

    fig_m = go.Figure()

    fig_m.add_trace(go.Choroplethmapbox(geojson=json.loads(gdf_p_code_added.geometry.to_json()),
                                        locations=gdf_p_code_added.index,
                                        z=gdf_p_code_added.rand,
                                        showscale=False,
                                        colorscale=map_colors,
                                        text=gdf_p_code_added.NAME,
                                        hovertemplate='%{text} - %{location}<extra></extra>',
                                        marker=dict(opacity=opacity_value),
                                        marker_line_width=.5))
    # fig_m.update_layout(mapbox_style="carto-positron",
    #                     mapbox_center={"lat": gdf_p_code_added['lat'].mean(),
    #                                    "lon": gdf_p_code_added['lon'].mean()},
    #                     mapbox_zoom=3.8,
    #                     margin=dict(b=0, t=10, l=0, r=10),
    #                     modebar_color=modebar_color, modebar_activecolor=modebar_activecolor,
    #                     autosize=True)
    fig_m.update_layout(mapbox_style="carto-positron",
                        mapbox_center = {"lat": gdf_p_code_added['lat'].mean()+10, "lon": gdf_p_code_added['lon'].mean()},
                        mapbox_zoom = 2.0,
                        margin=dict(b=0,t=10,l=0,r=10),
                        modebar_color = modebar_color, modebar_activecolor = modebar_activecolor,
                        autosize=True)

    return fig_m


# Region Map generator
def region_map(value, random_color, clicked_code):
    if clicked_code == 'N':
        clicked_province_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Province_Code'].tolist()[
            0]
        clicked_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Region_Code'].tolist()[0]

        gdf_r_filtered = gpd.read_file(f'./sources/mapdata_simplified/region_data/{clicked_province_code}.shp',
                                       encoding='UTF-8')
        # print('region from dropdown', clicked_province_code)

    else:

        gdf_r_filtered = gpd.read_file(f'./sources/mapdata_simplified/region_data/{clicked_code}.shp', encoding='UTF-8')

    if random_color == True:
        gdf_r_filtered["rand"] = [i for i in range(0, len(gdf_r_filtered))]
        map_colors = map_colors_wo_black

    else:
        gdf_r_filtered["rand"] = gdf_r_filtered['CDUID'].apply(lambda x: 0 if x == clicked_code else 100)
        map_colors = ['#37BB31', '#74D3F9']

    gdf_r_filtered = gdf_r_filtered.set_index('CDUID')

    fig_mr = go.Figure()

    fig_mr.add_trace(go.Choroplethmapbox(geojson=json.loads(gdf_r_filtered.geometry.to_json()),
                                         locations=gdf_r_filtered.index,
                                         z=gdf_r_filtered.rand,
                                         showscale=False,
                                         colorscale=map_colors,
                                         text=gdf_r_filtered.CDNAME,
                                         hovertemplate='%{text} - %{location}<extra></extra>',
                                         marker=dict(opacity=opacity_value),
                                         marker_line_width=.5))

    # fig_mr.update_layout(mapbox_style="carto-positron",
    #                      mapbox_center={"lat": gdf_r_filtered['lat'].mean() + 3, "lon": gdf_r_filtered['lon'].mean()},
    #                      mapbox_zoom=4.0,
    #                      margin=dict(b=0, t=10, l=0, r=10),
    #                      modebar_color=modebar_color, modebar_activecolor=modebar_activecolor,
    #                      autosize=True)
    fig_mr.update_layout(mapbox_style="carto-positron",
                            mapbox_center = {"lat": gdf_r_filtered['lat'].mean(), "lon": gdf_r_filtered['lon'].mean()},
                            mapbox_zoom = 3.0,
                            margin=dict(b=0,t=10,l=0,r=10),
                            modebar_color = modebar_color, modebar_activecolor = modebar_activecolor,
                            autosize=True)

    return fig_mr


# Subregion Map generator
def subregion_map(value, random_color, clicked_code):
    if clicked_code == 'N':
        # pdb.set_trace()
        clicked_region_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Region_Code'].tolist()[0]
        clicked_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Geo_Code'].tolist()[0]
        clicked_code = str(clicked_code)
        
    #     try:
    #         gdf_sr_filtered = gpd.read_file(f'./sources/mapdata_simplified/subregion_data/{clicked_region_code}.shp')
    #     except fiona.errors.DriverError:
    #         gdf_sr_filtered = gdf_p_code_added
    #         gdf_sr_filtered['CSDUID'] = province_code
    #         gdf_sr_filtered['CSDNAME'] = value

    # else:
    #     clicked_code_region = clicked_code[:4]
    #     try:
    #         gdf_sr_filtered = gpd.read_file(f'./sources/mapdata_simplified/subregion_data/{clicked_code_region}.shp')
    #     except fiona.errors.DriverError:
    #         gdf_sr_filtered = gdf_p_code_added
    #         gdf_sr_filtered['CSDUID'] = province_code
    #         gdf_sr_filtered['CSDNAME'] = value
        gdf_sr_filtered = gpd.read_file(f'./sources/mapdata_simplified/subregion_data/{clicked_region_code}.shp')
        
    else:
            clicked_code_region = clicked_code[:4]
            gdf_sr_filtered = gpd.read_file(f'./sources/mapdata_simplified/subregion_data/{clicked_code_region}.shp')

    if random_color == True:
        gdf_sr_filtered["rand"] = gdf_sr_filtered['CSDUID'].apply(
            lambda x: 0 if x in not_avail['CSDUID'].tolist() else np.random.randint(30, 100))

        if 0 in gdf_sr_filtered["rand"].tolist():
            colorlist = map_colors_w_black
        else:
            colorlist = map_colors_wo_black

    else:
        gdf_sr_filtered["rand"] = gdf_sr_filtered['CSDUID'].apply(
            lambda x: 0 if x in not_avail['CSDUID'].tolist() else (50 if x == clicked_code else 100))

        if 0 in gdf_sr_filtered["rand"].tolist():
            colorlist = ['#000000', '#37BB31', '#74D3F9']
        else:
            colorlist = ['#37BB31', '#74D3F9']

    gdf_sr_filtered = gdf_sr_filtered.set_index('CSDUID')

    fig_msr = go.Figure()

    fig_msr.add_trace(go.Choroplethmapbox(geojson=json.loads(gdf_sr_filtered.geometry.to_json()),
                                          locations=gdf_sr_filtered.index,
                                          z=gdf_sr_filtered.rand,
                                          showscale=False,
                                          text=gdf_sr_filtered.CSDNAME,
                                          hovertemplate='%{text} - %{location}<extra></extra>',
                                          colorscale=colorlist,
                                          marker=dict(opacity=opacity_value),
                                          marker_line_width=.5))

    
    max_bound = max(abs((gdf_sr_filtered['lat'].max() - gdf_sr_filtered['lat'].min())),
                    abs((gdf_sr_filtered['lon'].max() - gdf_sr_filtered['lon'].min()))) * 111

    zoom = 11.5 - np.log(max_bound)

    if len(gdf_sr_filtered) == 1:
        zoom = 9

    fig_msr.update_layout(mapbox_style="carto-positron",
                          mapbox_center={"lat": gdf_sr_filtered['lat'].mean(), "lon": gdf_sr_filtered['lon'].mean()},
                          mapbox_zoom=zoom,
                          margin=dict(b=0, t=10, l=0, r=10),
                          modebar_color=modebar_color, modebar_activecolor=modebar_activecolor,
                          autosize=True)
    return fig_msr


# Metropolitan Map generator
def metropolitan_map(value, random_color, clicked_code, zoom_offset=0):
    
    # print(gdf_master)

    if len(clicked_code) == 2:  # If a province is clicked in PT-CMA mode
        # Load all CMAs in the province
        cma_mapped_geo_codes = mapped_geo_code[mapped_geo_code['Geography'].str.contains('CMA')]
        province_cmas = cma_mapped_geo_codes[cma_mapped_geo_codes['Province_Code'] == clicked_code]
        # pdb.set_trace()
        province_cma_codes = province_cmas['Geo_Code'].tolist()
        # print(clicked_code, province_cma_codes, province_cmas, cma_mapped_geo_codes)

        gdf_m_filtered = gdf_master[gdf_master['CMAPUID'].isin(province_cma_codes)]

        if gdf_m_filtered.empty:
            return None
        
        

    else:
        # clicked_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Geo_Code'].tolist()[0]
        gdf_m_filtered = gdf_master[gdf_master['CMAPUID'] == clicked_code]


    if random_color == True:
        gdf_m_filtered["rand"] = [i for i in range(0, len(gdf_m_filtered))]
        map_colors = map_colors_wo_black

    else:
        gdf_m_filtered["rand"] = gdf_m_filtered['CMAPUID'].apply(lambda x: 1 if x == clicked_code else 0)
        map_colors = ['#37BB31', '#74D3F9']

    gdf_m_filtered = gdf_m_filtered.set_index('CMAPUID')

    # pdb.set_trace()

    fig_mm = go.Figure()

    fig_mm.add_trace(go.Choroplethmapbox(geojson=json.loads(gdf_m_filtered.geometry.to_json()),
                                         locations=gdf_m_filtered.index,
                                         z=gdf_m_filtered.rand,
                                         showscale=False,
                                         colorscale=map_colors,
                                         text=gdf_m_filtered.CMANAME,
                                         hovertemplate='%{text} - %{location}<extra></extra>',
                                         marker=dict(opacity=opacity_value),
                                         marker_line_width=.5))

    # fig_mr.update_layout(mapbox_style="carto-positron",
    #                      mapbox_center={"lat": gdf_r_filtered['lat'].mean() + 3, "lon": gdf_r_filtered['lon'].mean()},
    #                      mapbox_zoom=4.0,
    #                      margin=dict(b=0, t=10, l=0, r=10),
    #                      modebar_color=modebar_color, modebar_activecolor=modebar_activecolor,
    #                      autosize=True)


    if len(str(clicked_code)) == 2:
        zoom = 4 + zoom_offset
        fig_mm.update_layout(mapbox_style="carto-positron",
                                mapbox_center = {"lat": gdf_m_filtered['lat'].mean(), "lon": gdf_m_filtered['lon'].mean()},
                                mapbox_zoom = zoom,
                                margin=dict(b=0,t=10,l=0,r=10),
                                modebar_color = modebar_color, 
                                modebar_activecolor = modebar_activecolor,
                                autosize=True)
    else:
        max_bound = max(abs((gdf_m_filtered['lat'].max() - gdf_m_filtered['lat'].min())),
                    abs((gdf_m_filtered['lon'].max() - gdf_m_filtered['lon'].min()))) * 11

        zoom = 11.5 - np.log(max_bound)

        if len(gdf_m_filtered) == 1:
            zoom = 8

        if zoom_offset:
            zoom += zoom_offset


        fig_mm.update_layout(mapbox_style="carto-positron",
                            mapbox_center={"lat": gdf_m_filtered['lat'].mean(), "lon": gdf_m_filtered['lon'].mean()},
                            mapbox_zoom=zoom,
                            margin=dict(b=0, t=10, l=0, r=10),
                            modebar_color=modebar_color, modebar_activecolor=modebar_activecolor,
                            autosize=True)


    return fig_mm


# Callback logic for the map picker

@callback(
    Output('canada_map', 'figure'),
    Output('all-geo-dropdown', 'value'),
    Input('canada_map', 'clickData'),
    Input('reset-map', 'n_clicks'),
    Input('all-geo-dropdown', 'value'),
    Input('all-geo-dropdown-parent', 'n_clicks'),
    Input('to-geography-1', 'n_clicks'),
    Input('to-region-1', 'n_clicks'),
    Input('to-province-1', 'n_clicks'),
    Input('to-cma-1', 'n_clicks'),
    Input('view_mode_toggle', 'value')
)
def update_map(clickData, btn1, value, btn2, btn3, btn4, btn5, btn6, view_mode):
    # If no area is selected, then map will show Canada Map

    # if value == None:
    #     value = default_value

    if value is None or (ctx.triggered_id == 'all-geo-dropdown' and value == default_value):
        fig_canada = province_map(default_value, True)
        return fig_canada, default_value

    clicked_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Geo_Code'].tolist()[0]
    # pdb.set_trace()
    clicked_code = str(clicked_code)
    # print('in update map', clicked_code)

    # Added this line on 17-03-2025, to not break the map if Canada is selected from dropdown menu
    if len(clicked_code) == 1 and 'all-geo-dropdown-parent' == ctx.triggered_id:
        fig_m = province_map(value, True)
        return fig_m, value

    if ctx.triggered_id == "reset-map":
        fig_m = province_map(value, True)
        return fig_m, default_value

    # # Ensure geo_mode is set properly
    # if ctx.triggered_id in ['pt-cd-csd-btn', 'pt-cma-btn']:
    #     geo_mode = 'PT-CD-CSD' if ctx.triggered_id == 'pt-cd-csd-btn' else 'PT-CMA'

    
    if (ctx.triggered_id == "to-province-1") or (len(clicked_code) == 2 and 'all-geo-dropdown-parent' == ctx.triggered_id):
        province_code = clicked_code[:2]
        province_name = df_province_list.query("Geo_Code == "+ f"{province_code}")['Geography'].tolist()[0]
        fig_m = province_map(province_name, False)
        return fig_m, province_name
    
    if (ctx.triggered_id == "to-region-1") or (len(clicked_code) == 4 and 'all-geo-dropdown-parent' == ctx.triggered_id):

        if len(clicked_code) == 4:
            census_div_code = clicked_code[:4]  # Extract CD code
            census_div_name = df_region_list.query("Geo_Code == "+ f"{census_div_code}")['Geography'].tolist()[0]
            fig_mr = region_map(census_div_name, False, 'N')
            return fig_mr, census_div_name
        else:
            province_code = clicked_code[:2]  # Extract Province code
            province_name = df_province_list.query("Geo_Code == "+ f"{province_code}")['Geography'].tolist()[0]
            fig_mr = region_map(province_name, True, 'N')
            return fig_mr, province_name
    
    if (ctx.triggered_id == "to-cma-1") or (len(clicked_code) == 5 and 'all-geo-dropdown-parent' == ctx.triggered_id):
        if len(clicked_code) == 5:
            zoom_offset = 5 if view_mode == "PT-CMA" and int(clicked_code[:2]) in ["11", "61"] else 0
            fig_mm = metropolitan_map(value, True, clicked_code, zoom_offset)
            # pdb.set_trace()
            if fig_mm is None:
                fig_m = province_map(province_name, True)
                return fig_m, province_name
            else:
                region_name = df_cma_list.loc[df_cma_list['Geo_Code'] == clicked_code, 'Geography'].tolist()[0]
                return fig_mm, region_name
        else:
            province_code = clicked_code[:2]  # Extract Province code
            province_name = df_province_list.query("Geo_Code == "+ f"{province_code}")['Geography'].tolist()[0]
            zoom_offset = 5 if view_mode == "PT-CMA" and province_code in ["11", "61"] else 0
            fig_mm = metropolitan_map(province_name, True, clicked_code, zoom_offset)
            return fig_mm, province_name
    
    if (ctx.triggered_id == "to-geography-1") or (len(clicked_code) > 5 and 'all-geo-dropdown-parent' == ctx.triggered_id):

        if len(clicked_code) == 4:
            fig_msr = subregion_map(value, True, 'N')
            return fig_msr, value
        else:
            fig_msr = subregion_map(value, False, 'N')
            return fig_msr, value
    
    if isinstance(clickData, dict):
        clicked_code = str(clickData['points'][0]['location'])
        # If Province is Clicked
        if len(clicked_code) == 2:
            province_name = df_province_list.query("Geo_Code == "+ f"{clicked_code}")['Geography'].tolist()[0]
            if view_mode == 'PT-CMA':
                # print(clicked_code)
                zoom_offset = 5 if clicked_code in ["11", "61"] else 0
                fig_mm = metropolitan_map(province_name, True, clicked_code, zoom_offset)
                if fig_mm is None:
                    fig_m = province_map(province_name, True)
                    return fig_m, province_name
                return fig_mm, province_name
            else:
                fig_mr = region_map(value, True, clicked_code)
                return fig_mr, province_name
        
        # If Census Division is Clicked
        elif len(clicked_code) == 4:
            fig_msr = subregion_map(value, True, clicked_code)
            subregion_name = mapped_geo_code.query("Geo_Code == "+ f"{clicked_code}")['Geography'].tolist()[0]
            return fig_msr, subregion_name
            
        # If Census Metropolitan Area is Clicked
        elif len(clicked_code) == 5 and (view_mode is None or view_mode == "PT-CMA"):
            zoom_offset = 5 if view_mode == "PT-CMA" and int(clicked_code[:2]) in ["11", "61"] else 0
            fig_msr = metropolitan_map(value, True, clicked_code, zoom_offset)
            region_name = df_cma_list.loc[df_cma_list['Geo_Code'] == clicked_code, 'Geography'].tolist()[0]
            # region_name = df_cma_list.query("Geo_Code == "+ f"{str(clicked_code)}")['Geography'].tolist()[0]
            return fig_msr, region_name
        
        # If Census SubDivision is Clicked
        elif len(clicked_code) > 5 and (view_mode is None or view_mode == "PT-CD-CSD"):
            fig_msr = subregion_map(value, True, clicked_code)
            subregion_name = mapped_geo_code.query("Geo_Code == "+ f"{clicked_code}")['Geography'].tolist()[0]
            return fig_msr, subregion_name
        
    # Default Map View
    fig_m = province_map(value, True)
    return fig_m, default_value

