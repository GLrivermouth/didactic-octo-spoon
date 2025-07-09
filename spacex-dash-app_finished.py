# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id= 'site-dropdown',options=[{'label':'All Sites','value':'ALL'},
                                                                          {'label':'CCAFS LC-40','value':'CCAFS LC-40'},
                                                                          {'label':'VAFB SLC-4E','value':'VAFB SLC-4E'},
                                                                          {'label':'KSC LC-39A','value':'KSC LC-39A'},
                                                                          {'label':'CCAFS SLC-40','value':'CCAFS SLC-40'}],
                                                                          value='ALL',
                                                                          placeholder='Select a Launch Site here',
                                                                          searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div([
                                    html.Div(dcc.Graph(id='proportion-success-pie-chart', style={'height':'300px','width': '90', 'display': 'inline-block'}),
                                            style={'display': 'inline-block', 'width': '100%'}),
                                    html.Div(dcc.Graph(id='success-pie-chart', style={'height':'300px','width': '90%', 'display': 'inline-block'}),
                                            style={'display': 'inline-block', 'width': '90%'})
                                ], style={'display': 'flex', 'justify-content': 'center'}),  
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0, max=10000, step=1000, 
                                marks={i: str(i) for i in range(0, 10001, 1000)},
                                value=[min_payload, max_payload]
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='proportion-success-pie-chart', component_property='figure'),
                Output(component_id='success-pie-chart', component_property='figure'),            
                Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        success_count_by_site = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size()
        proportion_success_fig = px.pie(values=success_count_by_site, names=success_count_by_site.index,
        title='Proportion of Successful Launches by Site'
        )

        success_count = filtered_df['class'].value_counts()
        success_fig = px.pie(values = success_count, names= success_count.index,
        title='Total Successful Launches for All Sites')
        return proportion_success_fig, success_fig
    else:
        specific_site = filtered_df[filtered_df['Launch Site'] == entered_site]
        success_count = specific_site['class'].value_counts()
        success_fig = px.pie(values = success_count, names= success_count.index,
        title=f'Success vs. Failed Launches for {entered_site}')
        empty_fig = px.pie(values=[0, 0], names=['Success', 'Fail'], title='No Data')

        return empty_fig, success_fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),            
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id="payload-slider", component_property="value")
)
def update_scatter_chart(entered_site, payload_range):
    # Filter the dataframe based on the selected site
    filtered_df = spacex_df
    if entered_site == 'ALL':
        plot_df = filtered_df
    else:
        plot_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Further filter the dataframe based on the payload range
    plot_df = plot_df[(plot_df['Payload Mass (kg)'] >= payload_range[0]) &
                      (plot_df['Payload Mass (kg)'] <= payload_range[1])]

    # Create the scatter plot
    scatter_fig = px.scatter(
        plot_df,
        x='Payload Mass (kg)',
        y='class',color='Booster Version Category',
        title=f'Success versus Payload Mass (kg) for {entered_site}' if entered_site != 'ALL' else 'Success versus Payload Mass (kg) for All Sites'
    )

    # Return the figure object for the scatter chart
    return scatter_fig

# Run the app
if __name__ == '__main__':
    app.run()