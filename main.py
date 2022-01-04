import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
from dash_html_components.P import P
from pkg_resources import yield_lines
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os

# Pour charger une fiche css externe en ligne
external_stylesheets = ['customCSS/newbrl.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Charger un css local  => dans le dossier assets
# app = dash.Dash(__name__)

# ----------  CHARGEMENT DES DONNEES -----------------------------------------------------------------
load_df = os.listdir("assets/CSV")
print(load_df)
df_debit = pd.read_csv(f"assets/CSV/DebitMsoulet.csv")
# print(list_df)

# ---- Graph débits groupes
new_df = df_debit.query("Sens =='Entrant'")
fig = px.line(new_df, x=new_df.evttime, y=new_df['Débit m3/h'], color="Groupes")
annotations = []
annotations.append(dict(text = f"Courbe des groupes ",xref='paper', yref='paper', x=0.0, y=1.05,
                              xanchor='left', yanchor='bottom',
                               showarrow = False))
fig.update_xaxes(rangeslider_visible=True)
fig.update_layout(annotations=annotations)

# ---- Graph débits réseau
df_cible2 = df_debit.query("Sens =='Sortant'")
# print(df_cible2.columns)
df_cible3 = df_cible2.set_index("evttime",drop=True)
df_cible3.drop(columns='Unnamed: 0', inplace=True)
df_cible3.index = pd.to_datetime(df_cible3.index)
# print(df_cible3.columns)
# print(df_cible3.index[:5])
df_cible3 = df_cible3.resample('D').mean()

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df_cible2.evttime, y=df_cible2['Débit m3/h'],
                        mode = "lines",
                        name = f"Débit sortant pas 5 min"))
fig2.add_trace(go.Scatter(x=df_cible3.index, y=df_cible3['Débit m3/h'],
                        mode = "lines",
                        name = f"Débit sortant moyen journalier"))

fig2.update_xaxes(rangeslider_visible=True)

# ---- Graph maxs
df_cible4 = df_debit.query("Groupes == '(GR8)' & Sens =='Entrant'")
df_cible4 = df_cible4.set_index("evttime")
df_cible4.index = pd.to_datetime(df_cible4.index)
df_cible4 = df_cible4.resample('D').max()
df_cible5 = df_debit.query("Groupes == '(GR9)' & Sens =='Entrant'")
df_cible5 = df_cible5.set_index("evttime")
df_cible5.index = pd.to_datetime(df_cible5.index)
df_cible5 = df_cible5.resample('D').max()
df_cible6 = df_debit.query("Groupes == '(GR6)' & Sens =='Entrant'")
df_cible6 = df_cible6.set_index("evttime")
df_cible6.index = pd.to_datetime(df_cible6.index)
df_cible6 = df_cible6.resample('D').max()
df_cible7 = df_debit.query("Groupes == '(GR7)' & Sens =='Entrant'")
df_cible7 = df_cible7.set_index("evttime")
df_cible7.index = pd.to_datetime(df_cible7.index)
df_cible7 = df_cible7.resample('D').max()

fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=df_cible4.index, y=df_cible4['Débit m3/h'],
                        mode = "lines",
                        name = f"Débit Max Journalier GR8"))
fig3.add_trace(go.Scatter(x=df_cible5.index, y=df_cible5['Débit m3/h'],
                        mode = "lines",
                        name = f"Débit Max Journalier GR9"))
fig3.add_trace(go.Scatter(x=df_cible6.index, y=df_cible6['Débit m3/h'],
                        mode = "lines",
                        name = f"Débit Max Journalier GR6"))
fig3.add_trace(go.Scatter(x=df_cible7.index, y=df_cible7['Débit m3/h'],
                        mode = "lines",
                        name = f"Débit Max Journalier GR7"))

fig3.update_xaxes(rangeslider_visible=True)


# Chargement des fonctions ---------------------------------------------------------------------
def display_df(df):
    print('Z')
    print(df.columns)

    df.drop(columns='Unnamed: 0', inplace=True)
    df.set_index('evttime')
    print('B')
    print(df.columns)
    return  html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), 10))
        ])
    ])


# -----------  LAYOUT ---------------------------------------------------------------------------------
app.layout = html.Div(children=[

    html.H4(children='Estimation des débits de Mas Soulet',className="Title"),


    dcc.Tabs([
        dcc.Tab( label = 'Débits groupes', children = [

            html.Div(children=[
                dcc.Graph(id='GraphGroup',
                figure = fig)
            ])

        ]
        ),
        dcc.Tab( label = 'Débits réseau', children = [

            html.Div(children=[
                dcc.Graph(id='GraphReseau',
                figure = fig2)
            ])

        ]
         ),
        dcc.Tab( label = 'Débits Maximums journaliers', children = [

            html.Div(children=[
                dcc.Graph(id='GraphMax',
                figure = fig3)
            ])

        ]
        ),
        dcc.Tab( label = 'Données brutes', children = [

            html.Div([
                html.H4(children='Table des débits'),
                display_df(df_debit)
                ])

        ]
        )
    ])

])

# ------------ CALLBACKS ------------------------------------------------------------------------------
# TAB 1
# Callback Graph1 ---------------------------------------------------------
@app.callback(
    Output(component_id='GraphGroup', component_property='figure'),
    Input(component_id='Choix_df', component_property='value'))
def update_figure(selected_df):
    # "selected_df" correspond à la value de la callback input
    new_df = df_debit.query("Groupes == '(GR8)' & Sens =='Entrant'")
    print(new_df.head(3))

    fig = px.histogram(new_df, 
    y="Labels", 
    x="Durée_en_heures", 
    color="Années", 
    barmode="group")

    fig.update_layout(transition_duration=500)

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)