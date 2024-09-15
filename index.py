import pandas as pd
import dash
from dash import html,dcc,dash_table
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash.dependencies import Input, Output,State
from dash import dcc
import plotly.graph_objects as go
import dash_mantine_components as dmc
import plotly.express as px
import warnings
import os

from jinja2 import Environment, FileSystemLoader
import pdfkit
import uuid

warnings.filterwarnings("ignore")
from app import app


db_prescricao = pd.read_excel('Dados\Prescricao_2024.xlsx')
db_prescricao.columns = ['sistema', 'instancia',
       '%ID_PROCESSO_TRF_PRESCRICAO', 'secao_judiciaria',
       'classe_judicial', 'numero_processo',
       'data_inicio_processo', 'data_entrada_processo',
       'data_1_distribuicao', 'flag_pendente',
       'flag_sobrestado', 'serventia',
       'flag_baixado_julgado', 'movimento',
       'cpf_magistardo', 'cnj_magistrado',
       'magistrado', 'assunto', 'tarefa']

def dataPosLei(data):
    if data['data_inicio_processo'] < pd.to_datetime('2021-10-26'):
        return pd.to_datetime('2021-10-26') + pd.DateOffset(months=48)
    else:
        return data['data_inicio_processo'] + pd.DateOffset(months=48)
    
db_prescricao['data_prescricao_lei'] = db_prescricao.apply(dataPosLei, axis=1)
db_prescricao['dias_faltantes_prescricao'] = ""

for index,row in db_prescricao.iterrows():
    db_prescricao['dias_faltantes_prescricao'][index] = (row['data_prescricao_lei'] - pd.Timestamp.now()).days


df_prescricao = db_prescricao.copy()
df_prescricao['data_inicio_processo'] = pd.to_datetime(df_prescricao['data_inicio_processo']).dt.strftime('%d/%m/%Y %H:%M:%S')
df_prescricao['data_prescricao_lei'] = pd.to_datetime(df_prescricao['data_prescricao_lei']).dt.strftime('%d/%m/%Y')
cols_selecionadas_tabela = ['numero_processo','secao_judiciaria','data_inicio_processo','data_prescricao_lei','dias_faltantes_prescricao','movimento','magistrado','assunto']

colunasFormatadas = [
    {"headerName": "Nº Processo","field": "numero_processo",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Seção judiciária","field": "secao_judiciaria",'cellStyle': {'textAlign': 'center'}, "filterParams": { "buttons": ["reset", "apply"]}},
    {"headerName": "Data de início do processo","field": "data_inicio_processo",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Data de prescrição","field": "data_prescricao_lei",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Dias restantes para prescrição","field": "dias_faltantes_prescricao",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Movimento","field": "movimento"},
    {"headerName": "Magistrado","field": "magistrado"},
    {"headerName": "Assunto","field": "assunto"},
]
traducao = {
    #Set Filter
      # for filter panel
      'page': 'Página',
      'more': 'mais',
      'to': 'para',
      'TO':'para',
      'of': 'de',
      'next': 'Próximo',
      'last': 'Último',
      'first': 'Primeiro',
      'previous': 'Anterior',
      'loadingOoo': 'Carregar',

      # for set filter
      'selectAll': 'Selecionar tudo',
      'searchOoo': 'Procurar',
      'blanks': 'Vazio',

      # for number filter and text filter
      'filterOoo': 'Filtrar',
      'applyFilter': 'Aplicar filtro',

      # for number filter
      'equals': 'Igual',
      'doesNotEqual': 'Não é Igual',
      'notEqual': 'Não é Igual',
      'notContains': 'Não contém',
      'lessThan': 'Menor que',
      'greaterThan': 'Maior que',
      'inRange': 'Entre',
      'blank': 'Em branco',
      'notBlank': 'Não é branco',
      'greaterThanOrEqual': 'Maior ou igual a',
      'lessThanOrEqual': 'Menor ou igual a',

      # for text filter
      'contains': 'Contém',
      'startsWith': 'Começa com',
      'endsWith': 'Termina com',

      # the header of the default group column
      'group': 'Grupo',

      # tool panel
      'columns': 'Colunas',
      'rowGroupColumns': 'Colunas do grupo de linhas',
      'rowGroupColumnsEmptyMessage': 'Colunas do grupo de linhas vazias',
      'valueColumns': 'Valores das colunas',
      'pivotMode': 'Modo pivô',
      'groups': 'Grupos',
      'values': 'Valores',
      'pivots': 'Pivôs',
      'valueColumnsEmptyMessage': 'Valores de colunas vazias',
      'pivotColumnsEmptyMessage': 'Pivôs de colunas vazias',
      'toolPanelButton': 'Botão de painel de ferramentas',

      # other
      'noRowsToShow': 'Não há registros para mostrar.',

      # enterprise menu
      'pinColumn': 'Pinar coluna',
      'valueAggregation': 'Agregar valor',
      'autosizeThiscolumn': 'Redimensionar esta coluna',
      'autosizeAllColumns': 'Redimensionar todas colunas',
      'groupBy': 'Agrupar por',
      'ungroupBy': 'Desagrupar por',
      'resetColumns': 'Resetar colunas',
      'expandAll': 'Expandir tudo',
      'collapseAll': 'Contrair tudo',
      'toolPanel': 'Painel de ferramentas',
      'export': 'Exportar',
      'csvExport': 'Exportar para CSV',
      'excelExport': 'Exportar para Excel',

      # enterprise menu pinning
      'pinLeft': 'Pinar <<',
      'pinRight': 'Pinar >>',
      'noPin': 'Sem pinagem',

      # enterprise menu aggregation and status panel
      'sum': 'Soma',
      'min': 'Mínimo',
      'max': 'Máximo',
      'first': 'Primeiro',
      'last': 'Último',
      'none': 'Nenhum',
      'count': 'Contagem',
      'average': 'Média',

      # standard menu
      'copy': 'Copiar',
      'copyWithHeaders': 'Copiar com cabeçalho',
      'ctrlC': 'Ctrl+C',
      'paste': 'Colar',
      'ctrlV': 'Ctrl+V',
      'from': 'De',
      'to': 'Para',

      'andCondition':'E',

      'orCondition': 'OU',
      'resetFilter' : 'Resetar Filtro'

}



processos_menos_1 = len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] <= 365]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
processos_menos_2 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 366) & (df_prescricao['dias_faltantes_prescricao'] <= 730)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
processos_menos_3 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 731) & (df_prescricao['dias_faltantes_prescricao'] <= 1095)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())

