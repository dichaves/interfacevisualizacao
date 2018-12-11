# myapp.py

# -*- coding: utf-8 -*-
from bokeh.layouts import column, row, layout, widgetbox, gridplot
from bokeh.models import Button, ColumnDataSource, FactorRange, Range1d, LinearColorMapper, ColorBar
from bokeh.models.widgets import RangeSlider, Select, MultiSelect
from bokeh.models.glyphs import VBar
from bokeh.transform import cumsum
from bokeh.core.properties import value
from bokeh.colors import RGB
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.palettes import Category20b, Category20c, Category10, RdYlBu3, PuRd
from glob import glob
import pandas
import numpy as np
import roman
import unidecode

# COLUNAS
_MES = 'MÊS'.decode('utf-8')
_ANOS = 'ANOS'
_GERES = 'GERES'
_MUNICIPIO = 'MUNICÍPIO'.decode('utf-8')
_INSTITUICAO = 'INSTITUIÇãO '.decode('utf-8')
_OCUPACAO_SOLICITANTE = 'OCUPAÇãO DO SOLICITANTE'.decode('utf-8')
_INSTITUICAO_TELECONSULTOR = 'INSTITUIÇÃO TELECONSULTOR'.decode('utf-8')
_OCUPACAO_TELECONSULTOR = 'OCUPAÇãO DO TELECONSULTOR'.decode('utf-8')
_ESPECIALIDADE_TELECONSULTOR = 'ESPECIALIDADE DO TELECONSULTOR'
_NATUREZA = 'NATUREZA'
_AREA_TELECONSULTORIA = 'AREA DE TELECONSULTORIA'
_ESPECIALIDADE_DUVIDA = 'ESPECIALIDADE DA DÚVIDA'.decode('utf-8')
_COLUNAS = [_GERES, _MUNICIPIO, _INSTITUICAO, _OCUPACAO_SOLICITANTE,
            _INSTITUICAO_TELECONSULTOR, _OCUPACAO_TELECONSULTOR, _ESPECIALIDADE_TELECONSULTOR,
            _NATUREZA, _AREA_TELECONSULTORIA, _ESPECIALIDADE_DUVIDA]

# EIXO Y
_FREQUENCIA = 'FREQUÊNCIA ABSOLUTA'.decode('utf-8')
_PORCENTAGEM = 'FREQUÊNCIA EM PORCENTAGEM'.decode('utf-8')

# TIPOS DE GRÁFICO
_BARRAS = 'DE BARRAS'
_LINHA = 'DE LINHA'
_SETORES = 'DE SETORES'
_POR_ANOS = 'POR ANOS'
_MAPA_CALOR = 'MAPA DE CALOR'
_FRACIONADO_ANO = 'FRACIONADO POR ANO'
_FRACIONADO_MES = 'FRACIONADO POR MÊS'.decode('utf-8')
_CORRELACAO = 'CORRELAÇÃO'.decode('utf-8')
_TIPOS_GRAFICO = [_BARRAS, _LINHA, _SETORES, _POR_ANOS, _MAPA_CALOR, _FRACIONADO_ANO,
                _FRACIONADO_MES]


def is_string(s):
  try:
    s += ''
  except:
    return False
  return True

def frange(start, stop, step):
     i = start
     while i < stop:
         yield i
         i += step

all_data = pandas.DataFrame()
for year_file in glob('RN_SERVIÇOS_TELEASSISTENCIA_*_ANOM_.xlsm'):
    print year_file
    data = pandas.read_excel(year_file, sheet_name='TELECONSULTORIAS')
    all_data = all_data.append(data, ignore_index=True)

# TIRA OS ACENTOS E CAPITALIZA x, SE FOR STRING
def padronizar_elementos(x):
    if is_string(x):
        x = unidecode.unidecode(x)
        x = x.upper()
    return x

# CAPITALIZAR E TIRAR ACENTOS DE TODOS OS ELEMENTOS DA PLANILHA
# (OS NOMES DAS COLUNAS NÃO MUDAM)
all_data = all_data.applymap(padronizar_elementos)

