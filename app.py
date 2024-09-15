import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE,dbc.icons.FONT_AWESOME])
server = app.server
app.scripts.config.server_locally = True
server = app.server