percent_menos_1 = processos_menos_1/len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] > 0]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
percent_menos_2 = processos_menos_2/len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] > 0]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
percent_menos_3 = processos_menos_3/len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] > 0]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())

df_store = df_prescricao.to_dict()

data = {
    'Categoria' : ['Processos'],
    'Com menos de 1 ano' : [percent_menos_1 * 100],
    'Entre 1 e 2 anos' : [percent_menos_2 * 100],
    'Entre 2 e 3 anos' : [percent_menos_3 * 100],
} 

color_map = {
    'Com menos de 1 ano': '#db524b',
    'Entre 1 e 2 anos': '#f67c31',
    'Entre 2 e 3 anos': '#1baae2'
}
dfGraph = pd.DataFrame(data)

df_long = dfGraph.melt(id_vars='Categoria', var_name='Periodo', value_name='Percentual')

fig = px.bar(df_long, x='Percentual', y='Categoria', color='Periodo',orientation='h', title='Percentual de processo por periodo',color_discrete_map=color_map)
fig.update_layout(height=260)
def generate_pdf(sj,varas,assuntos,dataframe,processos,periodo):
    # Carregar o template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    
    # Renderizar o template com dados
    html_out = template.render(sj=sj,varas=varas,assuntos=assuntos,dataframe=dataframe,processos=processos,periodo=periodo)

    # Nome único para o arquivo PDF
    filename = f'relatorio_{uuid.uuid4()}.pdf'

    # Converter HTML para PDF
    pdfkit.from_string(html_out, filename)

    return filename

def generate_table(dataframe):
    return dbc.Table.from_dataframe(dataframe, striped=True, bordered=True, hover=True)

