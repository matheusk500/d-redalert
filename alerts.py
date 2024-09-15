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

db_mov = pd.read_excel('Dados\Movimentacao_2024.xlsx',nrows=5000)
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

df_mov = db_mov.copy()
df_mov['Data do ultimo movimento'] = pd.to_datetime(df_mov['Data do ultimo movimento']).dt.strftime('%d/%m/%Y %H:%M:%S')

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

processos_menos_1_mov = len(df_mov[(df_mov['Dias sem movimentação'] >= 30) & (df_mov['Dias sem movimentação'] <= 59)]['Número do processo'].unique())
processos_menos_2_mov = len(df_mov[(df_mov['Dias sem movimentação'] >= 60) & (df_mov['Dias sem movimentação'] <= 99)]['Número do processo'].unique())
processos_menos_3_mov = len(df_mov[(df_mov['Dias sem movimentação'] >= 100)]['Número do processo'].unique())

percent_menos_1_mov = processos_menos_1_mov/len(df_mov[df_mov['Dias sem movimentação'] > 0]['Número do processo'].unique())
percent_menos_2_mov = processos_menos_2_mov/len(df_mov[df_mov['Dias sem movimentação'] > 0]['Número do processo'].unique())
percent_menos_3_mov = processos_menos_3_mov/len(df_mov[df_mov['Dias sem movimentação'] > 0]['Número do processo'].unique())


processos_menos_1 = len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] <= 365]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
processos_menos_2 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 366) & (df_prescricao['dias_faltantes_prescricao'] <= 730)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
processos_menos_3 = len(df_prescricao[(df_prescricao['dias_faltantes_prescricao'] >= 731) & (df_prescricao['dias_faltantes_prescricao'] <= 1095)]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())

percent_menos_1 = processos_menos_1/len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] > 0]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
percent_menos_2 = processos_menos_2/len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] > 0]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())
percent_menos_3 = processos_menos_3/len(df_prescricao[df_prescricao['dias_faltantes_prescricao'] > 0]['%ID_PROCESSO_TRF_PRESCRICAO'].unique())


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
                            html.H4('Tempo de movimentação',style={'width':'100%','background-color':'#325d88','color':'white','text-align':'left','font-size':'35px'},id='card_12_mov')
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
                            dcc.Dropdown(df_mov['Localização'].unique(),df_mov['Localização'].unique(),multi=True,persistence=True,placeholder='Digite a seção', optionHeight=20,style={'color':'black'},id='dropdown_sj'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_sj',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Vara', id='filter_vara',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_vara',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_mov['Serventia Descrição Resumida'].unique(),df_mov['Serventia Descrição Resumida'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=20,style={'color':'black'},id='dropdown_vara'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_vara',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Movimento', id='filter_assunto',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_assunto',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_mov['Movimento realizado'].unique(),df_mov['Movimento realizado'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=60,style={'color':'black'},id='dropdown_assunto'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_assunto',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Magistrado', id='filter_magistrado',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_magistrado',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_mov['Magistrado'].unique(),df_mov['Magistrado'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=60,style={'color':'black'},id='dropdown_magistrado'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_magistrado',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Tarefa', id='filter_tarefa',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_tarefa',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_mov['Tarefa realizada'].unique(),df_mov['Tarefa realizada'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=50,style={'color':'black'},id='dropdown_tarefa'),
                            
                        ],style={'background-color':'white'}),
                    id='collapse_tarefa',is_open=False)
                ],width=2),
                dbc.Col([
                    dbc.Button('Classe', id='filter_sobrestado',n_clicks=0,style={'width':'100%'}),
                    dbc.Collapse(
                        dbc.Col([
                            dcc.Checklist(id='select-all_sobrestado',options=[{'label': 'Selecionar todos', 'value': 'ALL'}]),
                            dcc.Dropdown(df_mov['Classe Judicial'].unique(),df_mov['Classe Judicial'].unique(),multi=True,persistence=True,placeholder='Digite a vara', optionHeight=50,style={'color':'black'},id='dropdown_sobrestado'),
                            
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
                            html.H4(processos_menos_1_mov,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_1_mov'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_1_mov * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_1_mov')
                        ])
                    ],style={'background-color':'white'}),
                ],width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('De 60 até 99 dias sem movimento', style={'color':'white','width':'100%','background-color':'#f67c31'}),
                        dbc.CardBody([
                            html.H4(processos_menos_2_mov,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_2_mov'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_2_mov * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_2_mov')
                        ]),
                    ],style={'background-color':'white'}),
                ],width=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader('Mais de 100 dias sem movimento', style={'color':'white','width':'100%','background-color':'#db524b'}),
                        dbc.CardBody([
                            html.H4(processos_menos_3_mov,style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'65px'},id='card_3_mov'),
                            html.Span('{0:.2f}% dos processos'.format(percent_menos_3_mov * 100),style={'width':'100%','background-color':'white','color':'#1a4476','text-align':'center','font-size':'16px'},id='span_3_mov')
                        ]),
                    ],style={'background-color':'white'}),
                ],width=4),
            ],style={'padding-left':'35px','padding-right':'35px','padding-top':'35px','padding-bottom':'35px'}), 
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
            ],style={'padding-left':'35px','padding-right':'35px','background-color':'#325d88'}),
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
            ],style={'padding-left':'35px','padding-right':'35px','padding-top':'35px','padding-bottom':'35px'}), 
                dbc.Col([
                ])
        ],fluid=True,style={'background-color':'#f2f2f2'})
    ])

if __name__ == '__main__':
    app.run_server(debug=True, port='8051')
    #app.run_server(host='0.0.0.0', port='8050')