# Retorna uma lista com todos os anos presentes nas planilhas analisadas (int)
def anos_analisados(dataframe):
    meses_anos = list(set(dataframe['MÊS'.decode('utf-8')].tolist()))
    anos = []

    for mes_ano in meses_anos:
        mes, ano = mes_ano.split('/')
        anos.append(int(ano))

    anos = list(set(anos))
    anos.sort()

    return anos

# Retorna uma lista com todos os meses presentes nas planilhas analisadas,
# no formato xx/201x (string)
def meses_analisados(anos, meses):
    mes_ano = []

    for ano in anos:
        for mes in meses:
            mes_ano.append(str(mes) + '/' + str(ano))

    return mes_ano

# Retorna as geres analisadas nas planilhas em ordem alfabética. Precisa de uma
# função específica para ordenar corretamente, por causa dos números romanos
def geres_analisadas(geres):
    numeros_geres = []

    for gere in geres:
        if is_string(gere) and 'GERES' in gere:
                num_romano = gere.replace('GERES ','')
                num_cardinal = roman.fromRoman(num_romano)
                numeros_geres.append(num_cardinal)

    numeros_geres.sort()

    geres_final = ['GERES ' + str(roman.toRoman(numero_cardinal)) for numero_cardinal in numeros_geres]

    return geres_final

# Retorna uma lista com todos os valores que existem em uma coluna de um
# dataframe, em ordem alfabética e sem repetições.
def valores_coluna(dataframe, coluna):
    valores = list(set(dataframe[coluna].tolist()))
    valores.sort()

    valores = [x for x in valores if is_string(x)] # elimina valores nan

    if coluna == 'GERES':
        valores = geres_analisadas(valores)

    return valores

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[]))

_ANOS_ANALISADOS = anos_analisados(all_data)
_MESES_ANALISADOS = meses_analisados(_ANOS_ANALISADOS, range(1,13))

TOOLTIPS=[
    ("Mês/ano", "@legenda"),
    ("Serviços", "@y")
]

# create a plot and style its properties
p = figure(title='', x_range=_MESES_ANALISADOS, plot_width=1000, plot_height=500, tooltips=TOOLTIPS)
r = p.vbar(x="x", width=0.9, bottom=0, top="y", color="colors", source=source, line_width=2)
p.xaxis.major_label_orientation = 1.2
# p.xaxis.major_label_orientation = np.pi/7
p.axis.axis_label_text_font_size = '14pt'
p.axis.axis_label_text_font_style = 'bold'
p.y_range.start = 0
# p.x_range.range_padding = 0.1
p.xgrid.grid_line_color = None
# source = r.data_source

# Retorna uma lista com todos os valores que existem em uma coluna de um
# dataframe, em ordem alfabética e sem repetições, filtradas pelos multiselects
def valores_coluna_filtrada(dataframe, nome_eixo):
    if '-- TODOS --' in multiselects[nome_eixo].value:
        abscissas = valores_coluna(dataframe, nome_eixo)
    else:
        abscissas = valores_coluna(dataframe[(dataframe[nome_eixo].isin(multiselects[nome_eixo].value))], nome_eixo)

    return abscissas

# Retorna um dataframe filtrado de acordo com os valores selecionados para cada
# coluna
def dados_filtrados(dataframe, colunas, valores_selecionados):
    for (coluna, valores) in zip(colunas, valores_selecionados):
        if '-- TODOS --' not in valores:
            dataframe = dataframe[(dataframe[coluna].isin(valores))]

    return dataframe

