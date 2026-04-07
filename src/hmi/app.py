#------------------#
#---- Módulos -----#
#------------------#
from dash import Dash, html, dcc, callback, Output, Input, State, ctx
from datetime import datetime
from flask import Flask, Response
from backend import CAMERA_HQ
from gpiozero import LED


#------------------#
#---- Objetos -----#
#------------------#

# Aplicacion Dash
app = Dash(__name__, suppress_callback_exceptions=True)
# Camara HQ
camara = CAMERA_HQ()
# Servidor 
server = app.server
# Láser
laser = LED(4, initial_value=False)


#--------------------#
#---- Funciones -----#
#--------------------#

# Layout de monitoreo
def monitoreo():
    return html.Div(
        className='seccion-monitoreo',
        children=[
            html.Div(
                className='fila_graficos',
                children=[
                    dcc.Graph(
                        id='grafico-diametro',
                        responsive=True,
                        figure={
                            'data': [{'x': [1,2,3], 'y':[4,1,2], 'type':'line', 'name':'Diámetro'}],
                            'layout': {
                                'title': {
                                    'text': 'Diámetro en tiempo real',
                                    'font': {'color': 'black', 'size': 20}
                                },
                                'xaxis': {
                                    'title': {'text': 'Tiempo (s)', 'font': {'color': 'black'}},
                                    'automargin': True
                                },
                                'yaxis': {
                                    'title': {'text': 'Diámetro (mm)', 'font': {'color': 'black'}},
                                    'automargin': True
                                },
                                'template': 'plotly_white',
                                'margin': {'t': 80, 'l': 80, 'r': 40, 'b': 80},
                                'paper_bgcolor': 'white',
                                'plot_bgcolor': '#f9f9f9'
                            }
                        },
                        className='grafico',
                    ),
                    html.Img(id='video-feed', src='/video_feed', className='grafico-img'),
                    dcc.Interval(id='intervalo-camara',interval=100,n_intervals=0),
                ]
            ),

            html.Div(
                className='fila_graficos',
                children=[
                    dcc.Graph(
                        id='grafico-temperatura-humedad',
                        responsive=True,
                        figure={
                            'data': [{'x': [1,2,3], 'y':[4,1,2], 'type':'line', 'name':'Temperatura y humedad'}],
                            'layout': {
                                'title': {
                                    'text': 'Temperatura y humedad tiempo real',
                                    'font': {'color': 'black', 'size': 20}
                                },
                                'xaxis': {
                                    'title': {'text': 'Tiempo (s)', 'font': {'color': 'black'}},
                                    'automargin': True
                                },
                                'yaxis': {
                                    'title': {'text': 'Diámetro (mm)', 'font': {'color': 'black'}},
                                    'automargin': True
                                },
                                'template': 'plotly_white',
                                'margin': {'t': 80, 'l': 80, 'r': 40, 'b': 80},
                                'paper_bgcolor': 'white',
                                'plot_bgcolor': '#f9f9f9'
                            }
                        },
                        className='grafico',
                    ),
                    dcc.Graph(
                        id='grafico-velocidades',
                        responsive=True,
                        figure={
                            'data': [{'x': [1,2,3], 'y':[4,1,2], 'type':'line', 'name':'Velocidades'}],
                            'layout': {
                                'title': {
                                    'text': 'Velocidades en tiempo real',
                                    'font': {'color': 'black', 'size': 20}
                                },
                                'xaxis': {
                                    'title': {'text': 'Tiempo (s)', 'font': {'color': 'black'}},
                                    'automargin': True
                                },
                                'yaxis': {
                                    'title': {'text': 'Diámetro (mm)', 'font': {'color': 'black'}},
                                    'automargin': True
                                },
                                'template': 'plotly_white',
                                'margin': {'t': 80, 'l': 80, 'r': 40, 'b': 80},
                                'paper_bgcolor': 'white',
                                'plot_bgcolor': '#f9f9f9'
                            }
                        },
                        className='grafico',
                    ),
                ]
            ),
        ]
    )


# Función de Automatico
def automatico():
    return html.Div(children=[
        
        ]
    )


