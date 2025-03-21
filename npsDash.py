import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import dash
from dash import Dash, html, dash_table, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import json
import logging
import plotly.io as pio

logging.basicConfig(level=logging.DEBUG)

#####################  GLOBALS   #############################################
MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiY290Y2FzZWsiLCJhIjoiY204aGc4bTI5MDFtazJzcTAxZmp4em5nNCJ9.b7JU5FUF9tkZ8dar7jQU0w'

ZOOM_LEVELS = {
    (60, 90): 6,  # High latitudes, very zoomed out
    (30, 60): 8,  # Medium latitudes, moderate zoom
    (0, 30): 10}

PATH = 'data/'

#####################  TABLES  ###########################################
info = pd.read_csv(PATH + 'park_info.csv')
features = pd.read_csv(PATH + 'npFeatures.csv')
monthly = pd.read_csv(PATH + 'monthly_visits.csv')
annual = pd.read_csv(PATH + 'annual_visits.csv')
scatter_data = pd.read_csv(PATH + 'park_scatter.csv')

##################### chart styles/input set up #################################

px.set_mapbox_access_token(MAPBOX_ACCESS_TOKEN)

pio.templates["dark_theme"] = go.layout.Template(
    layout=go.Layout(
        plot_bgcolor="#4C2B36",  
        paper_bgcolor="#4C2B36",  
        font=dict(color="white"),
        xaxis=dict(showgrid=False),  # No grid for x-axis
        yaxis=dict(
            showgrid=True,  # Enable y-axis grid
            gridcolor="lightgrey",  # Light grey grid lines
            gridwidth=1,  # Thin lines
            griddash="dot"  # Dashed style
        )  
    )
)

pio.templates.default = "dark_theme"

##set uo slider # Convert 'Year Established' to numeric, handling errors
info['Year Established'] = pd.to_numeric(info['Year Established'], errors='coerce')

# Define min and max years for the slider
min_year = int(info['Year Established'].min())
max_year = int(info['Year Established'].max())

#selectors for scatter plot
# Define the choices for dropdowns
choices = ["Size (Acres)", "Economic Output (USD)", "Miles of hiking trails", "Campgrounds"]

#####################  MAP   #############################################
# Load GeoJSON file

parks_poly = gpd.read_file(PATH + 'cleaned_spatial/parks_poly.geojson')

# Convert GeoDataFrame to JSON format
parks_geojson = json.loads(parks_poly.to_json())

# Create a Plotly figure
fig = px.choropleth_mapbox(
    parks_poly,
    geojson=parks_geojson,
    locations=parks_poly.index,
    color_discrete_sequence=["#D17A22"],
    # color_discrete_sequence=["#004346"],  # Solid color #CHANGE TO ECONOMIC OUTPUT, MAY REQUIRE JOIN ALSO REQUIRES LEGEND
    hover_name=parks_poly["PARKNAME"]
)



fig.update_traces(hovertemplate="<b>%{customdata}</b><extra></extra>", 
    customdata=parks_poly["PARKNAME"],
    # mapbox_access_token=MAPBOX_ACCESS_TOKEN,
    marker_opacity=0.6,  # Adjust transparency 
    marker_line_width=2,  
    marker_line_color="#09BC8A"
    )


fig.update_layout(
    # mapbox_style="carto-positron",
    # mapbox_style="carto-darkmatter",
    mapbox_style="satellite-streets",
    # mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
    mapbox_zoom=2,
    mapbox_center={"lat": parks_poly.geometry.centroid.y.mean(), 
                   "lon": parks_poly.geometry.centroid.x.mean()},
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    # height=600, width=800 #play with this in full app
)
fig.update_layout(
    map_style="white-bg",
    map_layers=[
        {
            "below": 'traces',
            "sourcetype": "raster",
            "sourceattribution": "United States Geological Survey",
            "source": [
                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
            ]
        }
      ])



#####################  DASH APP   #############################################
# Dash App
app = dash.Dash(__name__)


############## layout


