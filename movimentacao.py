import pandas as pd
import dash
from dash import html,dcc,dash_table
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash.dependencies import Input, Output,State
from dash import dcc
import plotly.graph_objects as go
import dash_mantine_components as dmc
import warnings
import os

from jinja2 import Environment, FileSystemLoader
import pdfkit
import uuid

warnings.filterwarnings("ignore")
from app import app


db_prescricao = pd.read_excel('Dados\Movimentacao_2024.xlsx',nrows=5000)

df_prescricao = db_prescricao.copy()
df_prescricao['Data do ultimo movimento'] = pd.to_datetime(df_prescricao['Data do ultimo movimento']).dt.strftime('%d/%m/%Y %H:%M:%S')
cols_selecionadas_tabela = ['Número do processo','Localização','Data do ultimo movimento','Dias sem movimentação','Instância','Movimento realizado','Tarefa realizada','Serventia Descrição Resumida','Magistrado','Classe Judicial','Preferência Legal']

colunasFormatadas = [
    {"headerName": "Nº Processo","field": "Número do processo",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Seção judiciária","field": "Localização",'cellStyle': {'textAlign': 'center'}, "filterParams": { "buttons": ["reset", "apply"]}},
    {"headerName": "Vara","field": "Serventia Descrição Resumida",'cellStyle': {'textAlign': 'center'}, "filterParams": { "buttons": ["reset", "apply"]}},
    {"headerName": "Data do ultimo movimento","field": "Data do ultimo movimento",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Dias sem movimentação","field": "Dias sem movimentação",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Movimento realizado","field": "Movimento realizado",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Tarefa realizada","field": "Tarefa realizada",'cellStyle': {'textAlign': 'center'}},
    {"headerName": "Magistrado","field": "Magistrado"},
    {"headerName": "Classe Judicial","field": "Classe Judicial"}
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

processos_menos_1 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 30) & (df_prescricao['Dias sem movimentação'] <= 59)]['Número do processo'].unique())
processos_menos_2 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 60) & (df_prescricao['Dias sem movimentação'] <= 99)]['Número do processo'].unique())
processos_menos_3 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 100)]['Número do processo'].unique())

percent_menos_1 = processos_menos_1/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
percent_menos_2 = processos_menos_2/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
percent_menos_3 = processos_menos_3/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())

df_store = df_prescricao.to_dict()

