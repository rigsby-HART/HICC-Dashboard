# Importing Libraries
import pdb

import pandas as pd
import numpy as np
import warnings
import json, os
import geopandas as gpd
import fiona
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, ctx, callback
from sqlalchemy import create_engine

fiona.supported_drivers
warnings.filterwarnings("ignore")
current_dir = os.path.dirname(os.path.abspath(__file__))

# engine_new = create_engine('sqlite:///sources//new_hart.db')
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
# mapped_geo_code.to_csv(r"L:\Projects\22005 - Housing Needs Assessment\Processed\HART_2024\BC-HNA-Dashboard\sources\Archive\mapped_geo.csv")

df_geo_list = pd.read_sql_table('geocodes', engine_old.connect())
# pdb.set_trace()

df_region_list = pd.read_sql_table('regioncodes', engine_old.connect())

df_region_list.columns = df_geo_list.columns
df_province_list = pd.read_sql_table('provincecodes', engine_old.connect())

df_province_list.columns = df_geo_list.columns

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

default_value = 'Ottawa CV (CSD, ON)'  #'Canada'  #change this back to Canada when done testing!

# Plot icon colors

modebar_color = '#099DD7'
modebar_activecolor = '#044762'

# Setting orders of areas in dropdown

order = mapped_geo_code.copy()
order['Geo_Code'] = order['Geo_Code'].astype(str)
order = order.sort_values(by=['Province_Code', 'Region_Code', 'Geo_Code'])

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

    # Main Layout

    html.Div(
        children=[

            # Select Area Dropdowns
            html.Div(children=[

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
                className='dropdown-box-lgeo'
            ),

            # Area Scale Buttons
            html.Div(children=[

                html.Div(children=[
                    html.Button('View Census Subdivision (CSD)',
                                title='A provincially-legislated area at the municipal scale, or areas treated as municipal equivalents for statistical purposes (e.g. reserves, settlements and unorganized territories). Municipal status is defined by laws in effect in each province and territory in Canada.',
                                id='to-geography-1', n_clicks=0, className='region-button-lgeo'),
                ], className='region-button-box-lgeo'
                ),
                html.Div(children=[
                    html.Button('View Census Division (CD)',
                                title='A provincially legislated area like counties, regional districts or equivalent areas. Census divisions are intermediate geographic areas between the province/territory level and the municipality (census subdivision).',
                                id='to-region-1', n_clicks=0, className='region-button-lgeo'),
                ], className='region-button-box-lgeo'
                ),
                html.Div(children=[
                    html.Button('View Province / Territory', 
                                title= "'Province' and 'territory' refer to the major political units of Canada. Canada is divided into 10 provinces and 3 territories.",
                                id='to-province-1', n_clicks=0, className = 'region-button-lgeo'),
                ], className='region-button-box-lgeo'
                ),

            ],
                className='scale-button-box-lgeo'
            ),

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
    Input('all-geo-dropdown', 'value'),
    Input('comparison-geo-dropdown', 'value'),
    Input('all-geo-dropdown-parent', 'n_clicks'),
    Input('comparison-geo-dropdown-parent', 'n_clicks'),
    Input('to-geography-1', 'n_clicks'),
    Input('to-region-1', 'n_clicks'),
    Input('to-province-1', 'n_clicks')
)
def store_geo(geo, geo_c, btn1, btn2, btn3, btn4, btn5):
    id_name = str(ctx.triggered_id)

    return geo, geo_c, id_name


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
        clicked_region_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Region_Code'].tolist()[0]
        clicked_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Geo_Code'].tolist()[0]
        clicked_code = str(clicked_code)
        # print(clicked_code)
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


# Callback logic for the map picker

@callback(
    Output('canada_map', 'figure'),
    Output('all-geo-dropdown', 'value'),
    [Input('canada_map', 'clickData')],
    Input('reset-map', 'n_clicks'),
    Input('all-geo-dropdown', 'value'),
    Input('all-geo-dropdown-parent', 'n_clicks'),
    Input('to-geography-1', 'n_clicks'),
    Input('to-region-1', 'n_clicks'),
    Input('to-province-1', 'n_clicks')
)
def update_map(clickData, btn1, value, btn2, btn3, btn4, btn5):
    # If no area is selected, then map will show Canada Map

    if value == None:
        value = default_value

    clicked_code = mapped_geo_code.loc[mapped_geo_code['Geography'] == value, :]['Geo_Code'].tolist()[0]
    clicked_code = str(clicked_code)

    # When users click 'View Province' button or select a province on dropbox menu

    if (
            len(clicked_code) == 2 and 'all-geo-dropdown-parent' == ctx.triggered_id) or "to-province-1" == ctx.triggered_id:
        fig_m = province_map(value, False)

        return fig_m, value

    # When users click 'View Census Division' button or select a Census Division on dropbox menu

    if (len(clicked_code) == 4 and 'all-geo-dropdown-parent' == ctx.triggered_id) or "to-region-1" == ctx.triggered_id:

        # When users click 'View Census Division' button after selecting Province on dropbox menu
        # -> Show map for Province

        if len(clicked_code) == 2:
            fig_m = province_map(value, False)
            # fig_m = region_map(value, False, 'N')
            return fig_m, value

        # When users select Census Division on dropbox menu
        # or When users click 'View Census Division' button after selecting Census Division on dropbox menu
        # -> Show map for Census Division

        fig_mr = region_map(value, False, 'N')

        return fig_mr, value

    # When users click 'View Census SubDivision' button or select a Census SubDivision on dropbox menu

    if (
            len(clicked_code) > 4 and 'all-geo-dropdown-parent' == ctx.triggered_id) or "to-geography-1" == ctx.triggered_id:

        # When users click 'View Census SubDivision' button after selecting Census Division on dropbox menu
        # -> Show map for Census Division

        if len(clicked_code) == 4:

            fig_mr = region_map(value, False, 'N')

            return fig_mr, value

        # When users click 'View Census SubDivision' button after selecting Province on dropbox menu
        # -> Show map for Province

        elif len(clicked_code) == 2:

            fig_m = province_map(value, False)
            # fig_m = region_map(value, False, 'N')
            return fig_m, value

        # When users select Census SubDivision on dropbox menu
        # or when users click 'View Census SubDivision' button after selecting Census SubDivision on dropbox menu
        # -> Show map for Census SubDivision

        elif len(clicked_code) == 7:

            fig_msr = subregion_map(value, False, 'N')

            return fig_msr, value

    # When Reset-Map button is clicked

    if "reset-map" == ctx.triggered_id:
        fig_m = province_map(value, True)
        # fig_m = region_map(value, True, str(province_code))

        return fig_m, default_value

    # When users clicked province on the map

    if type(clickData) == dict:

        clicked_code = str(clickData['points'][0]['location'])

        if len(clicked_code) == 2:

            fig_mr = region_map(value, True, clicked_code)

            region_name = df_province_list.query("Geo_Code == " + f"{clicked_code}")['Geography'].tolist()[0]

            return fig_mr, region_name

        # When users clicked region on the regional map after clicking province
        # -> show subregion map

        elif len(clicked_code) == 4:

            fig_msr = subregion_map(value, True, clicked_code)

            region_name = df_region_list.query("Geo_Code == " + f"{clicked_code}")['Geography'].tolist()[0]

            return fig_msr, region_name

        # When users clicked subregion on the regional map after clicking province
        # -> remains subregion map and send subregion code to area selection dropdown

        elif len(clicked_code) > 4:

            fig_msr = subregion_map(value, False, clicked_code)

            subregion_name = mapped_geo_code.query("Geo_Code == " + f"{clicked_code}")['Geography'].tolist()[0]

            return fig_msr, subregion_name

    # default map (show provinces) before clicking anything on the map

    else:

        fig_m = province_map(value, True)
        # fig_m = region_map(value, True, str(province_code))

        return fig_m, default_value