app.layout = dbc.Container([

    # ROW for site header
    dbc.Row([html.H2("National Parks of the United States", id="bannerText", style={"textAlign": "center"})], id="siteBanner"),

    # text content
     dbc.Row([html.P("The National Parks Service was established in the summer of 1916 by President Woodrow Wilson.  Every month these parks welcome millions of visitors (even in the winter!) to hike, camp, sight-see, recreate, and enjoy nature.  Wild spaces like these have long been at risk, which is why they were designated for protection in the first place.  Now, more than ever, our parks--and planet--are vulnerable to the whims of corporate and political power holders.  Information is power, and it is my hope that exploratory tools such as this dashboard can serve to garner appreciation and protection for these beautiful lands.", id="overviewText")], id="overviewHolder"),

    # ROW for map/drop down
    dbc.Row([

        #COL for title/map
        dbc.Col([
            #title
            dbc.Row([
                html.H3("Click to select a park on the map (or use the dropdown)", id="map-title", style={"textAlign": "center"})
            ], id="mapTitle"),
            #map
            dbc.Row([
                dcc.Graph(
                    id="map",
                    figure=fig,
                    config={"scrollZoom": True}  # Enable scroll zoom
                )], id='parkMap',
                style={
                    "border-radius": "20px",  # Rounded corners
                    "overflow": "hidden",  # Ensures the corners stay rounded
                    "box-shadow": "2px 2px 10px rgba(0,0,0,0.2)" 
            })
        ], id='mapCol'),

        #COL for drop down, park stats
        dbc.Col([
            #title
            dbc.Row([
                html.H3("Park info", id="map-selector-title", style={"textAlign": "center"})
            ], id="mapSelectorTitle"),
            #ROW for drop down
            dbc.Row([
                dcc.Dropdown(
                    id="park-dropdown",
                    options=[
                        {"label": name, "value": name} for name in sorted(parks_poly["PARKNAME"])] + [{"label": "All Parks", "value": "All Parks"}
                    ],
                    placeholder="Select a Park", 
                    style={
                        "backgroundColor": "#004346",  #  background
                        # "color": "#D17A22",  #  text
                        "border": "1px solid #4C2B36",  #  border
                    }
                )
            ], id='parkDropdownHolder'),
            # ROW for stat divs
            dbc.Row([
                # COL for facts
                dbc.Col(html.Div(id="park-stats")),
                # COL for activities
                dbc.Col(html.Div(id="park-activities"))
            ], justify="start", align="center"),
                
        ], id='mapSelectCol')
    ], id='mapAndFacts'),

    # row for next fig
    dbc.Row([
        dbc.Col([
                # ADD MONTHLY CHART HERE
                dcc.Graph(id="month-chart")
            ], id='monthlyHolder',
            style={
                "border-radius": "20px",  
                "overflow": "hidden",  
                "box-shadow": "2px 2px 10px rgba(0,0,0,0.2)"  
            }),

        dbc.Col([
                # ADD ANNUAL CHART HERE
                dcc.Graph(id="year-chart")
            ], id='annualHolder',
            style={
                    "border-radius": "20px", 
                    "overflow": "hidden",  
                    "box-shadow": "2px 2px 10px rgba(0,0,0,0.2)"  
            })
    ], id='attendanceCharts'),
    html.Br(),
    # ROW last?
    dbc.Row([

        dbc.Col([
        # Radio buttons to aggregate by Region, State, or None
            html.Label("Aggregate By:"),
            dcc.RadioItems(
                id="aggregate-radio",
                options=[
                    {"label": "Region", "value": "Region"},
                    {"label": "State", "value": "State"},
                    {"label": "None", "value": "None"}
                ],
                value="None",  # Default to no aggregation
                inline=True
            ),
            
            # Dropdowns for y-axis, color, and size
            html.Br(),
            html.Label("Y-Axis:"),
            dcc.Dropdown(
                id="y-dropdown",
                options=[{"label": col, "value": col} for col in choices],
                value="Size (Acres)",  # Default value
                style={
                        "backgroundColor": "#004346",  #  background
                        # "color": "#D17A22",  #  text
                        "border": "1px solid #4C2B36",  #  border
                    }
            ),
            html.Br(),
            html.Label("Color:"),
            dcc.Dropdown(
                id="color-dropdown",
                options=[{"label": col, "value": col} for col in choices],
                value="Economic Output (USD)",  # Default value
                style={
                        "backgroundColor": "#004346", 
                        # "color": "#D17A22",  
                        "border": "1px solid #4C2B36",  
                    }
            ),
            html.Br(),
            html.Label("Size:"),
            dcc.Dropdown(
                id="size-dropdown",
                options=[{"label": col, "value": col} for col in choices],
                value="Miles of hiking trails" , # Default value
                style={
                        "backgroundColor": "#004346",  
                        # "color": "#D17A22", 
                        "border": "1px solid #4C2B36", 
                    }
            ),

        ], id='scatterSelectColumn',),
        dbc.Col([
            dcc.Graph(id="scatter-plot")
        ], id='scatterColumn',
        style={
                    "border-radius": "20px",  
                    "overflow": "hidden",  
                    "box-shadow": "2px 2px 10px rgba(0,0,0,0.2)"  
            }),
        dbc.Col([
            dcc.Graph(id="state-acres-chart"),
            dcc.Slider(
                    id="year-slider",
                    min=min_year,
                    max=max_year,
                    value=max_year,  # Default value
                    marks={year: str(year) for year in range(min_year, max_year + 1, 10)},
                    step=1
                )
        ], id='sizeChartColumn',
        style={
                    "border-radius": "20px",  
                    "overflow": "hidden",  
                    "box-shadow": "2px 2px 10px rgba(0,0,0,0.2)"  
            })
    ], id='sizeAndScatterRow'),

], id='parksDashContainer')


