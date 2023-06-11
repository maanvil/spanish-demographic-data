import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

mill = lambda n : f'{n/1e6:.1f}M'
kilo = lambda n : f'{n/1e3:.0f}K'

@st.cache_data
def get_data_evolucion():
    df = pd.read_csv('./data/evolucion_poblacion.csv', sep=';')
    min_year, max_year = min(df.Periodo), max(df.Periodo)
    return df, min_year, max_year

@st.cache_data
def metricas(year, df):
    df = df.set_index('Periodo')

    vars = ['Población', 'Nacimientos', 'Defunciones', 'Matrimonios']
    cols = st.columns(len(vars))

    for i, var in enumerate(vars):
        this = df.at[year,var]
        last = df.at[year-1,var] if year > 1975 else None
    
        cols[i].metric(f'{var} {year}', 
            mill(this) if var=='Población' else kilo(this), kilo(this-last) if year > 1975 else '')

@st.cache_data
def get_color(var):
    if var == 'Población': return 'lightskyblue'
    elif var == 'Nacimientos': return 'rebeccapurple'
    elif var == 'Defunciones': return 'darkorange'
    else: return 'forestgreen'

def grafica_general(data):
    variables = st.multiselect('Variables a estudiar:',
    ['Población', 'Nacimientos', 'Defunciones', 'Matrimonios'],
    ['Población', 'Nacimientos', 'Defunciones', 'Matrimonios'])

    data = data[data.Periodo>=v1]
    data = data[data.Periodo<=v2]

    # Figura con dos ejes Y
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    for var in variables:
        fig.add_trace(go.Scatter(x=data.Periodo, y=data[var], name=var, mode='lines+markers', marker_color=get_color(var)), secondary_y=(var=='Población'))

    fig.update_xaxes(title_text='Periodo')
    fig.update_yaxes(title_text='Personas', secondary_y=False)
    if 'Población' in variables:
        fig.update_yaxes(title_text='Personas (Población)', secondary_y=True)

    len_vars = len(variables)
    fig.update_layout(legend=dict(
        orientation='h',
        entrywidth=250 if len_vars==2 else 150 if len_vars==3 else 100,
        yanchor='top', y=1.2, xanchor='left', x=0,
        bordercolor='gray', borderwidth=0.5
    ))
    fig.update_traces(hovertemplate='%{y:,}')
    fig.update_layout(hovermode='x unified') 

    if v1 < 2009 and v2 > 2007:
        fig.add_vrect(x0=max(2007,v1),x1=min(2009,v2), line_width=0, fillcolor='gray', opacity=0.1, annotation_text='Gran Recesión', annotation_position='bottom', annotation_font=dict(color='black'))
    
    if v1 < 2022 and v2 > 2019:
        fig.add_vrect(x0=max(2019,v1),x1=min(2022,v2), line_width=0, fillcolor='gray', opacity=0.1, annotation_text='COVID-19', annotation_position='bottom', annotation_font=dict(color='black'))
    
    if v1 <= year <= v2:
        fig.add_vline(x=year, line_width=2, line_dash='dash', line_color='gray')

    st.plotly_chart(fig, use_container_width=True)

    exp = st.expander('Mostrar datos')
    with exp:
        df = data.set_index('Periodo')
        df.Nacimientos = df.Nacimientos.apply(lambda x:f'{int(x):,}')
        df.Defunciones = df.Defunciones.apply(lambda x:f'{int(x):,}')
        df.Población = df.Población.apply(lambda x:f'{int(x):,}')
        df.Matrimonios = df.Matrimonios.apply(lambda x:f'{int(x):,}')
        exp.table(df)#.Nacimientos if tipo == 'Nacimientos' else df.Defunciones if tipo == 'Defunciones' else df)

def crecimiento(df):
    df = df[df.Periodo>=v1]
    df = df[df.Periodo<=v2]

    col1, col2 = st.columns([4, 1])

    with col1:
        df['Δ Personas'] = df.Nacimientos - df.Defunciones
        fig = px.line(df, x='Periodo', y='Δ Personas', markers=True)
        fig['data'][0]['line']['color']='black'
        fig.add_hline(y=0, line_width=1, line_dash='dash', line_color='black')
        if v2 > 2015: fig.add_vrect(x0=max(2015,v1),x1=v2, line_width=0, fillcolor='red', annotation_text='Crecimiento negativo', annotation_position='top', annotation_font=dict(color='black'), opacity=0.1)
        if v1 < 2015: fig.add_vrect(x0=v1,x1=min(v2,2015), line_width=0, fillcolor='forestgreen', annotation_text='Crecimiento positivo', annotation_position='bottom', annotation_font=dict(color='black'), opacity=0.1)
        
        df, _, _ = get_data_evolucion()
        df = df.set_index('Periodo')
        df['Δ Personas'] = df.Nacimientos - df.Defunciones
        y = df.at[year, 'Δ Personas']

        if v1 <= year <= v2:
            fig.add_shape(type='circle', x0=year-0.5, y0=y-2e4, x1=year+0.5, y1=y+2e4, line_color='#318CE7')

        fig.update_traces(mode="markers+lines", hovertemplate='Δ Personas = %{y:,}')
        fig.update_layout(hovermode='x unified')

        st.plotly_chart(fig, use_container_width=True)

    # Añadimos espacios para conseguir un alineamiento vertical
    col2.write(' ')
    col2.write(' ')
    col2.write(' ')
    col2.write(' ')
    col2.write(' ')
    col2.write(' ')
    col2.write(' ')
    col2.metric('Año destacado', year)
    col2.write(' ')
    col2.metric('Total crecimiento', f'{round(y):,}')

###############################

TITLE = 'Visión general de España'
SHORT_TITLE = 'Visión general'

st.set_page_config(page_title=SHORT_TITLE, page_icon='📈')
st.markdown('# ' + TITLE)
st.sidebar.header(SHORT_TITLE)
st.caption('Fuente: INE')
st.write(
    '''En esta sección, encontrarás gráficos de líneas que muestran 
    la evolución de la población, nacimientos, defunciones y 
    matrimonios desde 1975 hasta la fecha más actualizada.
    En la barra lateral puedes seleccionar diferentes parámetros 
    para filtrar los datos.'''
)
st.write('')

###############################

df, min_year, max_year = get_data_evolucion()
year = st.sidebar.selectbox('Año destacado', list(range(max_year,min_year-1,-1)), 0)

metricas(year, df)

st.write('')
st.sidebar.write(' ')

v1, v2 = st.sidebar.slider('Intervalo de años a estudiar', min_value=min_year, max_value=max_year, value=(min_year, max_year), step=1, key='anyosEnCrecimiento')

tab1, tab2 = st.tabs(['Visión general', 'Crecimiento natural de la población'])

with tab1:
    st.header('Evolución de la sociedad')
    st.markdown('''Explora el gráfico de líneas que representa la 
    evolución de distintos fenómenos demográficos a lo largo de los años. Comprende cómo estos indicadores demográficos 
    han influenciado y moldeado la sociedad española en 
    diferentes momentos históricos.''')
    grafica_general(df)

with tab2:
    st.header('Crecimiento natural de la población')
    st.markdown('''
    Descubre el concepto de crecimiento natural de la población y 
    su impacto en el tamaño y la estructura demográfica de España. 
    Este indicador refleja la diferencia entre el número de nacimientos 
    y el número de defunciones en un determinado período de tiempo. 
    ''')
    crecimiento(df)