def grafico_mapa_calor(dados, valores_eixos, nomes_eixos):
    contagem = np.zeros((len(valores_eixos['x']), len(valores_eixos['y'])))
    xname = []
    yname = []
    alpha = []

    for i, x in enumerate(valores_eixos['x']):
        dados_x_filtrado = dados[dados[nomes_eixos['x']] == x]
        for j, y in enumerate(valores_eixos['y']):
            contagem[i, j] = dados_x_filtrado[dados_x_filtrado[nomes_eixos['y']] == y].shape[0]
            xname.append(x)
            yname.append(y)

    max_value = max(contagem.flatten())
    print max_value
    for value in contagem.flatten():
        alpha.append(min(value*1.0/max_value, 0.9) + 0.1)

    dados = dict(
        xname=xname,
        yname=yname,
        alphas=alpha,
        count=contagem.flatten(),
    )

    grafico = figure(title='',
       x_axis_location="above",
       x_range=valores_eixos['x'], y_range=valores_eixos['y'],
       tooltips = [('nomes', '@yname, @xname'), ('contagem', '@count')])

    grafico.plot_width = 800
    grafico.plot_height = 800
    grafico.grid.grid_line_color = None
    grafico.axis.axis_line_color = None
    grafico.axis.major_tick_line_color = None
    grafico.axis.major_label_text_font_size = "5pt"
    grafico.axis.major_label_standoff = 0
    grafico.xaxis.major_label_orientation = np.pi/2
    grafico.xaxis.axis_label = nomes_eixos['x'].upper()
    grafico.yaxis.axis_label = nomes_eixos['y'].upper()
    grafico.axis.axis_label_text_font_size = '14pt'
    grafico.axis.axis_label_text_font_style = 'bold'

    grafico.rect('xname', 'yname', 0.9, 0.9, source=dados,
            color='red', alpha='alphas', line_color=None,
            hover_line_color='black', hover_color='red')

    palette = []
    for alpha in frange(0.1, 1.0, 0.005):
        palette.append(RGB(255,0,0,alpha))
    color_mapper = LinearColorMapper(palette, low=0, high=max_value)
    color_bar = ColorBar(color_mapper=color_mapper,
                         label_standoff=12, border_line_color=None, location=(0,0))
    grafico.add_layout(color_bar, 'right')

    return grafico

def grafico_fracionado(tipo, eixo_x, eixo_y, intervalo_anos, intervalo_meses, dados):
    if tipo == _FRACIONADO_ANO:
        excecao = _MES
        intervalo = intervalo_anos
        intervalo_oposto = intervalo_meses
    elif tipo == _FRACIONADO_MES:
        excecao = _ANOS
        intervalo = intervalo_meses
        intervalo_oposto = intervalo_anos

    if eixo_x == excecao:
        x_valores = []
        for x in intervalo_oposto:
            x_valores.append(str(x))
    else:
        x_valores = valores_coluna_filtrada(dados, eixo_x)

    ordenada = 0
    por_tipo = {}
    por_tipo['x_valores'] = x_valores
    intervalo_str = []
    colors = Category20b[20][0:len(intervalo)]
    for unidade in intervalo:
        por_tipo[str(unidade)] = []
        intervalo_str.append(str(unidade))

    for valor in x_valores:
        if eixo_x == excecao:
            if tipo == _FRACIONADO_ANO:
                meses = meses_analisados(intervalo, [valor])
            elif tipo == _FRACIONADO_MES:
                meses = meses_analisados([valor], intervalo)

            total_por_valor = dados[dados[_MES].isin(meses)].shape[0]
        else:
            total_por_valor = dados[dados[eixo_x] == valor].shape[0]

        for unidade in intervalo:
            if tipo == _FRACIONADO_ANO:
                meses1 = meses_analisados([unidade], [valor])
                meses2 = meses_analisados([unidade], intervalo_oposto)
            elif tipo == _FRACIONADO_MES:
                meses1 = meses_analisados([valor], [unidade])
                meses2 = meses_analisados(intervalo_oposto, [unidade])

            if eixo_x == excecao:
                ordenada = dados[dados[_MES].isin(meses1)].shape[0]
            else:
                ordenada = dados[(dados[_MES].isin(meses2)) &
                                (dados[eixo_x] == valor)].shape[0]

            if eixo_y == _FREQUENCIA:
                por_tipo[str(unidade)].append(ordenada)
            elif eixo_y == _PORCENTAGEM:
                por_tipo[str(unidade)].append(ordenada*100.0/total_por_valor)

    grafico = figure(title='', y_axis_label='Frequência de teleconsultorias', x_range=x_valores, plot_width=1000, plot_height=500, tooltips="@x_valores/$name: @$name")
    grafico.vbar_stack(intervalo_str, x='x_valores', width=0.9, color=colors, source=por_tipo,
                legend=[value(x) for x in intervalo_str])
    grafico.xaxis.major_label_orientation = 1.2
    grafico.y_range.start = 0
    grafico.xgrid.grid_line_color = None
    grafico.xaxis.axis_label = eixo_x.upper()
    grafico.yaxis.axis_label = eixo_y.upper()
    grafico.xaxis.axis_label_text_font_size = '14pt'
    grafico.xaxis.axis_label_text_font_style = 'bold'
    grafico.yaxis.axis_label_text_font_size = '14pt'
    grafico.yaxis.axis_label_text_font_style = 'bold'

    return grafico