@app.callback(
    [
        Output("map", "figure"),
        Output("map-title", "children"),
        Output("park-stats", "children"),  # Stats as a list
        Output("park-activities", "children"),  # Activities as a sentence
        Output("park-dropdown", "value"),
        Output("map", "clickData"), 
        Output("month-chart", "figure"),
        Output("year-chart", "figure"),
    ],
    [
        Input("map", "clickData"), 
        Input("park-dropdown", "value"),
    ],
    [
        State("map", "clickData")  # Adding the State to manage clickData
        # StateOutput("park-dropdown", "value")
    ]
)



#####################  FUNCTIONS  #############################################
def zoom_to_polygon(clickData, park_name, current_clickData):
    
    if park_name:
        clickData = None
    #************ initial load case
    if clickData is None and park_name is None:
        clicked_code = 'ALLP'
        park_name = 'All Parks'
        logging.debug("No click data or dropdown selection.")

        # recenter map
        default_zoom = 2
        default_center = {
            "lat": parks_poly.geometry.centroid.y.mean(),
            "lon": parks_poly.geometry.centroid.x.mean()
        }

        # Reset figure with new zoom and center
        fig.update_layout(
            mapbox_zoom=default_zoom,
            mapbox_center=default_center
        )


        activity_list_display = 'Select a park for feature details.'
        # Sum numerical columns across all parks
        summed_info = info[['Size (Acres)', 'Economic Output (USD)', 'Miles of hiking trails', 'Campgrounds']].sum()

        # Convert to a dictionary with formatted values
        row_data = summed_info.to_dict()
        park_stats = [f"{key}: {value:,.0f}" for key, value in row_data.items()]  # Format numbers

        # Display as a list
        park_stats_display = [
            html.P("The 63 National Parks are responsible for:"),  # Intro text
            html.Ul([html.Li(stat) for stat in park_stats])  # List of stats
        ]

        # all parks, monthly attendence
        month_fig = px.bar(
        monthly[monthly['Year'] == 2024], 
        x="Month", 
        y="RecreationVisits", 
        color="ParkName", 
        labels={"RecreationVisits": "Number of Visits", "Month": "Month"}, 
        title=f"Monthly Park Attendance in 2024 for {park_name}",
        color_discrete_sequence=["#004346"]
        )
        # month_fig.update_traces(marker=dict(line=dict(color="#09BC8A", width=2)))
        month_fig.update_layout(showlegend=False)

        #all parks, annual attendance
        park_data = annual[annual["code"] == clicked_code]

        # Melt the data so that the years are in a single column
        visits_data = park_data.melt(id_vars=["park"], 
                                     value_vars=[str(year) for year in range(2005, 2025)],
                                     var_name="Year", value_name="Visits")

        # Create line chart
        annual_fig = px.line(visits_data, x="Year", y="Visits", title=f"Annual Visits for {park_name}",
                  labels={"Visits": "Number of Visits", "Year": "Year"})
        annual_fig.update_traces(line=dict(color="#D17A22"))

        temp_title = 'Click to select a park on the map (or use the dropdown)'

        return fig, temp_title, park_stats_display, activity_list_display, None, None, month_fig, annual_fig
    #************************** end initial load case

    # Handle click or dropdown select
    if clickData:
        logging.debug('using map click')
        clicked_index = clickData["points"][0]["location"]
        clicked_geom = parks_poly.loc[clicked_index, "geometry"]
        clicked_code = parks_poly.loc[clicked_index, "UNIT_CODE"]
        logging.debug(f"park code: {clicked_code}")
        bounds = clicked_geom.bounds
        new_center = {"lat": (bounds[1] + bounds[3]) / 2, "lon": (bounds[0] + bounds[2]) / 2}
        park_name = parks_poly.loc[clicked_index, "UNIT_NAME"]
    elif park_name:
        # Handle park selection from dropdown
        logging.debug('using drop down')
        clicked_index = parks_poly[parks_poly["PARKNAME"] == park_name].index[0]
        clicked_geom = parks_poly.loc[clicked_index, "geometry"]
        clicked_code = parks_poly.loc[clicked_index, "UNIT_CODE"]
        logging.debug(f"park code: {clicked_code}")
        bounds = clicked_geom.bounds
        new_center = {"lat": (bounds[1] + bounds[3]) / 2, "lon": (bounds[0] + bounds[2]) / 2}

    logging.debug(f"Park Name: {park_name}")

    #features list
    filtered_features = features[features['code'] == clicked_code]
    activity_list = filtered_features['Feature Name'].tolist()
    if len(activity_list) > 1:
        activity_sentence = ", ".join(activity_list[:-1]) + f", and {activity_list[-1]}"
    else:
        activity_sentence = activity_list[0] if activity_list else "No activities available"



    activity_list_display = [ html.P(f"{park_name} features:"),
                                html.P(activity_sentence)]

    #info list
    filtered_info = info[info['code'] == clicked_code]
    this_info = filtered_info[['Established', 'State', 'Size (Acres)', 'Economic Output (USD)', 'Miles of hiking trails', 'Campgrounds']]
    row_data = this_info.iloc[0].to_dict()
    # Create a list of formatted key-value pairs
    park_stats = [f"{key}: {value}" for key, value in row_data.items()]
    park_stats_display = html.Ul([html.Li(stat) for stat in park_stats])





    # Compute zoom level (adjust based on polygon size)
    lat_range = bounds[3] - bounds[1]
    lon_range = bounds[2] - bounds[0]
    max_range = max(lat_range, lon_range)
    #zoom_level = min(max(10 - (lat_range + lon_range) * 20, 3), 12)  # Adjust zoom dynamically
    zoom_level = np.clip(12 - np.log2(max_range * 40), 5, 15)  # Adjust scaling factors if needed


    logging.debug(f"New center: {new_center}, Zoom level: {zoom_level}")



    # Update figure
    fig.update_layout(
        mapbox_center=new_center,
        mapbox_zoom=zoom_level,  # Adjust zoom level as needed
        # mapbox_bounds={"west": bounds[0], "east": bounds[2], "south": bounds[1], "north": bounds[3]}
    )
    fig.add_trace(
    px.choropleth_mapbox(
        parks_poly[parks_poly.index == clicked_index],  # Only the selected polygon
        geojson=parks_geojson,
        locations=parks_poly.index,
        color_discrete_sequence=["rgba(0, 0, 0, 0)"],  # Transparent fill
    ).data[0]
    )

    fig.update_traces(
        marker_line_width=4,  
        marker_line_color="#09BC8A",  # Ensure the outline is visible
        hovertemplate="<b>%{customdata}</b><extra></extra>", 
        customdata=parks_poly["PARKNAME"],
    )
    
    
    #******************* monthly attendance chart

    monthly_2024 = monthly[monthly['Year'] == 2024]
    if park_name != "All Parks":
        # Filter data based on the selected park
        data = monthly_2024[monthly_2024['code'] == clicked_code]
    else:
        data = monthly_2024  # If "All Parks" is selected, show data for all parks
    
    # Generate bar chart using Plotly Express
    month_fig = px.bar(
        data, 
        x="Month", 
        y="RecreationVisits", 
        color="ParkName", 
        labels={"RecreationVisits": "Number of Visits", "Month": "Month"}, 
        title=f"Monthly Park Attendance in 2024 for {park_name}",
        color_discrete_sequence=["#004346"]
    )
    # month_fig.update_traces(marker=dict(line=dict(color="#09BC8A", width=2)))
    month_fig.update_layout(showlegend=False)

    #******************* annual attendance chart
    # Filter the data for the selected park
    park_data = annual[annual["code"] == clicked_code]

    # Melt the data so that the years are in a single column
    visits_data = park_data.melt(id_vars=["park"], 
                                 value_vars=[str(year) for year in range(2005, 2025)],
                                 var_name="Year", value_name="Visits")

    # Create a Plotly line chart
    annual_fig = px.line(visits_data, x="Year", y="Visits", title=f"Annual Visits for {park_name}", labels={"Visits": "Number of Visits", "Year": "Year"})
    annual_fig.update_traces(line=dict(color="#D17A22"))


    return fig, f"{park_name}", park_stats_display, activity_list_display, None, None, month_fig, annual_fig



