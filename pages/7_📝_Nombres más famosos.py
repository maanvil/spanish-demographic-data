import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

#--------------

sep = lambda : st.write(' ')

@st.cache_data
def read_names():
    res = {} # year:df
    years = list(map(str, range(1920,2021,10)))

    for year in years:

        df = pd.read_csv(f'./data/nombres/nombres{year}.csv', sep=';', 
            converters = {'prov':lambda x:x.lower().replace('araba/álava','álava/araba').replace('avila','ávila')}
        )
        df = df.drop([34,37,50,51,52]) # extranjero, canarias, ceuta y melilla

        df['prov'] = df['prov'].apply(lambda x: ' '.join([s.capitalize() for s in x.split()]))
        df['prov'] = df['prov'].apply(lambda x: ' '.join(reversed(x.strip().split(', '))) if ', ' in x else x[0].upper()+x[1:])
        df['prov'] = df['prov'].apply(lambda x: '/'.join(reversed(x.strip().split('/'))) if '/' in x else x[0].upper()+x[1:])
        df['prov'] = df['prov'].apply(lambda x: x[0].upper()+x[1:])

        res[year] = df
    
    return res

@st.cache_data
def get_dict_of_names_years():
    d = {} # k=name, v=(year,sex)
    years = list(map(str, range(1920,2021,10)))
    data = read_names()

    for year in years:

        df = data[year]
        
        chicos = df.nameH.to_list()
        chicas = df.nameM.to_list()

        for name in set(chicos):
            if name in d:
                d[name].append((year,'H'))
            else:
                d[name] = [(year,'H')]

        for name in set(chicas):
            if name in d:
                d[name].append((year,'M'))
            else:
                d[name] = [(year,'M')]
    
    return d 

@st.cache_data
def get_maps():
    provincias = gpd.read_file('./data/provincias.zip!provincias')
    provincias = provincias[~provincias.NAMEUNIT.isin(['Ceuta','Melilla','Territorio no asociado a ninguna provincia'])]
    provincias.to_crs(crs=3395, inplace=True)
    provincias = provincias[['NAMEUNIT','CODNUT2', 'geometry']]

    data_names = read_names()

    for year,df in data_names.items(): 

        assert sorted(df.prov.to_list()) == sorted(provincias.NAMEUNIT.to_list()) 

        df = df.rename(columns={'nameH': 'nameH'+str(year), 'nameM': 'nameM'+str(year)})
        provincias = pd.merge(provincias, df[['prov', 'nameH'+str(year), 'nameM'+str(year)]], left_on='NAMEUNIT', right_on='prov', how='left')
        provincias = provincias.drop('prov', axis=1)

    return provincias

@st.cache_data(show_spinner=False)
def process_name(name, d):
    if name == '':
        st.info('''
            Escribe un nombre de bebé para empezar ☝️\n
            💡 Por ejemplo, puedes probar con "Alejandro" o "Marta"
        ''')
    elif name in d: 
        st.balloons()
        st.success(f'{name.capitalize()} es uno de los nombres más famosos 😄')

        st.divider()

        progress_bar = st.progress(0, text='Cargando mapas')

        sorted_list = sorted(d[name], key=lambda x:x[0])
        len_list = len(sorted_list)
        sorted_years = [year for year,_ in sorted_list]
        tabs = st.tabs(sorted_years)

        for i, (year, sex) in enumerate(sorted_list):
            t = tabs[i]
            letter = "o" if sex=="H" else "a"
            t.header(f'Nombres de chic{letter} más comunes en l{letter}s recién nacid{letter}s del {year}')

            aux = provs.copy()
            aux['color'] = aux[f'name{sex}{year}'].map({x:0 if x == name else 1 for x in aux[f'name{sex}{year}'].unique()})
            aux[f'name{sex}{year}'] = aux[f'name{sex}{year}'].str.replace('MARIA\s','Mᵃ ',regex=True)
            aux[f'name{sex}{year}'] = aux[f'name{sex}{year}'].str.replace('JOSE\s','J. ',regex=True)
            aux[f'name{sex}{year}'] = aux[f'name{sex}{year}'].str.replace('FRANCISCO\s','FCO. ',regex=True)

            fig, ax = plt.subplots(1,1,figsize=(12,12))
            ax = aux.boundary.plot(color='Black', linewidth=.4, ax=ax)
            ax.set_axis_off()
            aux.apply(lambda x:ax.annotate(text=x[f'name{sex}{year}'], xy=x.geometry.centroid.coords[0], ha='center', fontsize=10, 
                        bbox=dict(boxstyle="round", fc="w", ec='k', pad=0.4, alpha=0.65)), axis=1)

            aux.plot(ax=ax, cmap='tab20c', column='color')
            t.pyplot(fig, clear_figure=True)

            progress_bar.progress((i+1)/len_list, text=f'Cargando mapas:  ¡Mapa del {year} cargado!')

        progress_bar.empty()

    else:
        st.error(f'{name.capitalize()} no es uno de los nombres más famosos 😥')

###############################

TITLE = 'Nombres más famosos'

st.set_page_config(page_title=TITLE, page_icon='📝')
st.markdown('# ' + TITLE)
st.caption('Fuente: INE')
st.write(
    '''En esta sección, encontrarás información sobre los nombres más 
    famosos de bebés en España a lo largo de las décadas. Utiliza nuestro 
    buscador para verificar si un nombre específico está clasificado 
    como el más popular en alguna provincia.''')
st.write(
    '''Explora la fascinante demografía de los nombres de bebés y 
    descubre qué nombres han sido tendencia en diferentes épocas. 
    Además, si el nombre buscado está en el top-1 de alguna provincia, 
    podrás visualizar un mapa con los nombres 
    más famosos de ese año por provincia.'''
)
st.write(
    '''Sumérgete en los nombres más populares de los bebés en España y descubre 
    cómo han influido en la cultura y la sociedad a lo largo de las décadas.'''
)
st.write(' ')

###############################

provs = get_maps()

name = st.text_input('Nombre a buscar:', '')
name = name.strip().upper()

d = get_dict_of_names_years()

process_name(name, d)