def grafico_setores(valores_eixos, nome_x):
    fonte = {
        'value': valores_eixos['y'],
        'legend': valores_eixos['x'],
        'angle': [],
        'colors': [],
    }

    for ordenada in valores_eixos['y']:
        fonte['angle'].append( round( (ordenada * 2 * np.pi)/sum(valores_eixos['y']) , 3))

    for x in range(0, len(valores_eixos['x']), 20):
        fonte['colors'].extend(Category20c[20])
    fonte['colors'] = fonte['colors'][0:len(valores_eixos['x'])]

    grafico = figure(plot_height=350, title=nome_x.upper(),
                tooltips="@legend: @value", x_range=(-0.5, 1.0))

    grafico.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='colors', legend='legend', source=fonte)

    grafico.axis.axis_label=None
    grafico.axis.visible=False
    grafico.grid.grid_line_color = None

    return grafico

def callback():
    # Armazena valores selecionados pelo usuário nos widgets
    anos = slider_anos.value
    meses = slider_meses.value
    eixo_x = select_x.value
    eixo_y = select_y.value
    tipo_grafico = select_tipo.value

    intervalo_anos = range(int(anos[0]),int(anos[1])+1)
    intervalo_meses = range(int(meses[0]),int(meses[1])+1)

    keys_multiselects = list(_COLUNAS)
    valores_multiselects = []
    for key in keys_multiselects:
        valores_multiselects.append(multiselects[key].value)
    keys_multiselects.append(_MES)
    valores_multiselects.append(meses_analisados(intervalo_anos, intervalo_meses))

    dados = dados_filtrados(all_data, keys_multiselects, valores_multiselects)
    print dados.shape[0]

    cores = []
    abscissas = []
    ordenadas = []

    p.xaxis.axis_label = eixo_x.upper()
    p.yaxis.axis_label = eixo_y.upper()

    if tipo_grafico == _BARRAS or tipo_grafico == _LINHA or tipo_grafico == _SETORES:
        total = dados.shape[0]

        if eixo_x == _MES or eixo_x == _ANOS:

            for i, ano in enumerate(intervalo_anos):
                ordenada_ano = 0
                for mes in intervalo_meses:
                    mes_ano = str(mes)+"/"+str(ano)
                    ordenada = dados[dados[_MES] == mes_ano].shape[0]

                    if eixo_x == _MES:
                        abscissas.append(mes_ano)
                        if eixo_y == _FREQUENCIA:
                            ordenadas.append(ordenada)
                        elif eixo_y == _PORCENTAGEM:
                            ordenadas.append(ordenada * 100.0 / total)

                        cores.append(Category10[10][i])
                    elif eixo_x == _ANOS:
                        ordenada_ano += ordenada

                if eixo_x == _ANOS:
                    abscissas.append(str(ano))
                    if eixo_y == _FREQUENCIA:
                        ordenadas.append(ordenada_ano)
                    elif eixo_y == _PORCENTAGEM:
                        ordenadas.append(ordenada_ano * 100.0 / total)
                    cores.append(Category10[10][i])


        else:
            abscissas = valores_coluna_filtrada(dados, eixo_x)
            ordenadas = []

            for valor in abscissas:
                if eixo_y == _FREQUENCIA:
                    ordenadas.append(dados[dados[eixo_x] == valor].shape[0])
                elif eixo_y == _PORCENTAGEM:
                    ordenadas.append(dados[dados[eixo_x] == valor].shape[0] * 100.0 / total)

        if tipo_grafico == _SETORES:
            valores_eixos = {
                'x': abscissas,
                'y': ordenadas
            }

            grafico = grafico_setores(valores_eixos, eixo_x)
            l.children = [grafico, button, row_widgets]

        elif tipo_grafico == _LINHA:

            grafico = figure(title='', x_range=abscissas, plot_width=1000, plot_height=500, tooltips=TOOLTIPS)
            grafico.xaxis.major_label_orientation = 1.2
            grafico.axis.axis_label_text_font_size = '14pt'
            grafico.axis.axis_label_text_font_style = 'bold'
            grafico.xaxis.axis_label = eixo_x.upper()
            grafico.yaxis.axis_label = eixo_y.upper()

            if eixo_x == _MES:
                for i, ano in enumerate(_ANOS_ANALISADOS):
                    grafico.line(x=abscissas[(12*i):(12*i+13)], y=ordenadas[(12*i):(12*i+13)], color=Category10[10][i], line_width=4)
            else:
                grafico.line(x='x', y='y', source=source, color=Category10[10][3], line_width=4)

            l.children = [grafico, button, row_widgets]

        elif tipo_grafico == _BARRAS:
            l.children = [p, button, row_widgets]


    elif tipo_grafico == _POR_ANOS:
        if eixo_x == _MES:

            abscissas = intervalo_meses
            ordenadas = []
            ordenada = 0

            for mes in intervalo_meses:
                total = dados[dados[_MES].isin(meses_analisados(intervalo_anos, [mes]))].shape[0]
                for ano in intervalo_anos:
                    ordenada = dados[dados[_MES].isin(meses_analisados([ano], [mes]))].shape[0]
                    if eixo_y == _FREQUENCIA:
                        ordenadas.append(ordenada)
                    elif eixo_y == _PORCENTAGEM:
                        ordenadas.append(ordenada * 100.0 / total)

            for x in abscissas:
                cores.extend(Category10[10][0:len(intervalo_anos)])

            # this creates [ ("Apples", "2015"), ("Apples", "2016"), ("Apples", "2017"), ("Pears", "2015), ... ]
            abscissas = [ (str(abscissa), str(ano)) for abscissa in abscissas for ano in intervalo_anos ]

        else:
            abscissas = valores_coluna_filtrada(dados, eixo_x)
            ordenadas = []
            for valor in abscissas:
                total = dados[dados[eixo_x] == valor].shape[0]
                for ano in intervalo_anos:
                    m = meses_analisados([ano], intervalo_meses)
                    dados2 = dados_filtrados(dados, [_MES], [m])

                    ordenada = dados2[dados2[eixo_x] == valor].shape[0]
                    if eixo_y == _FREQUENCIA:
                        ordenadas.append(ordenada)
                    elif eixo_y == _PORCENTAGEM:
                        ordenadas.append(ordenada * 100.0 / total)

            for x in abscissas:
                cores.extend(Category10[10][0:len(intervalo_anos)])

            abscissas = [ (str(abscissa), str(ano)) for abscissa in abscissas for ano in intervalo_anos ]

        l.children = [p, button, row_widgets]


    elif tipo_grafico == _MAPA_CALOR:

        valores_eixos = {
            'x': valores_coluna_filtrada(dados, eixo_x),
            'y': valores_coluna_filtrada(dados, eixo_y)
        }

        nomes_eixos = {
            'x': eixo_x,
            'y': eixo_y
        }

        grafico = grafico_mapa_calor(dados, valores_eixos, nomes_eixos)
        l.children = [grafico, button, row_widgets]


    elif tipo_grafico == _FRACIONADO_ANO:

        grafico = grafico_fracionado(_FRACIONADO_ANO, eixo_x, eixo_y, intervalo_anos, intervalo_meses, dados)
        l.children = [grafico, button, row_widgets]


    elif tipo_grafico == _FRACIONADO_MES:

        grafico = grafico_fracionado(_FRACIONADO_MES, eixo_x, eixo_y, intervalo_anos, intervalo_meses, dados)
        l.children = [grafico, button, row_widgets]

    print abscissas, ordenadas

    p.x_range.factors = abscissas

    if cores == []:
        for x in range(0, len(abscissas), 20):
            cores.extend(Category20b[20])
        cores = cores[0:len(abscissas)]

    source.data = dict(
        x=abscissas,
        y=ordenadas,
        legenda=abscissas,
        colors=cores,
    )