# Función de Manual
def manual():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.H3("Temperatura Calefactor"),
                    dcc.Slider(
                        id='slider-temperatura',
                        min=100,
                        max=400,
                        value=100,
                        step=1,
                        marks={
                            100: {'label': '100°C','style': {'color': "#64f006"}},
                            107: {'label': 'LDPE','style': {'color': "#64f006"}},
                            115: {'label': '115°C','style': {'color': "#88d002"}},
                            150: {'label': 'HDPE','style': {'color': "#88d002"}},
                            180: {'label': '180°C','style': {'color': "#baa801"}},
                            200: {'label': 'PLA','style': {'color': "#baa801"}},
                            220: {'label': '220°C','style': {'color': "#baa801"}},
                            230: {'label': '230°C','style': {'color': "#ae5502"}},
                            240: {'label': 'ABS','style': {'color': "#ae5502"}},
                            250: {'label': '250°C','style': {'color': "#ae5502"}},
                            360: {'label': '360°C','style': {'color': "#ae0202"}},
                            380: {'label': 'PEEK','style': {'color': "#ae0202"}},
                            400: {'label': '400°C','style': {'color': "#ae0202"}},
                        },
                        included=False,
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                    html.Div(
                        [
                            html.Button("ON", id='temperatura-on', n_clicks=0, className='btn-on'),
                            html.Button("OFF", id='temperatura-off', n_clicks=0, className='btn-off'),
                        ],
                    className='contenedor-botones',),
                ],
            className='contenedor_slider_botones'),

            html.Div(
                children=[
                    html.H3("Velocidad Extrusor"),
                    dcc.Slider(
                        id='slider-velocidad-extrusora',
                        min=0,
                        max=10,
                        value=0,
                        step=0.1,
                        marks={
                            0: {'label': '0 mm/s'},
                            1: {'label': '1 mm/s'},
                            2: {'label': '2 mm/s'},
                            3: {'label': '3 mm/s'},
                            4: {'label': '4 mm/s'},
                            5: {'label': '5 mm/s'},
                            6: {'label': '6 mm/s'},
                            7: {'label': '7 mm/s'},
                            8: {'label': '8 mm/s'},
                            9: {'label': '9 mm/s'},
                            10: {'label': '10 mm/s'},
                        },
                        included=False,
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                html.Div(
                        [
                            html.Button("ON", id='velocidad-extrusora-on', n_clicks=0, className='btn-on'),
                            html.Button("OFF", id='velocidad-extrusora-off', n_clicks=0, className='btn-off'),
                        ],
                    className='contenedor-botones',),
                ],
            className='contenedor_slider_botones'),

            html.Div(
                children=[
                    html.H3("Velocidad Enrolladora"),
                    dcc.Slider(
                        id='slider-velocidad-enrolladora',
                        min=0,
                        max=10,
                        value=0,
                        step=0.1,
                        marks={
                            0: {'label': '0 mm/s'},
                            1: {'label': '1 mm/s'},
                            2: {'label': '2 mm/s'},
                            3: {'label': '3 mm/s'},
                            4: {'label': '4 mm/s'},
                            5: {'label': '5 mm/s'},
                            6: {'label': '6 mm/s'},
                            7: {'label': '7 mm/s'},
                            8: {'label': '8 mm/s'},
                            9: {'label': '9 mm/s'},
                            10: {'label': '10 mm/s'},
                        },
                        included=False,
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                html.Div(
                        [
                            html.Button("ON", id='velocidad-enrolladora-on', n_clicks=0, className='btn-on'),
                            html.Button("OFF", id='velocidad-enrolladora-off', n_clicks=0, className='btn-off'),
                        ],
                    className='contenedor-botones',),
                ],
            className='contenedor_slider_botones'),

            html.Div([
                html.H3("Control Laser"),
                html.Div(
                        [
                            html.Button("ON", id='laser-on', n_clicks=0, className='btn-on'),
                            html.Button("OFF", id='laser-off', n_clicks=0, className='btn-off'),
                        ],
                    className='contenedor-botones',)
                ],
            className='contenedor_slider_botones'),
        ],
    className='seccion_manual')


# LAYOUT PRINCIPAL
app.layout = html.Div([
    # PANEL LATERAL
    html.Div([
        html.Div(
            [
                html.Button("Monitoreo", id='btn-monitoreo', className='boton_menu'),
                html.Button("Automático", id='btn-automatico', className='boton_menu'),
                html.Button("Manual", id='btn-manual', className='boton_menu'),
            ],
        className='menu'),
        
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Diámetro"),
                        html.Span("0.00", className="display")
                    ],
                className='label-display-parametros'),

                html.Div(
                    [
                        html.Label("Temperatura"),
                        html.Span("0.00", className="display")
                    ],
                className='label-display-parametros'),

                html.Div(
                    [
                        html.Label("Vel. Extrusión"),
                        html.Span("0.00", className="display")
                    ],
                className='label-display-parametros'),

                html.Div(
                    [
                        html.Label("Vel. Enrolladora"),
                        html.Span("0.00", className="display")
                    ],
                className='label-display-parametros'),

                html.Button("Parada", id='btn-parada', className='boton_parada'),
            ],
        className='parametros'),

        html.Div(
            [
                html.Div(id='calefactor-estado',
                        children=[
                            html.Label("Calefactor"),
                            html.Div(className='led-off')
                        ],
                        className='estado'),
                
                html.Div(id='motor-extrusora-estado',
                        children=[
                            html.Label("Motor Extrusora"),
                            html.Div(className='led-off')
                        ],
                        className='estado'),

                html.Div(id='motor-enrolladora-estado',
                         children=[
                            html.Label("Motor Enrolladora"),
                            html.Div(className='led-off')
                        ],
                        className='estado'),
                    
                html.Div(id='laser-estado',
                        children=[
                            html.Label("Láser"),
                            html.Div(className='led-off')
                        ],
                        className='estado'),
                    
                html.Div(id='camara-estado',
                        children=[
                            html.Label("Cámara"),
                            html.Div(className='led-off')
                        ],
                        className='estado'),
            ],
        className='estados'),
    ],
    className='contenedor_lateral'),

    # CONTENIDO DERECHO
    html.Div([
        html.Div(id='contenido', children=monitoreo()), 
        html.Div(
            [
                html.P(f"[{datetime.now().strftime('%H:%M:%S')}] > Sistema iniciado..."),
            ],
            id='log-sistema',
            className='contenedor_log'),
    ],
    className='contenedor_contenido_menu'),

    #MEMORIA
    dcc.Store(id='store-graficos', storage_type='memory'), 
    dcc.Store(id='store-estado-maquina', storage_type='memory'),
],
className='contenedor_principal')


