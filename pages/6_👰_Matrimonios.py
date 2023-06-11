import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import numpy as np

#--------------

sep = lambda : st.write(' ')

prov_geo = './data/provincias.geojson'

@st.cache_data
def get_data(): # Solo tenemos datos de todo en el rango [1975, 2021]
    df = pd.read_csv('./data/matrimonios.csv', sep=';', 
        converters={'Provincias':lambda x:x.replace('Araba/Álava','Álava/Araba')}, dtype={'Codigo':str})
    df.rename(columns={'Total': 'Matrimonios'}, inplace=True)
    df['Provincias'] = df['Provincias'].apply(lambda x: ' '.join(reversed(x.strip().split(', '))) if ', ' in x else x)
    df['Provincias'] = df['Provincias'].apply(lambda x: '/'.join(reversed(x.strip().split('/'))) if '/' in x else x)
    df['Provincias'] = df['Provincias'].str.replace('Total','Total Nacional')
    prov_dict = pd.Series(df['Provincias'].values,index=df.Codigo).to_dict()
    rev_prov_dict = {v: k for k, v in prov_dict.items()}
    years = df['Periodo'].unique()

    poblacion = pd.read_csv('./data/poblacion_por_provincias.csv', sep=';', converters = {'Provincias':lambda x:' '.join(x.split()[1:]).replace('Araba/Álava','Álava/Araba'), 'Periodo':lambda x:int(x.split()[-1]), 'Total':lambda x:float(x.replace('.','').replace(',','.'))})
    poblacion.rename(columns={'Total': 'Poblacion'}, inplace=True)
    poblacion = poblacion[poblacion['Periodo']>=1975]
    poblacion = poblacion[poblacion['Periodo']<=2021]
    poblacion['Provincias'] = poblacion['Provincias'].apply(lambda x: ' '.join(reversed(x.strip().split(', '))) if ', ' in x else x)
    poblacion['Provincias'] = poblacion['Provincias'].apply(lambda x: '/'.join(reversed(x.strip().split('/'))) if '/' in x else x)
    poblacion['Provincias'] = poblacion['Provincias'].str.replace('Nacional','Total Nacional')

    assert sorted(poblacion['Provincias'].unique().tolist()) == sorted(df['Provincias'].unique())
    assert sorted(poblacion['Periodo'].unique().tolist()) == sorted(df['Periodo'].unique())

    df = df.merge(poblacion, left_on=['Provincias','Periodo'], right_on=['Provincias','Periodo'], how='left')

    df.drop(['Edad','Sexo'], axis=1, inplace=True)

    df['MatrimoniosperMil'] = df['Matrimonios'] / df['Poblacion'] * 1000

    sinTotal = df[df['Provincias']!='Total Nacional']

    # Harcoded es mas eficiente que calcularlo cada vez 
    prov_geo_point_2d = {'10':[39.7118899607,-6.16082194997],'11':[36.5538729195,-5.7604183752],'12':[40.2413705852,-0.146777086937],'13':[38.9256128254,-3.82809764894],'14':[37.9926944409,-4.80926161095],'15':[43.1257958229,-8.4642836868],'16':[39.8960496846,-2.19567153274],'17':[42.1280117119,2.6735559327],'18':[37.3125169672,-3.26788107732],'19':[40.8134495654,-2.62368878371],'20':[43.1437759117,-2.19417845709],'21':[37.5771794021,-6.82930221031],'22':[42.2030557371,-0.0728865943582],'23':[38.0165122783,-3.44169215171],'24':[42.6199552439,-5.83988102629],'25':[42.0439686698,1.04798206104],'26':[42.2748706958,-2.5170441194],'27':[43.011764,-7.44638404764],'28':[40.4950873744,-3.71704619215],'29':[36.8138591651,-4.72586195603],'30':[38.0023681653,-1.48575629332],'31':[42.6672011509,-1.64611414443],'32':[42.1964503002,-7.59259790937],'33':[43.292357861,-5.99350932547],'34':[42.3718338546,-4.53585717538],'35':[28.3624928216,-14.5509933924],'36':[42.435764706,-8.46106294738],'37':[40.8049892162,-6.06541224773],'38':[28.3125567678,-17.017856743],'39':[43.1975220484,-4.03002122038],'40':[41.1710254065,-4.05415057783],'41':[37.4356699135,-5.68277303032],'42':[41.6207742504,-2.58874304739],'43':[41.0876143957,0.818127863314],'44':[40.6612619615,-0.815532258446],'45':[39.7937341614,-4.14815562595],'46':[39.3702562375,-0.800789615081],'47':[41.6341260695,-4.84719141141],'48':[43.2376797057,-2.85260007926],'49':[41.7271743961,-5.98053925522],'50':[41.6203648019,-1.06449678144],'51':[35.8934069863,-5.34342403891],'52':[35.2908279949,-2.95053552337],'05':[40.5710367492,-4.94553505619],'06':[38.7097707381,-6.14158521981],'07':[39.5751889864,2.91229172079],'03':[38.4786378049,-0.568699068376],'02':[38.8254086192,-1.98037326935],'08':[41.7310008895,1.98405401772],'09':[42.3687127267,-3.58574245567],'04':[37.1960852121,-2.3448128003],'01':[42.8351264353,-2.72060346921]}

    return df, sinTotal, int(min(years)), int(max(years)), df.Provincias.unique(), prov_dict, rev_prov_dict, prov_geo_point_2d