def atualizar_multiselect(multiselect_mae, multiselect_filha, coluna_mae, coluna_filha):
    novos_valores = ['-- TODOS --']
    if '-- TODOS --' not in multiselect_mae.value:
        for valor in multiselect_mae.value:
            novos_valores.extend(valores_coluna(all_data[all_data[coluna_mae]==valor],coluna_filha))

        novos_valores = list(set(novos_valores))
        novos_valores.sort()
    else:
        novos_valores.extend(valores_coluna(all_data, coluna_filha))

    multiselect_filha.options = novos_valores
    multiselect_filha.value = novos_valores

def criar_multiselect(titulo, coluna):
    valores = ['-- TODOS --']
    valores.extend(valores_coluna(all_data, coluna))
    multiselect = MultiSelect(title=titulo, value=valores, options=valores)
    return multiselect

def ligar_multiselects(coluna_mae, coluna_filha):
    multiselects[coluna_mae].on_change('value', lambda attr, old, new:
        atualizar_multiselect(multiselects[coluna_mae], multiselects[coluna_filha], coluna_mae, coluna_filha))

def restringir_eixos():
    if select_tipo.value == _BARRAS or select_tipo.value == _SETORES:
        opt = [_MES, _ANOS]
        opt.extend(_COLUNAS)
        select_x.options = opt
        select_x.value = opt[0]
        select_y.options = [_FREQUENCIA, _PORCENTAGEM]
        select_y.value = _FREQUENCIA
    elif select_tipo.value == _POR_ANOS or select_tipo.value == _FRACIONADO_ANO:
        opt = [_MES]
        opt.extend(_COLUNAS)
        select_x.options = opt
        select_x.value = opt[0]
        select_y.options = [_FREQUENCIA, _PORCENTAGEM]
        select_y.value = _FREQUENCIA
    elif select_tipo.value == _FRACIONADO_MES:
        opt = [_ANOS]
        opt.extend(_COLUNAS)
        select_x.options = opt
        select_x.value = opt[0]
        select_y.options = [_FREQUENCIA, _PORCENTAGEM]
        select_y.value = _FREQUENCIA
    elif select_tipo.value == _MAPA_CALOR:
        select_x.options = _COLUNAS
        select_x.value = _COLUNAS[0]
        select_y.options = _COLUNAS
        select_y.value = _COLUNAS[0]

