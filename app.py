import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import os


# Create a dash application
app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True #prevent error message
#reading data
airline =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv', 
                            encoding = "ISO-8859-1",dtype={'Div1Airport': str, 'Div1TailNum': str,'Div2Airport': str, 'Div2TailNum': str})


years = [i for i in range(2005, 2021, 1)]

def compute_data_choice_1(df):
    bar = df.groupby(['Month','CancellationCode'])['Flights'].sum().reset_index()
    line = df.groupby(['Month','Reporting_Airline'])['AirTime'].mean().reset_index()
    divair = df[df['DivAirportLandings'] != 0.0]
    mapita = df.groupby(['OriginState'])['Flights'].sum().reset_index()
    group = df.groupby(['DestState', 'Reporting_Airline'])['Flights'].sum().reset_index()
    return bar, line, divair, mapita, group



def compute_data_choice_2(df):
    # Compute delay averages
    car = df.groupby(['Month','Reporting_Airline'])['CarrierDelay'].mean().reset_index()
    weather = df.groupby(['Month','Reporting_Airline'])['WeatherDelay'].mean().reset_index()
    nasde = df.groupby(['Month','Reporting_Airline'])['NASDelay'].mean().reset_index()
    sec = df.groupby(['Month','Reporting_Airline'])['SecurityDelay'].mean().reset_index()
    late = df.groupby(['Month','Reporting_Airline'])['LateAircraftDelay'].mean().reset_index()
    return car, weather, nasde, sec, late

def get_asset_url(path):
                return os.path.join("assets", path)


# Application layout
app.layout = html.Div(children=[ 
                                html.Img( src =  app.get_asset_url("https://pregem.com/wp-content/uploads/2017/03/airline-banner-V2.png"),),
                                html.H1('US Domestic Airline Flights Performance',
                                        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
                                html.Div([
                                    html.Div([
                                        html.Div(
                                            [
                                            html.H2('Report Type:', style={'margin-right': '2em'}),
                                            ]
                                        ),
                                        dcc.Dropdown(id='input-type', 
                                                        options=[
                                                                {'label': 'Yearly Airline Performance Report', 'value': 'OPT1'},
                                                                {'label': 'Yearly Airline Delay Report', 'value': 'OPT2'}
                                                                ],
                                                        placeholder='Select a report type',
                                                        style={'text-align-last': 'center', 'font-size': '20px', 'width': '80%', 'padding': '3px'})
                                    ], style={'display':'flex'}),
                                    
                                   html.Div([
                                        html.Div(
                                            [
                                            html.H2('Choose Year:', style={'margin-right': '2em'})
                                            ]
                                        ),
                                        dcc.Dropdown(id='input-year', 
                                                     options=[{'label': i, 'value': i} for i in years],
                                                     placeholder="Select a year",
                                                     style={'width':'80%', 'padding':'3px', 'font-size': '20px', 'text-align-last' : 'center'}),
                                            ], style={'display': 'flex'}),  
                                          ]),
                                
                                html.Div([ ], id='plot1'),
    
                                html.Div([
                                        html.Div([ ], id='plot2'),
                                        html.Div([ ], id='plot3')
                                ], style={'display': 'flex'}),
                                  
                                html.Div([
                                        html.Div([ ], id='plot4'),
                                        html.Div([ ], id='plot5')
                                ], style={'display': 'flex'})
                                ])

@app.callback( [Output(component_id='plot1', component_property='children'),
                Output(component_id='plot2', component_property='children'),
                Output(component_id='plot3', component_property='children'),
                Output(component_id='plot4', component_property='children'),
                Output(component_id='plot5', component_property='children')],
               [Input(component_id='input-type', component_property='value'),
                Input(component_id='input-year', component_property='value')],
               [State("plot1", 'children'), State("plot2", "children"),
                State("plot3", "children"), State("plot4", "children"),
                State("plot5", "children")
               ])


def get_graph(chart, year, children1, children2, c3, c4, c5):
        df =  airline[airline['Year']==int(year)]
        if chart == 'OPT1':
            bar, line, divair, mapita, group = compute_data_choice_1(df)     
            bar_fig = px.bar(bar, x='Month', y='Flights', color='CancellationCode', title='Monthly Flight Cancellation')
            line_fig = px.line(line, x='Month', y='AirTime', color='Reporting_Airline', title='Average monthly flight time (minutes) by airline')     
            pie_fig = px.pie(divair, values='Flights', names='Reporting_Airline', title='% of flights by reporting airline')
            map_fig = px.choropleth(mapita,
                    locations='OriginState', 
                    color='Flights',  
                    hover_data=['OriginState', 'Flights'], 
                    locationmode = 'USA-states', 
                    color_continuous_scale='GnBu',
                    range_color=[0, mapita['Flights'].max()]) 
            map_fig.update_layout(
                    title_text = 'Number of flights from origin state', 
                    geo_scope='usa') 

            tree_fig = px.treemap(group, path=['DestState', 'Reporting_Airline'], 
                                values='Flights',
                                color='Flights',
                                color_continuous_scale='RdBu',
                                title='Flight count by airline to destination state'
                                )
            
            
            return [dcc.Graph(figure=tree_fig), 
                    dcc.Graph(figure=pie_fig),
                    dcc.Graph(figure=map_fig),
                    dcc.Graph(figure=bar_fig),
                    dcc.Graph(figure=line_fig)
                   ]
        else:

            car, weather, nasde, sec, late = compute_data_choice_2(df)
            
            #graph
            carrier_fig = px.line(car, x='Month', y='CarrierDelay', color='Reporting_Airline', title='Average carrrier delay time (minutes) by airline')
            weather_fig = px.line(weather, x='Month', y='WeatherDelay', color='Reporting_Airline', title='Average weather delay time (minutes) by airline')
            nas_fig = px.line(nasde, x='Month', y='NASDelay', color='Reporting_Airline', title='Average NAS delay time (minutes) by airline')
            sec_fig = px.line(sec, x='Month', y='SecurityDelay', color='Reporting_Airline', title='Average security delay time (minutes) by airline')
            late_fig = px.line(late, x='Month', y='LateAircraftDelay', color='Reporting_Airline', title='Average late aircraft delay time (minutes) by airline')
            
            return[dcc.Graph(figure=carrier_fig), 
                   dcc.Graph(figure=weather_fig), 
                   dcc.Graph(figure=nas_fig), 
                   dcc.Graph(figure=sec_fig), 
                   dcc.Graph(figure=late_fig)]


# Run the app
if __name__ == '__main__':
    app.run_server()