@app.callback(
    # Output("year-output", "children"),
    Output("state-acres-chart", "figure"),
    Input("year-slider", "value")
)
def update_year(selected_year):
    # f"Selected Year: {selected_year}"
    # return f"Selected Year: {selected_year}"

    logging.debug(f'selected year on load = {selected_year}')
    if selected_year is None:
        selected_year = max_year
        logging.debug(f'selected year on load = {selected_year}')
        
    # state acres chart
    filtered_df = info[info['Year Established'] <= selected_year]

    # Aggregate data by state
    state_acres = filtered_df.groupby("State")["Size (Acres)"].sum().reset_index()

    # Check if there's data available
    if state_acres.empty:
        state_acres_fig = px.bar(title=f"No Data Available for {selected_year}")

    # Create the bar chart
    state_acres_fig = px.bar(
        state_acres,
        x="State",
        y="Size (Acres)",
        title=f"National Park Acres by State {min_year} to {selected_year}",
        labels={"Size (Acres)": "Total Acres", "State": "State"},
        color_discrete_sequence=["#004346"]  # Green bars
    )
    state_acres_fig.update_traces(marker=dict(line=dict(color="#09BC8A", width=.5)))
    return state_acres_fig


@app.callback(
    Output("scatter-plot", "figure"),
    [
        Input("aggregate-radio", "value"),
        Input("y-dropdown", "value"),
        Input("color-dropdown", "value"),
        Input("size-dropdown", "value")
    ]
)
def update_scatter(aggregate_by, y_axis, color, size):
    # Copy the dataset to avoid modifying the original
    data = scatter_data.copy()
    hover_text = ''
    
    # Aggregate data if required
    if aggregate_by != "None":
        data = data.groupby(aggregate_by).sum().reset_index()
        x_axis_title = "Relative park age"  # Rename axis if aggregated
        show_x_ticks = False  # Hide tick labels if aggregated
    else:
        hover_text = ['name', "Region", "Economic Output (USD)"]
        x_axis_title = "Year Established"
        show_x_ticks = True  # Show tick labels if not aggregated
    
    if aggregate_by =='Region':
        hover_text = ["Region", "Economic Output (USD)"]
    elif aggregate_by == 'State':
        hover_text = ["State", "Economic Output (USD)"]
        
    
    
    # Create the scatter plot
    scatter_fig = px.scatter(
        data,
        x="Year Established",
        y=y_axis,
        color=color,
        size=size,
        hover_data=hover_text,  # Add any hover data you want
        # labels={"Year Established": "Year Established", y_axis: y_axis, color: color, size: size},
        title=f"Scatter Plot: {y_axis} vs Year Established",
        color_continuous_scale=px.colors.sequential.Viridis
    )

    if aggregate_by != "None":
        scatter_fig.update_layout(
        xaxis_title=x_axis_title,  # Keep the x-axis title
        xaxis_showticklabels=show_x_ticks  # Hide or show tick labels dynamically
        )
    
    return scatter_fig


############### MAIN ###########

if __name__ == '__main__':
    app.run(debug=True) #turn off debug when finished