app.layout = dmc.MantineProvider(
    children=[
        dbc.Container(
        children=[
            dbc.Row([
                dbc.Col([
                    html.Img(src=r'assets\TRF5_w.png',style={'width':'100%'})
                ],width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody(
                            html.H4('Prescrição em improbidade administrativa',style={'width':'100%','background-color':'#325d88','color':'white','text-align':'left','font-size':'35px'},id='card_12')
                        ),
                    ],style={'background-color':'#325d88','border-color':'#325d88'})
                ],width=8)
            ],style={'padding-left':'35px','padding-right':'35px','padding-top':'15 px','background-color':'#325d88'}),
            dbc.Row([
                dbc.Col([
                    dbc.Button('Seção Judiciária', id='filter_sj',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_sj',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['secao_judiciaria'].unique(),df_prescricao['secao_judiciaria'].unique(),multi=True,persistence=True,placeholder='Digite a seção', optionHeight=20,style={'color':'black'},id='dropdown_sj'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_sj',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Vara', id='filter_vara',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_vara',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['serventia'].unique(),df_prescricao['serventia'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=20,style={'color':'black'},id='dropdown_vara'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_vara',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Assunto', id='filter_assunto',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_assunto',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['assunto'].unique(),df_prescricao['assunto'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=60,style={'color':'black'},id='dropdown_assunto'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_assunto',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Magistrado', id='filter_magistrado',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_magistrado',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['magistrado'].unique(),df_prescricao['magistrado'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=60,style={'color':'black'},id='dropdown_magistrado'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_magistrado',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Tarefa', id='filter_tarefa',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_tarefa',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['tarefa'].unique(),df_prescricao['tarefa'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=50,style={'color':'black'},id='dropdown_tarefa'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_tarefa',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Sobrestado?', id='filter_sobrestado',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_sobrestado',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['flag_sobrestado'].unique(),df_prescricao['flag_sobrestado'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=50,style={'color':'black'},id='dropdown_sobrestado'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_sobrestado',is_open=False)
                ],width=2),
            ],style={'padding-left':'35px','padding-right':'35px','padding-top':'35px'}),
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                            html.I(className='fa-solid fa-filter'),  # Ícone Bootstrap Icons
                            '  FILTRAR'], 
                            id='aplicar_filtro',n_clicks=0,color='secondary',style={'width':'100%'})
                ],width=1),
                dbc.Col([
                    dbc.Button([
                            html.I(className='fa-solid fa-filter-circle-xmark'),  # Ícone Bootstrap Icons
                            '  LIMPAR'], 
                            id='limpar_filtro',n_clicks=0,color='secondary',style={'width':'100%'})
                ],width=1)
            ],style={'padding-left':'35px','padding-right':'35px','padding-top':'15px'}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Processos com menos de 1 ano para prescrição', style={'color':'white','width':'100%','background-color':'#db524b'}),
                        dbc.CardBody([
                            html.H4(processos_menos_1,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_1'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_1 * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_1')
                        ])
                    ],style={'background-color':'white'}),
                ],width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Processos entre 1 e 2 anos para prescrição', style={'color':'white','width':'100%','background-color':'#f67c31'}),
                        dbc.CardBody([
                            html.H4(processos_menos_2,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_2'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_2 * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_2')
                        ]),
                    ],style={'background-color':'white'}),
                ],width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Processos entre 2 e 3 anos para prescrição', style={'color':'white','width':'100%','background-color':'#1baae2'}),
                        dbc.CardBody([
                            html.H4(processos_menos_3,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_3'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_3 * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_3')
                        ]),
                    ],style={'background-color':'white'}),
                ],width=4),
            ],style={'padding-left':'35px','padding-right':'35px','padding-top':'35px'}), 
            dbc.Row([
                dcc.Graph(
                    id='stacked-bar-chart',
                    figure=fig
                )
            ],style={'padding-left':'35px','padding-right':'35px','padding-top':'15px'}),
            dbc.Row([
                dbc.Col([
                    dag.AgGrid(
                        id="filter-model-grid2",
                        columnSize="autoSize",
                        rowData= df_prescricao[cols_selecionadas_tabela].to_dict('records'),
                        columnDefs = colunasFormatadas,
                        defaultColDef={"filter": True, "sortable": True, "floatingFilter": True},
                        filterModel={'model': {'filterType': 'text', 'type': 'contains', 'filter': 'cel'}},
                        dashGridOptions={'localeText': traducao,'enableCellTextSelection': True, 'ensureDomOrder': True},
                        csvExportParams={'fileName': "Relatório_Red_Alert.csv"}
                    )
                ],width=12),
                dbc.Col([

                ])
        ],style={'padding-left':'35px','padding-right':'35px','padding-top':'25px'}),
            dbc.Row([
                dbc.Col([
                     html.H5("Processos encontrados: ",id='div_total_processos'),
                ],width=3),
                dbc.Col([

                ],width=7),
                dbc.Col([
                    dbc.Button('CSV', id='download_csv',n_clicks=0,color='primary',style={'width':'100%'})
                ]),
                dbc.Col([
                    dbc.Button('PDF', id='download_pdf',n_clicks=0,color='primary',style={'width':'100%'})
                ]),
                dcc.Download(id='download-pdf-dcc'),
                html.Div(id='pdf-content', style={'display': 'none'})
            ],style={'padding-left':'35px','padding-top':'15px','padding-right':'35px','padding-bottom':'25px'}),

        ],fluid=True,style={'background-color':'#f2f2f2'})
    ])
