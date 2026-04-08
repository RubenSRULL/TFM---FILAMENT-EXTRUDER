# python -m src.hmi.app
# source myenv/bin/activate
# ip link show can0
# sudo ip link set can0 down
# sudo ip link set can0 up type can bitrate 500000


#------------------#
#---- Módulos -----#
#------------------#
from dash import Dash, html, dcc, callback, Output, Input, State, ctx, no_update
from datetime import datetime
from flask import Flask, Response
from src.backend.CAMARA_HQ import CAMARA_HQ
from src.backend.CAN_COM import CAN_COM
from gpiozero import LED


#------------------#
#---- Objetos -----#
#------------------#    

# Aplicacion Dash
app = Dash(__name__, suppress_callback_exceptions=True)
# Camara HQ
camara = CAMARA_HQ()
# Servidor 
server = app.server
# Láser
laser = LED(4, initial_value=False)
# Comunicación CAN
can_com = CAN_COM()
can_com.iniciar_recepcion()


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
                    className='grafico'),
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
                    className='grafico'),
                ]
            ),
        ]
    )


# Función de Automatico
def automatico():
    return html.Div(
        className='contenedor_fases',
        children=[
            html.Div([
                html.Label("1", className='fase_auto'),
                html.Label("Configuración"),
            ], className='fila_fase_auto'),

            html.Div([
                html.Label("2", className='fase_auto'),
                html.Label("Calentamiento"),
            ], className='fila_fase_auto'),

            html.Div([
                html.Label("3", className='fase_auto'),
                html.Label("Guiado"),
            ], className='fila_fase_auto'),

            html.Div([
                html.Label("4", className='fase_auto'),
                html.Label("Extrusión"),
            ], className='fila_fase_auto'),

            html.Div([
                html.Label("5", className='fase_auto'),
                html.Label("Finalización"),
            ], className='fila_fase_auto'),
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
                            115: {'label': '115°C','style': {'color': "#88d002"}},
                            180: {'label': '180°C','style': {'color': "#baa801"}},
                            220: {'label': '220°C','style': {'color': "#baa801"}},
                            230: {'label': '230°C','style': {'color': "#ae5502"}},
                            250: {'label': '250°C','style': {'color': "#ae5502"}},
                            360: {'label': '360°C','style': {'color': "#ae0202"}},
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
                    className='contenedor-botones'),
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
                    className='contenedor-botones'),
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
        can_com.enviar_mensaje(0x201, "AUTO")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        msg = f"Sección: Automático cargada. {'Modo automático activado en uC.' if exito else 'Error al activar modo automático en uC.'}"
        contenido = automatico()

    elif id_disparador == 'btn-manual':
        can_com.enviar_mensaje(0x202, "MANUAL")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        msg = f"Sección: Manual cargada. {'Modo manual activado en uC.' if exito else 'Error al activar modo manual en uC.'}"
        contenido = manual()

    else:
        return ctx.no_update, ctx.no_update

    logs_actuales.append(html.P(f"[{hora}] > {msg}"))
    return contenido, logs_actuales