@st.cache_data
def get_diff(year1, year2, df):
    if year1 != year2:
        df = df[(df['Periodo'] == year1) | (df['Periodo'] == year2)]
        df.loc[df['Periodo'] == year1, ['Matrimonios','MatrimoniosperMil']] *= -1      # Por -1 y luego se suman
        aux1 = df.groupby(['Codigo','Provincias'])['Matrimonios'].agg(sum).reset_index()
        aux2 = df.groupby(['Codigo','Provincias'])['MatrimoniosperMil'].agg(sum).reset_index()
        aux3 = df.groupby(['Codigo','Provincias'])['Poblacion'].agg(np.mean).reset_index()

        df = aux1
        df['MatrimoniosperMil'] = aux2['MatrimoniosperMil']
        df['Poblacion'] = aux3['Poblacion']

    else:
        df = df[df['Periodo'] == year1]
    
    return df

@st.cache_data
def get_data_prov(prov, df):
    return df[df.Provincias==prov]

@st.cache_data
def get_data_years(year1, year2, df, perMil):
    df = df[(df['Periodo'] == year1) | (df['Periodo'] == year2)]['MatrimoniosperMil' if perMil else 'Matrimonios']
    return df.values

@st.cache_data
def generate_metrics(year1, year2, df, perMil, sameYear=False):
    if sameYear:
        data = get_data_years(year1, year2, df, perMil)
        _, col, _ = st.columns([3,2,2])
        col.metric(f'Matrimonios {year1}', f'{data[0]:.2f} ‰' if perMil else f'{data[0]:,}')
    else:
        data2, data1 = get_data_years(year1, year2, df, perMil)
        col1, col2, col3 = st.columns(3)
        if perMil:
            col1.metric(f'Matrimonios {year1}', f'{data1:.2f} ‰')
            col2.metric(f'Matrimonios {year2}', f'{data2:.2f} ‰')
            col3.metric(f'Diferencia', f'{data2-data1:.2f} ‰')
        else:
            col1.metric(f'Matrimonios {year1}', f'{data1:,}')
            col2.metric(f'Matrimonios {year2}', f'{data2:,}')
            col3.metric(f'Diferencia', f'{data1-data2:,}')

