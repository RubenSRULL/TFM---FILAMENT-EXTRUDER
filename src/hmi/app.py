# AUTOR: Rubén Sahuquillo Redondo


# ===================== #
# ===== LIBRERIAS ===== #
# ===================== #
import dash
from dash import Dash, html, dcc, callback, Output, Input, State
import dash_daq as daq
import plotly.express as px
import pandas as pd


# ===== APP DASH ===== #
app = Dash(__name__, suppress_callback_exceptions=True)


# ================== #
# ===== LAYOUT ===== #
# ================== #
app.layout = html.Div([
    dcc.Store(id='store_monitoreo', storage_type='session'),
    dcc.Store(id='store_automatico', storage_type='session'),
    dcc.Store(id='store_manual', storage_type='session'),
    dcc.Store(id='store_alarmas', storage_type='session'),
    dcc.Tabs(id='system-tabs', value='monitoring', children=[
        dcc.Tab(label='Monitoreo', value='monitoring'),
        dcc.Tab(label='Automático', value='automatic'),
        dcc.Tab(label='Manual', value='manual'),
        dcc.Tab(label='Alarmas/Historial', value='alarms_history'),
    ], className='dash-tabs'),
    html.Div(id='tab_content', className='tab-content')
])

# ========================= #
# ===== TAB CALLBACKS ===== #
# ========================= #
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


# ============================= #
# ===== MONITORING LAYOUT ===== #
# ============================= #
def monitoring_layout():
    return html.Div([
        html.H3('Estado general del sistema'),
        html.Div([
        ], className='container'),
        html.H3('Datos del proceso'),
        html.Div([
        ], className='container'),
        html.H3('Variables del sistema'),
        html.Div([
        ], className='container'),
        html.H3('Diámetro del filamento'),
        html.Div([
        ], className='container'),
        html.H3('Imagen del filamento'),
        html.Div([
        ], className='container'),
        html.H3('Alarmas activas'),
        html.Div([
        ], className='container')
    ])


# ================================ #
# ===== MONITORING CALLBACKS ===== #
# ================================ #


# ================================== #
# ===== MODO AUTOMATICO LAYOUT ===== #
# ================================== #
def automatic_layout():
    """
    Layout para el modo automático, con fases y gráficos de datos en tiempo real
    """
    return html.Div([
        dcc.Store(id='auto_phase', data=0),
        dcc.Store(id='store_auto_material', data='pla'),

        html.H3('Fases del proceso'),
        html.Div([
            html.Div(id='phase_indicator', className='phase-indicator-container'),
            html.Div(id='phase_content', className='phase-content-container'),

            html.Div([
                html.Button("Anterior", id="btn_prev_phase", n_clicks=0, className="phase-btn"),
                html.Button("Siguiente", id="btn_next_phase", n_clicks=0, className="phase-btn")
            ], className='button-container-fixed')

        ], className='container phase-container'),

        html.H3('Gráficas del proceso'),
        html.Div([
                dcc.Graph(id='diameter-graph', figure=px.line(x=[0], y=[0], title='Diámetro del filamento'), className='graph'),
                dcc.Graph(id='temperature-graph', figure=px.line(x=[0], y=[0], title='Variables extrusora'), className='graph')
        ], className='graphs-container'),
    ])
        

# ================================ #
# ===== CALLBACKS AUTOMATICO ===== #
# ================================ #
@callback(
    Output('store_auto_material', 'data'),
    Input('auto_material', 'value'),
    prevent_initial_call=True
)
def guardar_material(material):
    return material


@callback(
    Output("btn_prev_phase", "style"),
    Output("btn_next_phase", "style"),
    Input("auto_phase", "data")
)
def update_buttons_visibility(phase):
    prev_style = {"display": "none"} if phase == 0 else {}
    next_style = {"display": "none"} if phase == 4 else {}
    return prev_style, next_style


# --- Callback para controlar el avance entre fases del proceso automático --- #
@callback(
    Output('auto_phase', 'data'),
    Input('btn_next_phase', 'n_clicks'),
    Input('btn_prev_phase', 'n_clicks'),
    Input('auto_phase', 'data'),
)
def update_phase(next_clicks, prev_clicks, current_phase):
    """
    Callback para actualizar la fase del proceso automático. Controla el avance y retroceso entre fases.
        :param next_clicks: número de clicks en el botón "Siguiente"
        :param prev_clicks: número de clicks en el botón "Anterior"
        :param current_phase: fase actual del proceso
        :return: nueva fase actualizada
    """
    ctx = dash.callback_context

    if not ctx.triggered:
        return current_phase

    button = ctx.triggered[0]['prop_id'].split('.')[0]

    if button == "btn_next_phase":
        return min(current_phase + 1, 4)

    elif button == "btn_prev_phase":
        return max(current_phase - 1, 0)

    return current_phase