# CALLBACK BOTONES MANUAL
@callback(
    Output('log-sistema', 'children', allow_duplicate=True),
    Output('calefactor-estado', 'children', allow_duplicate=True),
    Output('motor-extrusora-estado', 'children', allow_duplicate=True),
    Output('motor-enrolladora-estado', 'children', allow_duplicate=True),
    Output('laser-estado', 'children', allow_duplicate=True),
    Input('temperatura-on', 'n_clicks'),
    Input('temperatura-off', 'n_clicks'),
    Input('velocidad-extrusora-on', 'n_clicks'),
    Input('velocidad-extrusora-off', 'n_clicks'),
    Input('velocidad-enrolladora-on', 'n_clicks'),
    Input('velocidad-enrolladora-off', 'n_clicks'),
    Input('laser-on', 'n_clicks'),
    Input('laser-off', 'n_clicks'),
    State('slider-temperatura', 'value'),
    State('slider-velocidad-extrusora', 'value'),
    State('slider-velocidad-enrolladora', 'value'),
    State('log-sistema', 'children'),
    prevent_initial_call=True
)
def botones_manual(n_on1, n_off1, n_on2, n_off2, n_on3, n_off3, n_on4, n_off4, slider_temp, slider_vel_extr, slider_vel_enroll, logs_actuales):
    if logs_actuales is None:
        logs_actuales = []

    id_disparador = ctx.triggered_id
    hora = datetime.now().strftime('%H:%M:%S')

    # Inicializamos todas las salidas como no_update
    # Esto evita el UnboundLocalError si no se entra en un IF específico
    calefactor_estado = no_update
    motor_extrusora_estado = no_update
    motor_enrolladora_estado = no_update
    laser_estado = no_update

    # --- LÓGICA DE CALEFACTOR ---
    if id_disparador == "temperatura-on" and n_on1:
        can_com.enviar_mensaje(0x100, f"C_ON{slider_temp}")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        logs_actuales.append(html.P(f"[{hora}] > {'Encendiendo' if exito else 'Error'} Calefactor"))
        # Re-insertamos el Label para no perderlo en el layout
        calefactor_estado = [html.Label("Calefactor"), html.Div(className='led-on' if exito else 'led-off')]
        
    elif id_disparador == "temperatura-off" and n_off1:
        can_com.enviar_mensaje(0x100, "C_OFF")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        logs_actuales.append(html.P(f"[{hora}] > {'Apagando' if exito else 'Error'} Calefactor"))
        calefactor_estado = [html.Label("Calefactor"), html.Div(className='led-off' if exito else 'led-on')]

    # --- LÓGICA DE EXTRUSORA ---
    elif id_disparador == "velocidad-extrusora-on" and n_on2:
        can_com.enviar_mensaje(0x101, f"EX_ON{slider_vel_extr}")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        logs_actuales.append(html.P(f"[{hora}] > {'Encendiendo' if exito else 'Error'} Motor Extrusora"))
        motor_extrusora_estado = [html.Label("Motor Extrusora"), html.Div(className='led-on' if exito else 'led-off')]

    elif id_disparador == "velocidad-extrusora-off" and n_off2:
        can_com.enviar_mensaje(0x101, "EX_OFF")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        logs_actuales.append(html.P(f"[{hora}] > {'Apagando' if exito else 'Error'} Motor Extrusora"))
        motor_extrusora_estado = [html.Label("Motor Extrusora"), html.Div(className='led-off' if exito else 'led-on')]

    # --- LÓGICA DE ENROLLADORA ---
    elif id_disparador == "velocidad-enrolladora-on" and n_on3:
        can_com.enviar_mensaje(0x102, f"EN_ON{slider_vel_enroll}")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        logs_actuales.append(html.P(f"[{hora}] > {'Encendiendo' if exito else 'Error'} Motor Enrolladora"))
        motor_enrolladora_estado = [html.Label("Motor Enrolladora"), html.Div(className='led-on' if exito else 'led-off')]

    elif id_disparador == "velocidad-enrolladora-off" and n_off3:
        can_com.enviar_mensaje(0x102, "EN_OFF")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        logs_actuales.append(html.P(f"[{hora}] > {'Apagando' if exito else 'Error'} Motor Enrolladora"))
        motor_enrolladora_estado = [html.Label("Motor Enrolladora"), html.Div(className='led-off' if exito else 'led-on')]

    # --- LÓGICA DE LÁSER ---
    elif id_disparador == "laser-on" and n_on4:
        laser.on()
        logs_actuales.append(html.P(f"[{hora}] > Encendiendo Láser"))
        laser_estado = [html.Label("Láser"), html.Div(className='led-on')]

    elif id_disparador == "laser-off" and n_off4:
        laser.off()
        logs_actuales.append(html.P(f"[{hora}] > Apagando Láser"))
        laser_estado = [html.Label("Láser"), html.Div(className='led-off')]

    # Si no hubo disparador válido (aunque prevent_initial_call debería evitarlo)
    else:
        return no_update, no_update, no_update, no_update, no_update

    return logs_actuales, calefactor_estado, motor_extrusora_estado, motor_enrolladora_estado, laser_estado

# Función para alimentar el video en tiempo real
@server.route('/video_feed')
def video_feed():
    return Response(
        camara.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.callback(
    Output('log-sistema', 'children', allow_duplicate=True),
    Output('calefactor-estado', 'children', allow_duplicate=True),
    Output('motor-extrusora-estado', 'children', allow_duplicate=True),
    Output('motor-enrolladora-estado', 'children', allow_duplicate=True),
    Output('laser-estado', 'children', allow_duplicate=True),
    Input('btn-parada', 'n_clicks'),
    State('log-sistema', 'children'),
    prevent_initial_call=True
)
def parada_emergencia(n_clicks, logs_actuales):
    if logs_actuales is None:
        logs_actuales = []

    id_disparador = ctx.triggered_id
    hora = datetime.now().strftime('%H:%M:%S')

    calefactor_estado = no_update
    motor_extrusora_estado = no_update
    motor_enrolladora_estado = no_update
    laser_estado = no_update

    if id_disparador == 'btn-parada' and n_clicks:
        can_com.enviar_mensaje(0x400, "STOP")
        respuesta = can_com.get_mensaje()
        exito = respuesta and respuesta[1] == "OK"
        msg = f"¡PARADA DE EMERGENCIA ACTIVADA! {'Parada de emergencia activada en uC.' if exito else 'Error al activar parada de emergencia en uC.'}"
        logs_actuales.append(html.P(f"[{hora}] > {msg}"))
        calefactor_estado = [html.Label("Calefactor"), html.Div(className='led-off' if exito else 'led-off')]
        motor_extrusora_estado = [html.Label("Motor Extrusora"), html.Div(className='led-off' if exito else 'led-off')]
        motor_enrolladora_estado = [html.Label("Motor Enrolladora"), html.Div(className='led-off' if exito else 'led-off')]
        laser_estado = [html.Label("Láser"), html.Div(className='led-off' if exito else 'led-off')]
        laser.off()

    return logs_actuales, calefactor_estado, motor_extrusora_estado, motor_enrolladora_estado, laser_estado


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)