def generate_map(df, sameYear=False):
    mn = abs(min(sinTotal['MatrimoniosperMil' if perMil else 'Matrimonios']))
    mx = abs(max(sinTotal['MatrimoniosperMil' if perMil else 'Matrimonios']))
    lim = mn if mn > mx else mx
    lim = int(lim) + 1
    if lim <= 1: lim = 2

    mapa = folium.Map(location=[40.42, -3.7], zoom_start=5, no_touch=True, control_scale=True)

    coropletas = folium.Choropleth(
        geo_data=prov_geo,
        name='Matrimonios',
        data=df,
        columns=['Codigo', 'MatrimoniosperMil' if perMil else 'Matrimonios'],
        key_on='properties.codigo', 
        fill_color='Greys' if sameYear else 'PRGn',
        fill_opacity=0.75,
        line_opacity=1.0,
        control=False,
        legend_name=f'Matrimonios ({"‰" if perMil else "cantidad"})',
        bins=6 if sameYear else (list(range(-lim,lim+1,1)) if perMil else list(range(-lim,lim+(lim//10),lim//10))) 
    )

    for feature in coropletas.geojson.data['features']:
        code = feature['properties']['codigo']
        feature['properties']['Provincia'] = prov_dict[code]
        feature['properties']['MatrimoniosperMil'] = f'{df[df.Codigo==code].MatrimoniosperMil.values[0]:.2f} ‰'
        feature['properties']['Matrimonios'] = f'{df[df.Codigo==code].Matrimonios.values[0]:,} bodas'

    coropletas.add_to(mapa)
    coropletas.geojson.add_child(folium.features.GeoJsonTooltip(['Provincia', 'MatrimoniosperMil' if perMil else 'Matrimonios'], labels=False))

    return mapa

###############################

TITLE = 'Comparativa de Matrimonios'
SHORT_TITLE = 'Matrimonios'

st.set_page_config(page_title=SHORT_TITLE, page_icon='👰')
st.markdown('# ' + TITLE)
st.sidebar.header(SHORT_TITLE)
st.caption('Fuente: INE')
st.write(
    '''En esta sección, encontrarás información comparativa sobre 
    los matrimonios en España. Compara el número de matrimonios 
    entre dos años específicos y descubre cómo ha evolucionado 
    esta institución a lo largo del tiempo.''')
st.write('Por otra parte, si superpones ambos años en el mismo, obtendrás los datos de matrimonios de ese año.')
st.write(
    '''Sumérgete en las estadísticas demográficas y observa las variaciones en 
    el número de matrimonios por año y provincia. Obtén una visión detallada 
    de cómo ha cambiado la tendencia matrimonial en diferentes regiones del país.'''
)
st.write(' ')

###############################

df, sinTotal, min_year, max_year, provs, prov_dict, rev_prov_dict, prov_geo_point_2d = get_data()

year1, year2 = st.slider('Años de comparativa:', min_year, max_year, (1982, 2012))
perMil = st.sidebar.checkbox('Mostrar datos por mil habitantes', True)
st.sidebar.write(' ')

sinTotal = get_diff(year1, year2, sinTotal)

#--------------

mapa = generate_map(sinTotal, sameYear=(year1==year2))
folium.TileLayer('cartodbpositron',name='light mode',control=True).add_to(mapa)
folium.TileLayer('cartodbdark_matter',name='dark mode',control=True).add_to(mapa)
folium.LayerControl(collapsed=False).add_to(mapa)

#--------------

sel = st.sidebar.selectbox('Región destacada:', provs)
if sel != 'Total Nacional':
    folium.Marker(prov_geo_point_2d[rev_prov_dict[sel]]).add_to(mapa)

#--------------

st_map = st_folium(mapa, width=700, height=450)
st.expander('Mostrar datos').table(sinTotal.set_index('Codigo'))

#--------------

df = get_data_prov(sel, df)

if year1 != year2:
    st.header(f'{sel} - Comparativa entre los años {year1} y {year2}')
    generate_metrics(year1, year2, df, perMil)
else:
    st.header(f'{sel} - Datos del año {year1}')
    generate_metrics(year1, year2, df, perMil, sameYear=True)

#--------------

fig = px.bar(df, x='Periodo', y='MatrimoniosperMil' if perMil else 'Matrimonios')

fig.update_layout(title=f'Matrimonios en {"España" if sel=="Total Nacional" else sel}', 
    hovermode='x unified', yaxis=dict(title='Matrimonios' + (' (‰)' if perMil else ''))) 
fig.update_traces(hovertemplate=('%{y:.2f} ‰' if perMil else '%{y:,} bodas'))
fig['data'][0]['marker']['color'] = ['#318CE7' if (c == year1 or c == year2) else 'lightblue' for c in fig['data'][0]['x']]

st.plotly_chart(fig, use_container_width=True)