# Criando widgets
button = Button(label="Atualizar")
slider_anos = RangeSlider(title="Anos", value=(_ANOS_ANALISADOS[0],_ANOS_ANALISADOS[len(_ANOS_ANALISADOS)-1]), start=_ANOS_ANALISADOS[0], end=_ANOS_ANALISADOS[len(_ANOS_ANALISADOS)-1], step=1)
slider_meses = RangeSlider(title="Meses", value=(1,12), start=1, end=12, step=1)
select_tipo = Select(title="Tipo de gráfico:", options=_TIPOS_GRAFICO, value=_TIPOS_GRAFICO[0])
opt = [_MES, _ANOS]
opt.extend(_COLUNAS)
select_x = Select(title="Eixo X:", options=opt, value=_MES)
select_y = Select(title="Eixo Y:", options=[_FREQUENCIA, _PORCENTAGEM], value=_FREQUENCIA)

children = [select_tipo, select_x, select_y, slider_anos, slider_meses]
multiselects = {}
for (titulo, coluna) in zip(
    ["GERES:", "Municípios:", "Instituições:", "Ocupação do solicitante:",
    "Instituição do teleconsultor:", "Ocupação do teleconsultor:",
    "Especialidade do teleconsultor:", "Natureza:", "Área de teleconsultoria:",
    "Especialidade da dúvida:"],
    _COLUNAS):
    multiselects[coluna] = criar_multiselect(titulo, coluna)
    children.append(multiselects[coluna])

# Atribuindo ações aos widgets
button.on_click(callback)
ligar_multiselects(_GERES, _MUNICIPIO)
ligar_multiselects(_MUNICIPIO, _INSTITUICAO)
select_tipo.on_change('value', lambda attr, old, new: restringir_eixos())

# children.append(button)
sizing_mode = 'scale_width'
widgets = widgetbox(children[0:8], sizing_mode=sizing_mode)
widgets2 = widgetbox(children[8:15], sizing_mode=sizing_mode)
row_widgets = row([widgets, widgets2], sizing_mode=sizing_mode)

l = layout(children=[
            [p],
            [button],
            row_widgets,
        ],
        sizing_mode=sizing_mode,
    )

callback()

# Adicionando os gráficos e widgets ao documento
curdoc().add_root(l)
