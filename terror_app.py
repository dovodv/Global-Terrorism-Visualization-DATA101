from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc

#Import data
df = pd.read_csv('globalterrorismdb_0718dist.csv', encoding="ISO-8859-1", low_memory=False)
df['count'] = 1

#Mapbox Token
px.set_mapbox_access_token(open(".mapbox_token").read())

#Var Assignment
value_one = 'nkill'
value_two = 'count'
grp = 'gname'
region = 'Middle East & North Africa'

#Data Transformation
df_region = df.loc[df['region_txt'] == region].reset_index(drop=True)
df_map = df.head(1000)

df_hor_bar = df_region.groupby(['country_txt'])[[value_one, value_two]].sum().reset_index()
df_hor_bar = df_hor_bar.sort_values(by=value_one, ascending=True).tail(5)

df_pie = pd.DataFrame(df_region.groupby(grp)[value_one].sum()).reset_index()
df_pie = df_pie.sort_values(by=value_one, ascending=False).head(9)

df_time = pd.DataFrame(df_region.groupby([grp, 'iyear'], as_index=False)[value_one].sum())
df_time_sorted = df_time.sort_values(by=value_one, ascending=False)
top_five_kills = df_time_sorted[grp].unique()[:5].tolist()
df_time = df_time.loc[(df_time[grp] == top_five_kills[0]) | 
                      (df_time[grp] == top_five_kills[1]) | 
                      (df_time[grp] == top_five_kills[2]) | 
                      (df_time[grp] == top_five_kills[3]) | 
                      (df_time[grp] == top_five_kills[4])]

df_stacked = pd.DataFrame(df_region.groupby(['country_txt', grp])[value_one].sum())
df_stacked = df_stacked.sort_values(by=[value_one])
df_stacked = df_stacked.reset_index()

top_group = df_pie[grp].unique().tolist()
top_group.append('country_txt')
df_stacked_pivot = pd.pivot_table(data=df_stacked, 
                                  index='country_txt', 
                                  columns=grp, 
                                  values=value_one)
df_stacked_pivot['total'] = df_stacked_pivot.sum(axis=1)
df_stacked_pivot = df_stacked_pivot.sort_values(by=['total'], ascending=False).head(10)
df_stacked_pivot = df_stacked_pivot.reset_index()
df_stacked_pivot = df_stacked_pivot[top_group]

#Plotly Express Figures
fig_map = px.scatter_mapbox(df_map,
                        lat='latitude',
                        lon='longitude',
                        hover_name="city",
                        color=grp,
                        zoom=1)
fig_map.update_layout(showlegend=False)

fig_bar = px.bar(df_hor_bar, x=[value_one, value_two], y='country_txt', orientation='h', barmode='group')
fig_bar.update_layout(
    width=400,
    height=350,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=3
    ),
    legend=dict(
        yanchor="bottom",
        y=0.01,
        xanchor="right",
        x=0.99
    ),
    font=dict(
            size=9,
    )
)

fig_pie = px.pie(df_pie, values=value_one, names=grp)
fig_pie.update_layout(showlegend=False,
    width=250,
    height=250,
    margin=dict(
        l=50,
        r=0,
        b=0,
        t=0,
        pad=3
    ),
    legend=dict(
        yanchor="bottom",
        y=0.01,
        xanchor="right",
        x=0.99
    ),
    font=dict(
            size=9,
    )
)


fig_line = px.area(df_time, x='iyear', y=value_one, color=grp)
fig_line.update_layout(
    width=400,
    height=350,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=3
    ),
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ),
    font=dict(
            size=9,
    )
)

fig_stacked = px.bar(df_stacked_pivot.reset_index(), x='country_txt', y=df_stacked_pivot.columns)
fig_stacked.update_layout(
    width=400,
    height=350,
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0,
        pad=3
    ),
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
    ),
    font=dict(
            size=9,
    )
)

# Initialize Dash application
app = Dash(__name__, 
           external_stylesheets=[dbc.themes.BOOTSTRAP])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="#"),
                dbc.DropdownMenuItem("Page 3", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="Global Terrorism Visualization",
    brand_href="#",
    color="dark",
    dark=True,
)

# App layout
app.layout = html.Div(children=[
    navbar,
    dbc.Container([
        dbc.Col(children=[
            dcc.Graph(id="scatter-map", figure=fig_map)
        ]),
        dbc.Row(children=[
             dbc.Col(children=[
                
            ], width=4),
            dbc.Col(children=[
                dcc.Graph(id="bar-chart", figure=fig_bar)
            ], width=4),
            dbc.Col(children=[
                dcc.Graph(id="pie-chart", figure=fig_pie)
            ], width=4),
        ]),
        dbc.Row(children=[
            dbc.Col(children=[
                dcc.Graph(id="line-chart", figure=fig_line)
            ], width=4),
            dbc.Col(children=[
                dcc.Graph(id="stacked-chart", figure=fig_stacked)
            ], width=4),
            # dbc.Col(children=[
                
            # ], width=4),
        ])
    ])
    
    
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)