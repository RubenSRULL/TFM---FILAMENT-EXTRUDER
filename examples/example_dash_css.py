from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Guía Maestra de Posicionamiento", style={'textAlign': 'center', 'marginBottom': '40px'}),

    # --- 1. MOVER A LA DERECHA (Usando Margen) ---
    html.Div([
        html.H3("1. Empujar a la derecha (marginLeft: auto)"),
        html.Div("Me movieron a la derecha", style={
            'width': '250px',
            'marginLeft': 'auto', # <--- El truco
            'backgroundColor': '#ffcccb',
            'padding': '15px',
            'fontWeight': 'bold'
        })
    ], style={'borderBottom': '1px solid #ddd', 'padding': '20px'}),

    # --- 2. CENTRADO TOTAL (Flexbox) ---
    html.Div([
        html.H3("2. Centrado Horizontal y Vertical (Flexbox)"),
        html.Div([
            html.Div("Centro Perfecto", style={
                'backgroundColor': '#b3e5fc',
                'padding': '20px',
                'width': '150px',
                'textAlign': 'center'
            })
        ], style={
            'display': 'flex',
            'justifyContent': 'center', # Centra horizontal
            'alignItems': 'center',     # Centra vertical
            'height': '150px',          # Altura necesaria para ver el centrado vertical
            'backgroundColor': '#f5f5f5'
        })
    ], style={'borderBottom': '1px solid #ddd', 'padding': '20px'}),

    # --- 3. MOVER ARRIBA / ABAJO (Relative) ---
    html.Div([
        html.H3("3. Ajuste fino (Relative: top/bottom)"),
        html.Div([
            html.Div("Subir 10px", style={
                'position': 'relative',
                'top': '-10px', # Números negativos suben
                'backgroundColor': '#c8e6c9',
                'display': 'inline-block',
                'padding': '10px',
                'marginRight': '20px'
            }),
            html.Div("Bajar 20px", style={
                'position': 'relative',
                'top': '20px', # Números positivos bajan
                'backgroundColor': '#fff9c4',
                'display': 'inline-block',
                'padding': '10px'
            }),
        ], style={'height': '80px'})
    ], style={'borderBottom': '1px solid #ddd', 'padding': '20px'}),

    # --- 4. LAS 4 ESQUINAS (Absolute) ---
    html.Div([
        html.H3("4. Posicionamiento en Esquinas (Absolute)"),
        html.Div([
            html.Div("Top-Left", style={'position': 'absolute', 'top': '0', 'left': '0', 'backgroundColor': '#e1bee7'}),
            html.Div("Top-Right", style={'position': 'absolute', 'top': '0', 'right': '0', 'backgroundColor': '#e1bee7'}),
            html.Div("Bottom-Left", style={'position': 'absolute', 'bottom': '0', 'left': '0', 'backgroundColor': '#e1bee7'}),
            html.Div("Bottom-Right", style={'position': 'absolute', 'bottom': '0', 'right': '0', 'backgroundColor': '#e1bee7'}),
            html.P("El contenedor padre es mi límite.", style={'textAlign': 'center', 'paddingTop': '40px'})
        ], style={
            'position': 'relative', # OBLIGATORIO para que el Absolute no se escape a la pantalla
            'height': '120px',
            'backgroundColor': '#fafafa',
            'border': '1px dashed #999'
        })
    ], style={'padding': '20px'})

], style={'fontFamily': 'sans-serif', 'maxWidth': '800px', 'margin': 'auto'})

if __name__ == '__main__':
    app.run(debug=True)