@app.callback(
    Output('div_total_processos', 'children'),
    [Input('filter-model-grid2', 'virtualRowData')]
)
def update_total_rows(data):
    dataFiltred = pd.DataFrame(data).drop_duplicates('numero_processo')
    total_rows = len(dataFiltred)
    return f"Total de processos: {total_rows}"

@app.callback(
    Output("collapse_sj", "is_open"),
    [Input("filter_sj", "n_clicks")],
    [State("collapse_sj", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse_vara", "is_open"),
    [Input("filter_vara", "n_clicks")],
    [State("collapse_vara", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse_assunto", "is_open"),
    [Input("filter_assunto", "n_clicks")],
    [State("collapse_assunto", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse_magistrado", "is_open"),
    [Input("filter_magistrado", "n_clicks")],
    [State("collapse_magistrado", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



@app.callback(
    Output("collapse_tarefa", "is_open"),
    [Input("filter_tarefa", "n_clicks")],
    [State("collapse_tarefa", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse_sobrestado", "is_open"),
    [Input("filter_sobrestado", "n_clicks")],
    [State("collapse_sobrestado", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output('dropdown_sj', 'value'),
    Output('select-all_sj', 'value'),
    Input('select-all_sj', 'value'),
    Input('dropdown_sj', 'value')
)
def update_dropdown_sj(select_all_value, dropdown_value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'select-all_sj':
        if 'ALL' in select_all_value:
            return df_prescricao['secao_judiciaria'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_sj':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['secao_judiciaria'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['secao_judiciaria'].unique(), ['ALL']


@app.callback(
    Output('dropdown_vara', 'value'),
    Output('select-all_vara', 'value'),
    Input('select-all_vara', 'value'),
    Input('dropdown_vara', 'value')
)
def update_dropdown_vara(select_all_value, dropdown_value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'select-all_vara':
        if 'ALL' in select_all_value:
            return df_prescricao['serventia'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_vara':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['serventia'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['serventia'].unique(), ['ALL']
    

@app.callback(
    Output('dropdown_assunto', 'value'),
    Output('select-all_assunto', 'value'),
    Input('select-all_assunto', 'value'),
    Input('dropdown_assunto', 'value')
)
def update_dropdown_assunto(select_all_value, dropdown_value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'select-all_assunto':
        if 'ALL' in select_all_value:
            return df_prescricao['assunto'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_assunto':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['assunto'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['assunto'].unique(), ['ALL']


@app.callback(
    Output('dropdown_magistrado', 'value'),
    Output('select-all_magistrado', 'value'),
    Input('select-all_magistrado', 'value'),
    Input('dropdown_magistrado', 'value')
)
def update_dropdown_magistrado(select_all_value, dropdown_value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'select-all_magistrado':
        if 'ALL' in select_all_value:
            return df_prescricao['magistrado'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_magistrado':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['magistrado'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['magistrado'].unique(), ['ALL']


@app.callback(
    Output('dropdown_tarefa', 'value'),
    Output('select-all_tarefa', 'value'),
    Input('select-all_tarefa', 'value'),
    Input('dropdown_tarefa', 'value')
)
def update_dropdown_tarefa(select_all_value, dropdown_value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'select-all_tarefa':
        if 'ALL' in select_all_value:
            return df_prescricao['tarefa'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_tarefa':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['tarefa'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['tarefa'].unique(), ['ALL']


@app.callback(
    Output('dropdown_sobrestado', 'value'),
    Output('select-all_sobrestado', 'value'),
    Input('select-all_sobrestado', 'value'),
    Input('dropdown_sobrestado', 'value')
)
def update_dropdown_tarefa(select_all_value, dropdown_value):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'select-all_sobrestado':
        if 'ALL' in select_all_value:
            return df_prescricao['flag_sobrestado'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_sobrestado':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['flag_sobrestado'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['flag_sobrestado'].unique(), ['ALL']


@app.callback(
    [Output("filter-model-grid2", "rowData"),
    Output("card_1", "children"),
    Output("card_2", "children"),
    Output("card_3", "children")],
    [Input("aplicar_filtro", "n_clicks"),
    Input("limpar_filtro", "n_clicks")],
    [State('dropdown_sj', 'value'),
    State('dropdown_vara', 'value'),
    State('dropdown_assunto', 'value'),
    State('dropdown_magistrado', 'value'),
    State('dropdown_tarefa', 'value'),]
)
def toggle_collapse(n1,n2,sj,vr,ass,mag,tar):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'aplicar_filtro' and n1:
        df_prescricao = db_prescricao[(db_prescricao['secao_judiciaria'].isin(sj)) & (db_prescricao['serventia'].isin(vr)) & (db_prescricao['assunto'].isin(ass) & (db_prescricao['magistrado'].isin(mag)& (db_prescricao['tarefa'].isin(tar))))]
        df_prescricao['data_inicio_processo'] = pd.to_datetime(df_prescricao['data_inicio_processo']).dt.strftime('%d/%m/%Y %H:%M:%S')
        df_prescricao['data_prescricao_lei'] = pd.to_datetime(df_prescricao['data_prescricao_lei']).dt.strftime('%d/%m/%Y')
        menos_1 = len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] <= 365]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        menos_2 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 366) & (df_prescricao['dias_faltantes_prescricao'] <= 730)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        menos_3 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 731) & (df_prescricao['dias_faltantes_prescricao'] <= 1095)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        return df_prescricao[cols_selecionadas_tabela].to_dict('records'), menos_1,menos_2,menos_3

    elif button_id == 'limpar_filtro' and n2:
        df_prescricao = db_prescricao.copy()
        df_prescricao['data_inicio_processo'] = pd.to_datetime(df_prescricao['data_inicio_processo']).dt.strftime('%d/%m/%Y %H:%M:%S')
        df_prescricao['data_prescricao_lei'] = pd.to_datetime(df_prescricao['data_prescricao_lei']).dt.strftime('%d/%m/%Y')
        menos_1 = len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] <= 365]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        menos_2 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 366) & (df_prescricao['dias_faltantes_prescricao'] <= 730)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        menos_3 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 731) & (df_prescricao['dias_faltantes_prescricao'] <= 1095)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        return df_prescricao[cols_selecionadas_tabela].to_dict('records'), menos_1,menos_2,menos_3
    else:
        df_prescricao = db_prescricao[(db_prescricao['secao_judiciaria'].isin(sj)) & (db_prescricao['serventia'].isin(vr)) & (db_prescricao['assunto'].isin(ass) & (db_prescricao['magistrado'].isin(mag)& (db_prescricao['tarefa'].isin(tar))))]
        df_prescricao['data_inicio_processo'] = pd.to_datetime(df_prescricao['data_inicio_processo']).dt.strftime('%d/%m/%Y %H:%M:%S')
        df_prescricao['data_prescricao_lei'] = pd.to_datetime(df_prescricao['data_prescricao_lei']).dt.strftime('%d/%m/%Y')
        menos_1 = len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] <= 365]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        menos_2 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 366) & (df_prescricao['dias_faltantes_prescricao'] <= 730)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        menos_3 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 731) & (df_prescricao['dias_faltantes_prescricao'] <= 1095)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
        return df_prescricao[cols_selecionadas_tabela].to_dict('records'), menos_1,menos_2,menos_3

@app.callback(
    Output("filter-model-grid2", "exportDataAsCsv"),
    Input("download_csv", "n_clicks"),
)
def export_data_as_csv(n_clicks):
    if n_clicks:
        return True
    return False
@app.callback(
    Output('download-pdf-dcc', 'data'),
    Input('download_pdf', 'n_clicks'),
    [State('dropdown_sj','value'),
     State('dropdown_vara','value'),
     State('dropdown_assunto','value'),
     State('filter-model-grid2','virtualRowData')],
    prevent_initial_call=True
)

def generate_pdf_callback(n_clicks,sj,vara,assunto,processos):
    if n_clicks:
        
        df = pd.DataFrame(processos)
        df.columns = ['Nº PROCESSOS','SEÇÃO JUDICIÁRIA','DATA DE INICIO','DATA DE PRESCRIÇÃO','DIAS FALTANTES PARA PRESCRIÇÃO','ULTIMO MOVIMENTO','MAGISTRADO','ASSUNTO']
        # Gerar o PDF com nome único
        dataFiltred = df.drop_duplicates('Nº PROCESSOS')
        total_rows = len(dataFiltred)
        dataMax = df['DIAS FALTANTES PARA PRESCRIÇÃO'].max()
        dataMin = df['DIAS FALTANTES PARA PRESCRIÇÃO'].min()
        filename = generate_pdf(sj,vara,assunto,df,total_rows,'De '+str(dataMin)+' até '+str(dataMax)+' dias para prescrição')

        # Lê o arquivo PDF gerado e o retorna como um objeto de bytes
        with open(filename, 'rb') as f:
            pdf_data = f.read()

        # Remove o arquivo temporário após a leitura
        os.remove(filename)

        return dcc.send_bytes(pdf_data, filename)

if __name__ == '__main__':
    app.run_server(debug=True, port='8051')
    #app.run_server(host='0.0.0.0', port='8050')