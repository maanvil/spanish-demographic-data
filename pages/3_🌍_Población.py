import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings; warnings.filterwarnings("ignore")

mill = lambda n : f'{n/1e6:.1f}M'
kilo = lambda n : f'{n/1e3:.0f}K'

@st.cache_data
def get_data_poblacion_provs():
    df = pd.read_csv('./data/poblacion_por_provincias.csv', sep=';', 
        converters = {'Total':lambda x:float(x.replace('.','').replace(',','.')), 
                      'Provincias':lambda x:x.replace('Araba/Álava','Álava/Araba'),
                      'Periodo':lambda x : int(x.strip().split()[-1])})
    df.drop(['Sexo','Edad'], axis=1, inplace=True)
    return df, min(df.Periodo), max(df.Periodo)

@st.cache_data
def get_data_poblacion_tipo(min_year, max_year):
    df = pd.read_csv('./data/poblacion_por_sexo_edad.csv', sep=';')
    df1 = df[df.Periodo>=min_year+1]
    df1 = df1[df1.Periodo<=max_year]
    df2 = df[df.Periodo>=min_year]
    df2 = df2[df2.Periodo<=max_year]
    return df1, df2
                     
@st.cache_data
def donut(df, top, year):
    df = df[df.Periodo==year]
    df.drop(['Periodo'], axis=1, inplace=True)
    df = df.set_index('Provincias')
    df.drop('Total Nacional', inplace=True)
    df = df.reset_index()
    df = df.sort_values(by=['Total'], ascending=False).head(top)
    df.Total = df.Total.apply(lambda x: round(x))
    df.Provincias = df.Provincias.apply(lambda x:' '.join(x.split()[1:]))
    df.Provincias = df.Provincias.apply(lambda x: ' '.join(reversed(x.strip().split(', '))) if ', ' in x else x)
    df.Provincias = df.Provincias.apply(lambda x: list(reversed(x.strip().split('/')))[1] if '/' in x else x)

    colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']

    fig = go.Figure(data=[go.Pie(labels=df.Provincias, values=df.Total, hole=0.5)])
    fig.update_layout(title=f'TOP-{top} provincias con más habitantes en el año {year}', 
        annotations=[dict(text=f'{year}', x=0.5, y=0.5, font_size=44, showarrow=False)])
    fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=24,
                  marker=dict(colors=colors, line=dict(color='white', width=2)))
    fig.update_layout(width=700, height=700)
    st.plotly_chart(fig, use_container_width=True)

    df = df.reset_index()
    for c in range(top//3+1):
        cols = st.columns(3)
        r = top%3 if c == top//3 else 3
        for i in range(r):
            cols[i].metric(df.at[3*c+i,'Provincias'], f'{round(df.at[3*c+i,"Total"]):,}')

@st.cache_data
def piramide(df, year):
    dfh = df[(df.Sexo=='Hombres') & (df.Edad!='Todas') & (df.Periodo==year)]
    dfm = df[(df.Sexo=='Mujeres') & (df.Edad!='Todas') & (df.Periodo==year)]

    dfh['Edad'] = pd.to_numeric(dfh['Edad'])
    dfm['Edad'] = pd.to_numeric(dfm['Edad'])

    dfh['Grupo'] = pd.cut(dfh['Edad'], bins=list(range(0,111,10)), right=False,
        labels=[f'{x-10}-{x-1}'if x<=100 else '>= 100' for x in range(10,111,10)])
    dfm['Grupo'] = pd.cut(dfm['Edad'], bins=list(range(0,111,10)), right=False,
        labels=[f'{x-10}-{x-1}'if x<=100 else '>= 100' for x in range(10,111,10)])
    
    dh = dfh.groupby('Grupo').sum()['Total']*-1
    dm = dfm.groupby('Grupo').sum()['Total']

    fig = go.Figure()
    fig.add_trace(go.Bar(y=dh.index.tolist(),x=dh.tolist(),name='Hombres',orientation='h'))
    fig.add_trace(go.Bar(y=dm.index.tolist(),x=dm.tolist(),name='Mujeres',orientation='h'))

    fig['data'][0]['marker']['color']='royalblue'
    fig['data'][1]['marker']['color']='sandybrown'
    
    fig.update_layout(title='', barmode='relative', bargap=0, bargroupgap=0,
        xaxis=dict(tickvals=[-4e6, -2e6, 0, 2e6, 4e6],
                     ticktext=['4M', '2M', '0', '2M', '4M'],
                     title='Población'),
        yaxis=dict(title='Grupo de edad'),
        legend_title='Sexo',
    )
    fig.update_traces(hovertemplate='%{x:,}')

    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def barras_genero(df, year):
    df = df[(df.Edad=='Todas') & (df.Sexo!='Total')]
    fig = px.bar(df, x='Periodo', y='Total', color='Sexo')
    
    fig['data'][0]['marker']['color']='royalblue'
    fig['data'][1]['marker']['color']='sandybrown'

    fig.update_traces(hovertemplate='%{y:,}')
    fig.update_layout(hovermode='x unified') 

    h,m = df[df.Periodo==year]['Total'].values
    fig.add_annotation(
        x=year, y=h+m, text=f'{h+m:,}', ax=0, ay=-75,
        showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#636363",
        font=dict(size=20, color="black"), align="center",
        bordercolor="#c7c7c7", borderwidth=2, borderpad=4, bgcolor="white", opacity=0.7
    )

    st.plotly_chart(fig, use_container_width=True)

@st.cache_data
def basic_metrics(df, year):
    df = df[(df.Edad=='Todas') & (df.Periodo==year)]
    p, h, m = df.Total.values
    return int(p), int(h), int(m)

###############################

TITLE = 'Población'

st.set_page_config(page_title=TITLE, page_icon='🌍')
st.markdown('# ' + TITLE)
st.sidebar.header(TITLE)
st.caption('Fuente: INE')
st.write('''
    En esta sección, encontrarás información detallada sobre 
    la población española, su distribución por edad, sexo y su 
    reparto geográfico en las diferentes regiones del país.'''
)
st.write('')

###############################

df_prov, min_year, max_year = get_data_poblacion_provs()
df_tipo, real_df_tipo = get_data_poblacion_tipo(min_year, max_year)

year = st.sidebar.selectbox('Año destacado', list(range(max_year,min_year,-1)), 0)

p, h, m = basic_metrics(real_df_tipo, year)
pp, ph, pm = basic_metrics(real_df_tipo, year-1)
col1, col2, col3 = st.columns(3)
col1.metric(f'Población {year}', f'{p:,}', f'{p-pp:,}')
col2.metric(f'Hombres', f'{h:,}', f'{h-ph:,}')
col3.metric(f'Mujeres', f'{m:,}', f'{m-pm:,}')

st.write('')

tab1, tab2 = st.tabs(['Población por edad y sexo', 'Distribución geográfica'])

with tab1:
    st.header(f'Pirámide poblacional - Año {year}')
    st.write('''Explora la pirámide poblacional de España, una representación 
    gráfica que muestra la distribución de la población por grupos de 
    edad y sexo. Esta herramienta visual te permitirá comprender la 
    estructura demográfica del país y observar cómo ha evolucionado 
    a lo largo del tiempo.''')
    piramide(df_tipo, year)
    st.divider()
    st.header('Población por sexo')
    st.write('''Explora la distribución de la población en España 
    desglosada por sexo. Este análisis demográfico te permitirá 
    conocer la proporción de hombres y mujeres en el país y 
    comprender cómo ha evolucionado a lo largo del tiempo.''')
    barras_genero(df_tipo, year)

with tab2:
    st.header('Distribución Geográfica')
    st.write('''Descubre la distribución geográfica de la población española. 
    Observa cómo se divide la población en las diferentes regiones del país 
    y compara la proporción de habitantes en cada una de ellas. 
    Recuerda que puedes cambiar el año seleccionado desde la barra lateral.''')
    top = st.slider('TOP provincias a mostrar:', 3, 52, 10)
    donut(df_prov, top, year)

###############################