def generate_pdf(sj,varas,assuntos,dataframe,processos,periodo):
    # Carregar o template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('templateMov.html')
    
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
                            html.H4('Tempo de movimentação',style={'width':'100%','background-color':'#325d88','color':'white','text-align':'left','font-size':'35px'},id='card_12')
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
                            dcc.Dropdown(df_prescricao['Localização'].unique(),df_prescricao['Localização'].unique(),multi=True,persistence=True,placeholder='Digite a seção', optionHeight=20,style={'color':'black'},id='dropdown_sj'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_sj',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Vara', id='filter_vara',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_vara',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['Serventia Descrição Resumida'].unique(),df_prescricao['Serventia Descrição Resumida'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=20,style={'color':'black'},id='dropdown_vara'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_vara',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Movimento', id='filter_assunto',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_assunto',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['Movimento realizado'].unique(),df_prescricao['Movimento realizado'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=60,style={'color':'black'},id='dropdown_assunto'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_assunto',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Magistrado', id='filter_magistrado',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_magistrado',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['Magistrado'].unique(),df_prescricao['Magistrado'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=60,style={'color':'black'},id='dropdown_magistrado'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_magistrado',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Tarefa', id='filter_tarefa',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_tarefa',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['Tarefa realizada'].unique(),df_prescricao['Tarefa realizada'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=50,style={'color':'black'},id='dropdown_tarefa'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_tarefa',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Classe', id='filter_sobrestado',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_sobrestado',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_prescricao['Classe Judicial'].unique(),df_prescricao['Classe Judicial'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=50,style={'color':'black'},id='dropdown_sobrestado'),
                            
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
                        dbc.CardHeader('De 30 até 59 dias sem movimento', style={'color':'white','width':'100%','background-color':'#1baae2'}),
                        dbc.CardBody([
                            html.H4(processos_menos_1,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_1'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_1 * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_1')
                        ])
                    ],style={'background-color':'white'}),
                ],width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('De 60 até 99 dias sem movimento', style={'color':'white','width':'100%','background-color':'#f67c31'}),
                        dbc.CardBody([
                            html.H4(processos_menos_2,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_2'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_2 * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_2')
                        ]),
                    ],style={'background-color':'white'}),
                ],width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Mais de 100 dias sem movimento', style={'color':'white','width':'100%','background-color':'#db524b'}),
                        dbc.CardBody([
                            html.H4(processos_menos_3,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_3'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_3 * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_3')
                        ]),
                    ],style={'background-color':'white'}),
                ],width=4),
            ],style={'padding-left':'35px','padding-right':'35px','padding-top':'35px'}), 
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
    dataFiltred = pd.DataFrame(data).drop_duplicates('Número do processo')
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
            return df_prescricao['Localização'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_sj':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['Localização'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['Localização'].unique(), ['ALL']


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
            return df_prescricao['Serventia Descrição Resumida'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_vara':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['Serventia Descrição Resumida'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['Serventia Descrição Resumida'].unique(), ['ALL']
    

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
            return df_prescricao['Movimento realizado'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_assunto':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['Movimento realizado'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['Movimento realizado'].unique(), ['ALL']


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
            return df_prescricao['Magistrado'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_magistrado':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['Magistrado'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['Magistrado'].unique(), ['ALL']


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
            return df_prescricao['Tarefa realizada'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_tarefa':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['Tarefa realizada'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['Tarefa realizada'].unique(), ['ALL']


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
            return df_prescricao['Classe Judicial'].unique(), ['ALL']
        else:
            return [],[]
    elif triggered_id == 'dropdown_sobrestado':
        if dropdown_value and set(dropdown_value) == set(df_prescricao['Classe Judicial'].unique()):
            return dropdown_value, ['ALL']
        else:
            return dropdown_value, []
    else:
        return df_prescricao['Classe Judicial'].unique(), ['ALL']


@app.callback(
    [Output("filter-model-grid2", "rowData"),
    Output("card_1", "children"),
    Output("card_2", "children"),
    Output("card_3", "children"),
    Output("span_1", "children"),
    Output("span_2", "children"),
    Output("span_3", "children")],
    [Input("aplicar_filtro", "n_clicks"),
    Input("limpar_filtro", "n_clicks")],
    [State('dropdown_sj', 'value'),
    State('dropdown_vara', 'value'),
    State('dropdown_assunto', 'value'),
    State('dropdown_magistrado', 'value'),
    State('dropdown_tarefa', 'value'),
    State('dropdown_sobrestado', 'value')]
)
def toggle_collapse(n1,n2,sj,vr,ass,mag,tar,sobr):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'aplicar_filtro' and n1:
        df_prescricao = db_prescricao[(db_prescricao['Localização'].isin(sj)) & (db_prescricao['Serventia Descrição Resumida'].isin(vr)) & (db_prescricao['Movimento realizado'].isin(ass) & (db_prescricao['Magistrado'].isin(mag)& (db_prescricao['Tarefa realizada'].isin(tar)) & (db_prescricao['Classe Judicial'].isin(sobr))))]
        df_prescricao['Data do ultimo movimento'] = pd.to_datetime(df_prescricao['Data do ultimo movimento']).dt.strftime('%d/%m/%Y %H:%M:%S')
        menos_1 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 30) & (df_prescricao['Dias sem movimentação'] <= 59)]['Número do processo'].unique())
        menos_2 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 60) & (df_prescricao['Dias sem movimentação'] <= 99)]['Número do processo'].unique())
        menos_3 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 100)]['Número do processo'].unique())
        
        percent_1 = menos_1/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        percent_2 = menos_2/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        percent_3 = menos_3/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        
        return df_prescricao[cols_selecionadas_tabela].to_dict('records'), menos_1,menos_2,menos_3,'{0:.2f}% dos processos'.format(percent_1 * 100),'{0:.2f}% dos processos'.format(percent_2 * 100),'{0:.2f}% dos processos'.format(percent_3 * 100)

    elif button_id == 'limpar_filtro' and n2:
        df_prescricao = db_prescricao.copy()
        df_prescricao['Data do ultimo movimento'] = pd.to_datetime(df_prescricao['Data do ultimo movimento']).dt.strftime('%d/%m/%Y %H:%M:%S')
        menos_1 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 30) & (df_prescricao['Dias sem movimentação'] <= 59)]['Número do processo'].unique())
        menos_2 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 60) & (df_prescricao['Dias sem movimentação'] <= 99)]['Número do processo'].unique())
        menos_3 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 100)]['Número do processo'].unique())
        
        percent_1 = menos_1/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        percent_2 = menos_2/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        percent_3 = menos_3/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        
        return df_prescricao[cols_selecionadas_tabela].to_dict('records'), menos_1,menos_2,menos_3,'{0:.2f}% dos processos'.format(percent_1 * 100),'{0:.2f}% dos processos'.format(percent_2 * 100),'{0:.2f}% dos processos'.format(percent_3 * 100)
    else:
        df_prescricao = db_prescricao[(db_prescricao['Localização'].isin(sj)) & (db_prescricao['Serventia Descrição Resumida'].isin(vr)) & (db_prescricao['Movimento realizado'].isin(ass) & (db_prescricao['Magistrado'].isin(mag)& (db_prescricao['Tarefa realizada'].isin(tar)) & (db_prescricao['Classe Judicial'].isin(sobr))))]
        df_prescricao['Data do ultimo movimento'] = pd.to_datetime(df_prescricao['Data do ultimo movimento']).dt.strftime('%d/%m/%Y %H:%M:%S')
        menos_1 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 30) & (df_prescricao['Dias sem movimentação'] <= 59)]['Número do processo'].unique())
        menos_2 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 60) & (df_prescricao['Dias sem movimentação'] <= 99)]['Número do processo'].unique())
        menos_3 = len(df_prescricao[(df_prescricao['Dias sem movimentação'] >= 100)]['Número do processo'].unique())
        
        percent_1 = menos_1/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        percent_2 = menos_2/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        percent_3 = menos_3/len(df_prescricao[df_prescricao['Dias sem movimentação'] > 0]['Número do processo'].unique())
        
        return df_prescricao[cols_selecionadas_tabela].to_dict('records'), menos_1,menos_2,menos_3,'{0:.2f}% dos processos'.format(percent_1 * 100),'{0:.2f}% dos processos'.format(percent_2 * 100),'{0:.2f}% dos processos'.format(percent_3 * 100)

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
     State('dropdown_sobrestado','value'),
     State('filter-model-grid2','virtualRowData')],
    prevent_initial_call=True
)

