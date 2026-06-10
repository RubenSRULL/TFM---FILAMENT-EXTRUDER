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
camara = CAMARA_HQ(verbose=True)
# Servidor Flask para streaming de video
server = app.server
# Láser
laser = LED(4, initial_value=False)
# Comunicación CAN
can_com = CAN_COM(modo_simulado=True)
can_com.iniciar_recepcion()


#--------------------#
#---- Variables -----#
#--------------------#   
diametros = []
velocidades_extrusora = []
velocidades_enrolladora = []
temperaturas = []
humedades = []
tiempos = []


#--------------------#
#---- Funciones -----#
#--------------------#
# Función para crear figuras de líneas para Plotly
def crear_figura_lineas(titulo, x_label, y_label, series):
    """
    Descripción:
        Crea una figura de líneas para Plotly a partir de los datos proporcionados.
    
    Parámetros:
        - titulo (str): Título del gráfico.
        - x_label (str): Etiqueta para el eje X.
        - y_label (str): Etiqueta para el eje Y.
        - series (list): Lista de tuplas con los datos para cada serie.
    
    Retorno:
        - dict: Configuración de la figura para Plotly.

    """
    return {
        "data": [
            {
                "x": x,
                "y": y,
                "type": "scatter",
                "mode": "lines+markers",
                "name": nombre,
            }
            for nombre, x, y in series
        ],
        "layout": {
            "title": {
                "text": titulo,
                "font": {"color": "black", "size": 20},
            },
            "xaxis": {
                "title": {"text": x_label, "font": {"color": "black"}},
                "automargin": True,
            },
            "yaxis": {
                "title": {"text": y_label, "font": {"color": "black"}},
                "automargin": True,
            },
            "template": "plotly_white",
            "margin": {"t": 80, "l": 80, "r": 40, "b": 80},
            "paper_bgcolor": "white",
            "plot_bgcolor": "#f9f9f9",
        },
    }


# Función para crear el layout de monitoreo
def monitoreo():
    """
    Descripción:
        Crea el layout para la sección de monitoreo, que incluye gráficos en tiempo real y un feed de video.

    Parámetros:
        - Ninguno.

    Retorno:
        - html.Div: Componente de Dash con el layout del monitoreo.
    """
    return html.Div(
        className='seccion-monitoreo',
        children=[
            html.Div(
                className='fila_graficos',
                children=[
                    dcc.Graph(
                        id='grafico-diametro',
                        responsive=True,
                        figure=crear_figura_lineas(
                            'Diámetro en tiempo real',
                            'Tiempo (s)',
                            'Diámetro (mm)',
                            [('Diámetro', [], [])],
                        ),
                        className='grafico',
                    ),
                    html.Img(id='video-feed', src='/video_feed', className='grafico-img'),
                ]
            ),

            html.Div(
                className='fila_graficos',
                children=[
                    dcc.Graph(
                        id='grafico-temperatura-humedad',
                        responsive=True,
                        figure=crear_figura_lineas(
                            'Temperatura y humedad tiempo real',
                            'Tiempo (s)',
                            'Temperatura / Humedad',
                            [
                                ('Temperatura', [], []),
                                ('Humedad', [], []),
                            ],
                        ),
                        className='grafico',
                    ),
                    dcc.Graph(
                        id='grafico-velocidades',
                        responsive=True,
                        figure=crear_figura_lineas(
                            'Velocidades en tiempo real',
                            'Tiempo (s)',
                            'Velocidad (mm/s)',
                            [
                                ('Extrusora', [], []),
                                ('Enrolladora', [], []),
                            ],
                        ),
                        className='grafico',
                    ),
                ]
            ),
        ]
    )



FASES_AUTOMATICAS = [
    {"titulo": "Configuración", "descripcion": "Configura el material y los parámetros base del proceso."},
    {"titulo": "Temperatura", "descripcion": "Ajusta y aplica la temperatura del calefactor."},
    {"titulo": "Guiado", "descripcion": "Prepara el guiado del filamento antes de extruir."},
    {"titulo": "Extrusión", "descripcion": "Ajusta velocidades de extrusora y enrolladora."},
    {"titulo": "Finalización", "descripcion": "Cierra el proceso de forma ordenada."},
]


