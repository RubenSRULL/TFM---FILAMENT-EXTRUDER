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
        dcc.Store(id='store_configuracion', storage_type='session'),
        dcc.Tabs(id='system-tabs',value='system_tab', children=[
            dcc.Tab(label='Monitoreo', value='monitoring'),
            dcc.Tab(label='Automático', value='automatic'),
            dcc.Tab(label='Manual', value='manual'),
            dcc.Tab(label='Alarmas/Historial', value='alarms_history'),
            dcc.Tab(label='Configuración', value='settings')
        ]
    ),
    html.Div(id='tab_content', className='render_tab')
    ], className='app-container')
]


# MONITOREO LAYOUT
def monitoring_layout():
    return html.Div('Contenido de Monitoreo', className='card')


# MODO AUTOMATICO LAYOUT
def automatic_layout():
    return html.Div('Contenido de Automático', className='card')


# MODO MANUAL LAYOUT
def manual_layout():
    return html.Div('Contenido de Manual', className='card')


# ALARMAS/HISTORIAL LAYOUT
def alarms_history_layout():
    return html.Div('Contenido de Alarmas/Historial', className='card')


# CONFIGURACIÓN LAYOUT
def settings_layout():
    return html.Div('Contenido de Configuración', className='card')


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
    
    elif tab == 'settings':
        layout = settings_layout()
        return layout
    
    return html.Div('Seleccione una pestaña válida')


# MAIN
if __name__ == '__main__':
    app.run(debug=True)