def generate_pdf_callback(n_clicks,sj,vara,assunto,processos):
    if n_clicks:
        
        df = pd.DataFrame(processos)
        df = df.sort_values(['Dias sem movimentação','Localização','Número do processo'],ascending=False)
        #df.columns = ['Nº PROCESSOS','SEÇÃO JUDICIÁRIA','DATA DE INICIO','DATA DE PRESCRIÇÃO','DIAS FALTANTES PARA PRESCRIÇÃO','ULTIMO MOVIMENTO','MAGISTRADO','ASSUNTO']
        # Gerar o PDF com nome único
        dataFiltred = df.drop_duplicates('Número do processo')
        total_rows = len(dataFiltred)
        dataMax = df['Dias sem movimentação'].max()
        dataMin = df['Dias sem movimentação'].min()
        filename = generate_pdf(sj,vara,assunto,df,total_rows,'De '+str(dataMin)+' até '+str(dataMax)+' dias sem movimento')

        # Lê o arquivo PDF gerado e o retorna como um objeto de bytes
        with open(filename, 'rb') as f:
            pdf_data = f.read()

        # Remove o arquivo temporário após a leitura
        os.remove(filename)

        return dcc.send_bytes(pdf_data, filename)

if __name__ == '__main__':
    app.run_server(debug=True, port='8051')
    #app.run_server(host='0.0.0.0', port='8050')