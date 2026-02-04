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
    ])
]


# CALLBACKS
@callback(
    Output('tab_content', 'children'),
    Input('system-tabs', 'value')
)
def render_tab_content(tab):
    if tab == 'monitoring':
        return html.Div('Contenido de Monitoreo')
    
    elif tab == 'automatic':
        return html.Div('Contenido de Automático')
    
    elif tab == 'manual':
        return html.Div('Contenido de Manual')
    
    elif tab == 'alarms_history':
        return html.Div('Contenido de Alarmas/Historial')
    
    elif tab == 'settings':
        return html.Div('Contenido de Configuración')
    
    return html.Div('Seleccione una pestaña válida')


# MAIN
if __name__ == '__main__':
    app.run(debug=True)