# CALLBACK MENU LATERAL
@callback(
    Output('contenido', 'children'),
    Output('log-sistema', 'children', ),
    Input('btn-monitoreo', 'n_clicks'),
    Input('btn-automatico', 'n_clicks'),
    Input('btn-manual', 'n_clicks'),
    State('log-sistema', 'children'),
    prevent_initial_call=True
)
def actualizar_interfaz(n1, n2, n3, logs_actuales):
    if logs_actuales is None:
        logs_actuales = []

    id_disparador = ctx.triggered_id
    hora = datetime.now().strftime('%H:%M:%S')
    
    if id_disparador == 'btn-monitoreo':
        contenido = monitoreo()
        msg = "Sección: Monitoreo cargada."
    elif id_disparador == 'btn-automatico':
        contenido = automatico()
        msg = "Sección: Automático cargada."
    elif id_disparador == 'btn-manual':
        contenido = manual()
        msg = "Sección: Manual cargada."
    else:
        return ctx.no_update, ctx.no_update

    logs_actuales.append(html.P(f"[{hora}] > {msg}"))
    return contenido, logs_actuales


@app.callback(
    Output('log-sistema', 'children', allow_duplicate=True),
    Input('temperatura-on', 'n_clicks'),
    Input('temperatura-off', 'n_clicks'),
    Input('velocidad-extrusora-on', 'n_clicks'),
    Input('velocidad-extrusora-off', 'n_clicks'),
    Input('velocidad-enrolladora-on', 'n_clicks'),
    Input('velocidad-enrolladora-off', 'n_clicks'),
    Input('laser-on', 'n_clicks'),
    Input('laser-off', 'n_clicks'),
    State('log-sistema', 'children'),
    prevent_initial_call=True
)
def botones_manual(n_on1, n_off1, n_on2, n_off2, n_on3, n_off3, n_on4, n_off4, logs_actuales):
    if logs_actuales is None:
        logs_actuales = []

    id_disparador = ctx.triggered_id
    hora = datetime.now().strftime('%H:%M:%S')

    if id_disparador == "temperatura-on" and n_on1:
        logs_actuales.append(html.P(f"[{hora}] > Encendiendo Calefactor"))
        
    elif id_disparador == "temperatura-off" and n_off1:
        logs_actuales.append(html.P(f"[{hora}] > Apagando Calefactor"))

    elif id_disparador == "velocidad-extrusora-on" and n_on2:
        logs_actuales.append(html.P(f"[{hora}] > Encendiendo Motor Extrusora"))

    elif id_disparador == "velocidad-extrusora-off" and n_off2:
        logs_actuales.append(html.P(f"[{hora}] > Apagando Motor Extrusora"))

    elif id_disparador == "velocidad-enrolladora-on" and n_on3:
        logs_actuales.append(html.P(f"[{hora}] > Encendiendo Motor Enrolladora"))

    elif id_disparador == "velocidad-enrolladora-off" and n_off3:
        logs_actuales.append(html.P(f"[{hora}] > Apagando Motor Enrolladora"))

    elif id_disparador == "laser-on" and n_on4:
        logs_actuales.append(html.P(f"[{hora}] > Encendiendo Láser"))
        laser.on()

    elif id_disparador == "laser-off" and n_off4:
        logs_actuales.append(html.P(f"[{hora}] > Apagando Láser"))
        laser.off()

    return logs_actuales


@server.route('/video_feed')
def video_feed():
    return Response(
        camara.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.callback(
    Output('log-sistema', 'children', allow_duplicate=True),
    Input('btn-parada', 'n_clicks'),
    State('log-sistema', 'children'),
    prevent_initial_call=True
)
def parada_emergencia(n_clicks, logs_actuales):
    if logs_actuales is None:
        logs_actuales = []

    id_disparador = ctx.triggered_id
    hora = datetime.now().strftime('%H:%M:%S')

    if id_disparador == 'btn-parada' and n_clicks:
        logs_actuales.append(html.P(f"[{hora}] > ¡PARADA DE EMERGENCIA ACTIVADA!"))
        laser.off()

    return logs_actuales


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)