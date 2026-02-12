# LIBRERIAS
from dash import Dash, html, dcc, callback, Output, Input


# APP DASH
app = Dash(__name__)


# LAYOUT
app.layout = [
    html.Div([
        dcc.Store(id='store_monitoreo', storage_type='session'),
        dcc.Store(id='store_automatico', storage_type='session'),
        dcc.Store(id='store_manual', storage_type='session'),
        dcc.Store(id='store_alarmas', storage_type='session'),
        dcc.Tabs(id='system-tabs',value='monitoring', children=[
            dcc.Tab(label='Monitoreo', value='monitoring'),
            dcc.Tab(label='Automático', value='automatic'),
            dcc.Tab(label='Manual', value='manual'),
            dcc.Tab(label='Alarmas/Historial', value='alarms_history'),
        ]
    ),
    html.Div(id='tab_content', className='render_tab')
    ], className='app-container')
]


# MONITOREO LAYOUT
def monitoring_layout():
    return html.Div([
        html.Div('Estado general', className='card estado'),
        html.Div('Datos del proceso', className='card datos'),
        html.Div('Temperatura y velocidad del tornillo', className='card temperatura'),
        html.Div('Filamento', className='card filamento'),
        html.Div('Diametro del filamento', className='card diametro'),
        html.Div('Alertas recientes', className='card alertas'),
    ], className='monitoring-grid')


# MODO AUTOMATICO LAYOUT
def automatic_layout():
    return html.Div([
        html.Div('Datos del proceso', className='card datos_automatica'),
        html.Div('Diametro del filamento', className='card diametro_automatica'),
        html.Div('Temperatura y velocidad del tornillo', className='card temperatura_automatica'),
        html.Div('Filamento', className='card filamento_automatica'),
    ], className='automatic-grid')


# MODO MANUAL LAYOUT
def manual_layout():
    return html.Div([
        html.Div('Datos manual', className='card datos_manual'),
        html.Div([
            html.Label('Temperatura extrusora (°C)'),
            html.Div(
                dcc.Slider(
                    min=150,
                    max=300,
                    step=1,
                    value=200,
                    marks={
                        150: '150',
                        180: '180',
                        210: '210',
                        230: '230',
                        250: '250',
                        270: '270',
                        300: '300',
                        165: {'label': 'LDPE', 'style': {'color': '#3498db'}},
                        195: {'label': 'PLA/HDPE', 'style': {'color': '#2ecc71'}},
                        220: {'label': 'PP', 'style': {'color': '#f1c40f'}},
                        240: {'label': 'ABS/PETG', 'style': {'color': '#e67e22'}},
                        260: {'label': 'Nylon', 'style': {'color': '#e74c3c'}},
                        285: {'label': 'PC', 'style': {'color': '#c0392b'}}
                    },
                    tooltip={"placement": "bottom", "always_visible": True},
                    className="temp-slider"
                ),
                className="slider-container"
            ),
            html.Br(),
            html.Label('Velocidad extrusión (cm/s)'),
            html.Div(
                dcc.Slider(
                    min=0,
                    max=10,
                    step=0.1,
                    value=3,
                    marks={
                        0: '0',
                        2: '2',
                        5: '5',
                        8: '8',
                        10: '10',
                        1: {'label': 'Muy baja', 'style': {'color': '#3498db'}},
                        3.5: {'label': 'Media', 'style': {'color': '#2ecc71'}},
                        6.5: {'label': 'Alta', 'style': {'color': '#f1c40f'}},
                        9: {'label': 'Muy alta', 'style': {'color': '#e74c3c'}}
                    },
                    tooltip={"placement": "bottom", "always_visible": True},
                    className="speed-slider"
                ),
                className="slider-container"
            ),
            html.Br(),
            html.Label('Velocidad enrolladora (cm/s)'),
            html.Div(
                dcc.Slider(
                    min=0,
                    max=10,
                    step=0.1,
                    value=3,
                    marks={
                        0: '0',
                        2: '2',
                        5: '5',
                        8: '8',
                        10: '10',
                        1: {'label': 'Muy baja', 'style': {'color': '#3498db'}},
                        3.5: {'label': 'Media', 'style': {'color': '#2ecc71'}},
                        6.5: {'label': 'Alta', 'style': {'color': '#f1c40f'}},
                        9: {'label': 'Muy alta', 'style': {'color': '#e74c3c'}}
                    },
                    tooltip={"placement": "bottom", "always_visible": True},
                    className="speed-slider"
                ),
                className="slider-container"
            ),
        ], className='card control_manual')
    ], className='manual-grid')


# ALARMAS/HISTORIAL LAYOUT
def alarms_history_layout():
    return html.Div([
        html.Div('Historial de alarmas', className='card datos_alarms_history'),
        html.Div('Alertas recientes', className='card datos_recient_alarms')
    ], className='alarms-history-grid')


# CALLBACKS
@callback(
    Output('tab_content', 'children'),
    Input('system-tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'monitoring':
        layout = monitoring_layout()
        return layout
    
    elif tab == 'automatic':
        layout = automatic_layout()
        return layout
    
    elif tab == 'manual':
        layout = manual_layout()
        return layout
    
    elif tab == 'alarms_history':
        layout = alarms_history_layout()
        return layout


# MAIN
if __name__ == '__main__':
    app.run(debug=True)