# --- Callback para actualizar el indicador de fases en el modo automático --- #
@callback(
    Output('phase_indicator', 'children'),
    Input('auto_phase', 'data'),
)
def update_phase_indicator(phase):
    """
    Actualiza el indicador de fases como flujograma.
    """
    phases = ["Configuración", "Preparación", "Calentamiento", "Guiado manual", "Producción"]
    flow = []

    for i, name in enumerate(phases):
        if i < phase:
            color = "#4CAF50"

        elif i == phase:
            color = "#2196F3"

        else:
            color = "#BDBDBD"

        flow.append(
            html.Div([
                html.Div(str(i+1), className="phase-circle", style={"backgroundColor": color}),
                html.Div(name, className="phase-label")
            ],className="phase-step")
        )

        if i < len(phases) - 1:
            flow.append(html.Div("➜", className="phase-arrow"))

    return html.Div(flow, className="phase-flow")


# --- Callback para actualizar el contenido de cada fase en el modo automático --- #
@callback(
    Output('phase_content', 'children'),
    Input('auto_phase', 'data'),
    State('store_auto_material', 'data'),
    prevent_initial_call=True
)
def update_phase_content(phase, material):
    if phase == 0:
        return html.Div([
            html.H4("Configuración"),
            html.Div([
                html.Div([
                    html.Label("Material"),
                    dcc.Dropdown(
                        options=[
                            {'label': 'PLA', 'value': 'pla'},
                            {'label': 'ABS', 'value': 'abs'},
                            {'label': 'PETG', 'value': 'petg'},
                            {'label': 'Nylon', 'value': 'nylon'},
                            {'label': 'PC', 'value': 'pc'},
                            {'label': 'LDPE', 'value': 'ldpe'},
                            {'label': 'HDPE', 'value': 'hdpe'},
                            {'label': 'PP', 'value': 'pp'}
                        ],
                        id='auto_material',
                        value='pla',
                        className='material-dropdown'
                    ),
                ], className="config-item"),
                html.Div([
                    html.Label("Diámetro"),
                    dcc.Input(type="number", value=1.75, className="diameter-input"),
                ], className="config-item"),
            ], className="config-row")
        ])
    
    elif phase == 1:
        return html.Div([html.H4("Preparación del sistema")])
    
    elif phase == 2:
        return html.Div([
            html.H4("Calentamiento extrusora"),
            html.Div([
                dcc.Slider(
                    id = 'auto_temp_slider',
                    min=180,
                    max=220,
                    step=1,
                    value=200,
                    marks={
                        180: '180',
                        200: '200',
                        220: '220',
                    },
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
            ]),

            html.Div([
                daq.BooleanSwitch(
                    id='switch_auto_temp',
                    on=False,
                    label="OFF / ON",
                    labelPosition="top"
                )
            ], className='switch-container')
        ])
    
    elif phase == 3:
        return html.Div([html.H4("Guiado manual del filamento")])
    
    elif phase == 4:
        return html.Div([html.H4("Producción"), daq.BooleanSwitch(id='switch_auto_process', on=False, label="OFF / ON")])


# ============================== #
# ===== MODO MANUAL LAYOUT ===== #
# ============================== #
def manual_layout():
    return html.Div([
        html.H3('Controles del sistema'),
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
                ),
            ),
            html.Label('Velocidad extrusión (cm/s)'),
            html.Div(
                dcc.Slider(
                    min=0,
                    max=10,
                    step=0.1,
                    value=0,
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
                ),
            ),
            html.Label('Velocidad enrolladora (cm/s)'),
            html.Div(
                dcc.Slider(
                    min=0,
                    max=10,
                    step=0.1,
                    value=0,
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
                ),
            ),

            html.Div([
                daq.BooleanSwitch(
                    id='switch_manual',
                    on=False,
                    label="OFF / ON",
                    labelPosition="top",
                    color="#28a745"
                )
            ], className='switch-container')

        ], className='container'),
        html.H3('Gráficas del proceso'),
        html.Div([
                dcc.Graph(id='diameter-graph', figure=px.line(x=[0], y=[0], title='Diámetro del filamento'), className='graph'),
                dcc.Graph(id='temperature-graph', figure=px.line(x=[0], y=[0], title='Variables extrusora'), className='graph')
        ], className='graphs-container'),
    ])


# ============================ #
# ===== CALLBACKS MANUAL ===== #
# ============================ #
pass

# ==================================== #
# ===== ALARMAS/HISTORIAL LAYOUT ===== #
# ==================================== #
def alarms_history_layout():
    return html.Div([
        html.Div([
            html.Label('Alarmas activas'),
            html.Div(id='active-alarms', children=[])
        ], className='container'),
        html.Div([
            html.Label('Alarmas recientes'),
            html.Div(id='recent-alarms', children=[])
        ], className='container')
    ])


# ================ #
# ===== MAIN ===== #
# ================ #
if __name__ == '__main__':
    app.run(debug=True)