# Función para crear los indicadores de fases automáticas
def crear_indicadores_fases(fase_activa):
    """
    Descripción:
        Crea los indicadores visuales para las fases automáticas, resaltando la fase activa y las completadas.
    
    Parámetros:
        - fase_activa (int): Índice de la fase actualmente activa.
    
    Retorno:
        - list: Lista de componentes html.Div que representan los indicadores de fase.
    """
    indicadores = []

    for indice, fase in enumerate(FASES_AUTOMATICAS):
        activa = indice == fase_activa
        completada = indice < fase_activa

        indicadores.append(
            html.Div(
                [
                    html.Div(
                        str(indice + 1),
                        className=(
                            'fase_auto fase_auto_activa'
                            if activa
                            else 'fase_auto fase_auto_completada'
                            if completada
                            else 'fase_auto'
                        ),
                    ),
                    html.Label(
                        fase['titulo'],
                        className=(
                            'label_fase_auto label_fase_auto_activa'
                            if activa
                            else 'label_fase_auto'
                        ),
                    ),
                ],
                className='fila_fase_auto',
            )
        )

    return indicadores


# Función para crear el contenido de cada fase automática
def crear_contenido_fase_automatica(fase_activa):
    """
    Descripción:
        Crea el contenido específico para cada fase del proceso automático, incluyendo controles y descripciones.
    
    Parámetros:
        - fase_activa (int): Índice de la fase actualmente activa.
    
    Retorno:
        - html.Div: Componente de Dash con el contenido de la fase activa.
    """
    fase = FASES_AUTOMATICAS[fase_activa]

    if fase_activa == 0:
        controles = [
            html.Div(
                [
                    html.Label("Material"),
                    dcc.Dropdown(
                        id='auto-material',
                        options=[
                            {'label': 'PLA', 'value': 'PLA'},
                            {'label': 'ABS', 'value': 'ABS'}
                        ],
                        value='PLA',
                        clearable=False,
                    ),
                ],
                className='campo_auto',
            ),
            html.Div(
                [
                    html.Label("Tiempo de proceso (min)"),
                    dcc.Input(id='auto-tiempo', type='number', min=1, step=1, value=10),
                ],
                className='campo_auto',
            ),
            html.Div(
                [
                    html.Label("Diámetro objetivo (mm)"),
                    dcc.Input(id='auto-diametro-objetivo', type='number', min=0.1, step=0.01, value=1.75),
                ],
                className='campo_auto',
            ),
        ]

    elif fase_activa == 1:
        controles = [
            html.H4("Temperatura del calefactor"),
            dcc.Slider(
                id='auto-temperatura',
                min=100,
                max=400,
                step=1,
                value=200,
                marks={
                    100: '100°C',
                    180: '180°C',
                    220: '220°C',
                    250: '250°C',
                    360: '360°C',
                    400: '400°C',
                },
                included=False,
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            html.Div(
                [
                    html.Button("ON", id='auto-aplicar-temperatura', n_clicks=0, className='btn-on'),
                    html.Button("OFF", id='auto-apagar-temperatura', n_clicks=0, className='btn-off'),
                ],
                className='contenedor-botones',
            ),
        ]

    elif fase_activa == 2:
        controles = [
            html.H4("Guiado del filamento"),
            html.Div(
                [
                    html.Label("Modo de guiado"),
                    dcc.Dropdown(
                        id='auto-modo-guiado',
                        options=[
                            {'label': 'Manual asistido', 'value': 'manual_asistido'},
                        ],
                        value='manual_asistido',
                        clearable=False,
                    ),
                ],
                className='campo_auto',
            ),
        ]

    elif fase_activa == 3:
        controles = [
            html.H4("Extrusion"),
            html.Div(
                [
                    html.Div(id='auto-tiempo-restante', children='Tiempo restante: 00:00'),
                ],
                className='contenedor-botones',
            ),
        ]

    else:
        controles = [
            html.H4("Finalización del proceso"),
            dcc.Checklist(
                id='auto-finalizacion-checklist',
                options=[
                    {'label': 'Apagar calefactor', 'value': 'calefactor'},
                    {'label': 'Detener motores', 'value': 'motores'},
                    {'label': 'Desactivar láser', 'value': 'laser'},
                ],
                value=['calefactor', 'motores', 'laser'],
            ),
            html.Div(
                [
                    html.Button("Finalizar proceso", id='auto-finalizar-proceso', n_clicks=0, className='btn-off'),
                ],
                className='contenedor-botones',
            ),
        ]

    return html.Div(
        [
            html.H3(f"Fase {fase_activa + 1}: {fase['titulo']}"),
            html.P(fase['descripcion']),
            html.Div(controles, className='controles_fase_auto'),
        ],
        className='contenedor_fase_auto',
    )

# Función para crear el layout de automático
def automatico():
    """
    Descripción:
        Crea el layout para la sección de operación automática, que incluye indicadores de fase y contenido específico para cada fase del proceso.
    
    Parámetros:
        - Ninguno.

    Retorno:
        - html.Div: Componente de Dash con el layout de la operación automática.
    """
    return html.Div(
        className='contenedor_fases',
        children=[
            dcc.Store(id='store-fase-automatica', data=0),

            html.Div(
                id='indicadores-fases-auto',
                className='indicadores_fases_auto',
                children=crear_indicadores_fases(0),
            ),

            html.Div(
                id='contenedor-fase-auto',
                children=crear_contenido_fase_automatica(0),
            ),

            html.Div(
                [
                    html.Button(
                        "Anterior",
                        id='btn-fase-anterior',
                        n_clicks=0,
                        className='boton_menu',
                        style={'display': 'none'},
                    ),
                    html.Button(
                        "Siguiente",
                        id='btn-fase-siguiente',
                        n_clicks=0,
                        className='boton_menu',
                        style={'display': 'inline-block'},
                    ),
                ],
                className='navegacion_fases_auto',
            ),
        ]
    )


# Función para crear el layout de manual
def manual():
    """
    Descripción:
        Crea el layout para la sección de operación manual, que incluye controles para ajustar la temperatura y velocidad de la extrusora.
    
    Parámetros:
        - Ninguno.

    Retorno:
        - html.Div: Componente de Dash con el layout de la operación manual.
    """
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


#----------------------------#
# --- Layouts y Callbacks ---#
# ---------------------------#
app.layout = html.Div([
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
                        html.Span("0.00", id="diametro-display", className="display")
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

    html.Div([
        html.Div(id='seccion-monitoreo', children=monitoreo(), style={'display': 'block'}),
        html.Div(id='seccion-automatico', children=automatico(), style={'display': 'none'}),
        html.Div(id='seccion-manual', children=manual(), style={'display': 'none'}),
        html.Div(
            [
                html.P(f"[{datetime.now().strftime('%H:%M:%S')}] > Sistema iniciado..."),
            ],
            id='log-sistema',
            className='contenedor_log'),
    ],
    className='contenedor_contenido_menu'),

    dcc.Store(id='store-graficos', storage_type='memory'), 
    dcc.Store(id='store-estado-maquina', storage_type='memory'),
    dcc.Interval(id='intervalo-diametro', interval=100, n_intervals=0),
],
className='contenedor_principal')


# Callback para actualizar el display de diámetro y el gráfico en tiempo real
@app.callback(
    Output("diametro-display", "children"),
    Output("grafico-diametro", "figure"),
    Input("intervalo-diametro", "n_intervals"),
    prevent_initial_call=False
)
def actualizar_diametro_display(n):
    valor_diametro = camara.diametro_mm

    if valor_diametro is None:
        valor_diametro = 0.0

    diametros.append(valor_diametro)
    tiempos.append(n * 0.1)

    max_puntos = 100
    if len(diametros) > max_puntos:
        del diametros[:-max_puntos]
        del tiempos[:-max_puntos]

    figura = crear_figura_lineas(
        'Diámetro en tiempo real',
        'Tiempo (s)',
        'Diámetro (mm)',
        [('Diámetro', tiempos, diametros)],
    )

    return f"{valor_diametro:.2f}", figura


# CALLBACK FASES AUTOMÁTICAS
@callback(
    Output('store-fase-automatica', 'data'),
    Input('btn-fase-anterior', 'n_clicks'),
    Input('btn-fase-siguiente', 'n_clicks'),
    State('store-fase-automatica', 'data'),
    prevent_initial_call=True
)
def cambiar_fase_automatica(n_anterior, n_siguiente, fase_actual):
    if fase_actual is None:
        fase_actual = 0

    id_disparador = ctx.triggered_id

    if id_disparador == 'btn-fase-anterior':
        return max(fase_actual - 1, 0)

    if id_disparador == 'btn-fase-siguiente':
        return min(fase_actual + 1, len(FASES_AUTOMATICAS) - 1)

    return fase_actual


@callback(
    Output('indicadores-fases-auto', 'children'),
    Output('contenedor-fase-auto', 'children'),
    Output('btn-fase-anterior', 'style'),
    Output('btn-fase-siguiente', 'style'),
    Input('store-fase-automatica', 'data')
)
def actualizar_fase_automatica(fase_activa):
    if fase_activa is None:
        fase_activa = 0

    fase_activa = max(0, min(fase_activa, len(FASES_AUTOMATICAS) - 1))

    estilo_boton_visible = {'display': 'inline-block'}
    estilo_boton_oculto = {'display': 'none'}

    return (
        crear_indicadores_fases(fase_activa),
        crear_contenido_fase_automatica(fase_activa),
        estilo_boton_oculto if fase_activa == 0 else estilo_boton_visible,
        estilo_boton_oculto if fase_activa == len(FASES_AUTOMATICAS) - 1 else estilo_boton_visible,
    )


# CALLBACK MENU LATERAL
@callback(
    Output('seccion-monitoreo', 'style'),
    Output('seccion-automatico', 'style'),
    Output('seccion-manual', 'style'),
    Output('log-sistema', 'children'),
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

    estilo_visible = {'display': 'block'}
    estilo_oculto = {'display': 'none'}

    if id_disparador == 'btn-monitoreo':
        msg = "Sección: Monitoreo cargada."
        estilos = (estilo_visible, estilo_oculto, estilo_oculto)

    elif id_disparador == 'btn-automatico':
        if can_com.bus is not None and not can_com.modo_simulado:
            can_com.enviar_mensaje(0x201, "AUTO")
            respuesta = can_com.get_mensaje()
            exito = respuesta and respuesta[1] == "OK"
            msg = f"Sección: Automático cargada. {'Modo automático activado en uC.' if exito else 'Error al activar modo automático en uC.'}"
        else:
            msg = "Sección: Automático cargada."

        estilos = (estilo_oculto, estilo_visible, estilo_oculto)

    elif id_disparador == 'btn-manual':
        if can_com.bus is not None and not can_com.modo_simulado:
            can_com.enviar_mensaje(0x202, "MANUAL")
            respuesta = can_com.get_mensaje()
            exito = respuesta and respuesta[1] == "OK"
            msg = f"Sección: Manual cargada. {'Modo manual activado en uC.' if exito else 'Error al activar modo manual en uC.'}"
        else:
            msg = "Sección: Manual cargada. Modo SIMULADO activo, no se envió comando al uC."

        estilos = (estilo_oculto, estilo_oculto, estilo_visible)

    else:
        return no_update, no_update, no_update, no_update

    logs_actuales.append(html.P(f"[{hora}] > {msg}"))
    return estilos[0], estilos[1], estilos[2], logs_actuales


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

    calefactor_estado = no_update
    motor_extrusora_estado = no_update
    motor_enrolladora_estado = no_update
    laser_estado = no_update

    # --- LÓGICA DE CALEFACTOR ---
    if id_disparador == "temperatura-on" and n_on1:
        if can_com.bus is None and not can_com.modo_simulado:
            logs_actuales.append(html.P(f"[{hora}] > Error: Comunicación CAN no disponible. No se puede encender el calefactor."))

        else:
            can_com.enviar_mensaje(0x100, f"C_ON{slider_temp}")
            respuesta = can_com.get_mensaje()
            exito = respuesta and respuesta[1] == "OK"
            logs_actuales.append(html.P(f"[{hora}] > {'Encendiendo' if exito else 'Error'} Calefactor"))
            calefactor_estado = [html.Label("Calefactor"), html.Div(className='led-on' if exito else 'led-off')]
        
        return logs_actuales, calefactor_estado, no_update, no_update, no_update


    elif id_disparador == "temperatura-off" and n_off1:
        if can_com.bus is None and not can_com.modo_simulado:
            logs_actuales.append(html.P(f"[{hora}] > Error: Comunicación CAN no disponible. No se puede apagar el calefactor."))

        else:
            can_com.enviar_mensaje(0x100, "C_OFF")
            respuesta = can_com.get_mensaje()
            exito = respuesta and respuesta[1] == "OK"
            logs_actuales.append(html.P(f"[{hora}] > {'Apagando' if exito else 'Error'} Calefactor"))
            calefactor_estado = [html.Label("Calefactor"), html.Div(className='led-off' if exito else 'led-on')]
        
        return logs_actuales, calefactor_estado, no_update, no_update, no_update


    # --- LÓGICA DE EXTRUSORA ---
    elif id_disparador == "velocidad-extrusora-on" and n_on2:
        if can_com.bus is None and not can_com.modo_simulado:
            logs_actuales.append(html.P(f"[{hora}] > Error: Comunicación CAN no disponible. No se puede encender el motor de extrusora."))

        else:
            can_com.enviar_mensaje(0x101, f"EX_ON{slider_vel_extr}")
            respuesta = can_com.get_mensaje()
            exito = respuesta and respuesta[1] == "OK"
            logs_actuales.append(html.P(f"[{hora}] > {'Encendiendo' if exito else 'Error'} Motor Extrusora"))
            motor_extrusora_estado = [html.Label("Motor Extrusora"), html.Div(className='led-on' if exito else 'led-off')]
        
        return logs_actuales, no_update, motor_extrusora_estado, no_update, no_update


    elif id_disparador == "velocidad-extrusora-off" and n_off2:
        if can_com.bus is None and not can_com.modo_simulado:
            logs_actuales.append(html.P(f"[{hora}] > Error: Comunicación CAN no disponible. No se puede apagar el motor de extrusora."))

        else:
            can_com.enviar_mensaje(0x101, "EX_OFF")
            respuesta = can_com.get_mensaje()
            exito = respuesta and respuesta[1] == "OK"
            logs_actuales.append(html.P(f"[{hora}] > {'Apagando' if exito else 'Error'} Motor Extrusora"))
            motor_extrusora_estado = [html.Label("Motor Extrusora"), html.Div(className='led-off' if exito else 'led-on')]

        return logs_actuales, no_update, motor_extrusora_estado, no_update, no_update


    # --- LÓGICA DE ENROLLADORA ---
    elif id_disparador == "velocidad-enrolladora-on" and n_on3:
        if can_com.bus is None and not can_com.modo_simulado:
            logs_actuales.append(html.P(f"[{hora}] > Error: Comunicación CAN no disponible. No se puede encender el motor de enrolladora."))

        else:
            can_com.enviar_mensaje(0x102, f"EN_ON{slider_vel_enroll}")
            respuesta = can_com.get_mensaje()
            exito = respuesta and respuesta[1] == "OK"
            logs_actuales.append(html.P(f"[{hora}] > {'Encendiendo' if exito else 'Error'} Motor Enrolladora"))
            motor_enrolladora_estado = [html.Label("Motor Enrolladora"), html.Div(className='led-on' if exito else 'led-off')]
        
        return logs_actuales, no_update, no_update, motor_enrolladora_estado, no_update
        

    elif id_disparador == "velocidad-enrolladora-off" and n_off3:
        if can_com.bus is None and not can_com.modo_simulado:
            logs_actuales.append(html.P(f"[{hora}] > Error: Comunicación CAN no disponible. No se puede apagar el motor de enrolladora."))
        
        else:
            can_com.enviar_mensaje(0x102, "EN_OFF")
            respuesta = can_com.get_mensaje()
            exito = respuesta and respuesta[1] == "OK"
            logs_actuales.append(html.P(f"[{hora}] > {'Apagando' if exito else 'Error'} Motor Enrolladora"))
            motor_enrolladora_estado = [html.Label("Motor Enrolladora"), html.Div(className='led-off' if exito else 'led-on')]
        
        return logs_actuales, no_update, no_update, motor_enrolladora_estado, no_update
    

    # --- LÓGICA DE LÁSER ---
    elif id_disparador == "laser-on" and n_on4:
        laser.on()
        logs_actuales.append(html.P(f"[{hora}] > Encendiendo Láser"))
        laser_estado = [html.Label("Láser"), html.Div(className='led-on')]

    elif id_disparador == "laser-off" and n_off4:
        laser.off()
        logs_actuales.append(html.P(f"[{hora}] > Apagando Láser"))
        laser_estado = [html.Label("Láser"), html.Div(className='led-off')]

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


# Callback para parada de emergencia: apaga todo y actualiza estados
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
    exito = False

    if id_disparador == 'btn-parada' and n_clicks:
        if can_com.bus is None and not can_com.modo_simulado:
            logs_actuales.append(html.P(f"[{hora}] > Error: Comunicación CAN no disponible. No se puede activar la parada de emergencia."))
        
        else:
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