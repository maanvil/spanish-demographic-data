import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

#--------------

sep = lambda : st.write(' ')

prov_geo = './data/provincias.geojson'

@st.cache_data
def get_data(): # Solo tenemos datos de todo en el rango [1975, 2021]
    df = pd.read_csv('./data/defunciones.csv', sep=';', 
        converters={'Provincias':lambda x:x.replace('Araba/Álava','Álava/Araba')}, dtype={'Codigo':str})
    df.rename(columns={'Total': 'Defunciones'}, inplace=True)
    df['Provincias'] = df['Provincias'].apply(lambda x: ' '.join(reversed(x.strip().split(', '))) if ', ' in x else x)
    df['Provincias'] = df['Provincias'].apply(lambda x: '/'.join(reversed(x.strip().split('/'))) if '/' in x else x)
    df['Provincias'] = df['Provincias'].str.replace('Total','Total Nacional')
    prov_dict = pd.Series(df['Provincias'].values,index=df.Codigo).to_dict()
    rev_prov_dict = {v: k for k, v in prov_dict.items()}
    years = df['Periodo'].unique()

    poblacion = pd.read_csv('./data/poblacion_por_provincias.csv', sep=';', converters = {'Provincias':lambda x:' '.join(x.split()[1:]).replace('Araba/Álava','Álava/Araba'), 'Periodo':lambda x:int(x.split()[-1]), 'Total':lambda x:float(x.replace('.','').replace(',','.'))})
    poblacion.drop(['Sexo','Edad'], axis=1, inplace=True)
    poblacion.rename(columns={'Total': 'Poblacion'}, inplace=True)
    poblacion = poblacion[poblacion['Periodo']>=1975]
    poblacion = poblacion[poblacion['Periodo']<=2021]
    poblacion['Provincias'] = poblacion['Provincias'].apply(lambda x: ' '.join(reversed(x.strip().split(', '))) if ', ' in x else x)
    poblacion['Provincias'] = poblacion['Provincias'].apply(lambda x: '/'.join(reversed(x.strip().split('/'))) if '/' in x else x)
    poblacion['Provincias'] = poblacion['Provincias'].str.replace('Nacional','Total Nacional')

    assert sorted(poblacion['Provincias'].unique().tolist()) == sorted(df['Provincias'].unique())
    assert sorted(poblacion['Periodo'].unique().tolist()) == sorted(df['Periodo'].unique())

    df = df.merge(poblacion, left_on=['Provincias','Periodo'], right_on=['Provincias','Periodo'], how='left')

    df['DefuncionesPerMil'] = df['Defunciones'] / df['Poblacion'] * 1000

    sinTotal = df[df['Provincias']!='Total Nacional']

    # Harcoded es mas eficiente que calcularlo cada vez 
    prov_geo_point_2d = {"10":[39.7118899607,-6.16082194997],"11":[36.5538729195,-5.7604183752],"12":[40.2413705852,-0.146777086937],"13":[38.9256128254,-3.82809764894],"14":[37.9926944409,-4.80926161095],"15":[43.1257958229,-8.4642836868],"16":[39.8960496846,-2.19567153274],"17":[42.1280117119,2.6735559327],"18":[37.3125169672,-3.26788107732],"19":[40.8134495654,-2.62368878371],"20":[43.1437759117,-2.19417845709],"21":[37.5771794021,-6.82930221031],"22":[42.2030557371,-0.0728865943582],"23":[38.0165122783,-3.44169215171],"24":[42.6199552439,-5.83988102629],"25":[42.0439686698,1.04798206104],"26":[42.2748706958,-2.5170441194],"27":[43.011764,-7.44638404764],"28":[40.4950873744,-3.71704619215],"29":[36.8138591651,-4.72586195603],"30":[38.0023681653,-1.48575629332],"31":[42.6672011509,-1.64611414443],"32":[42.1964503002,-7.59259790937],"33":[43.292357861,-5.99350932547],"34":[42.3718338546,-4.53585717538],"35":[28.3624928216,-14.5509933924],"36":[42.435764706,-8.46106294738],"37":[40.8049892162,-6.06541224773],"38":[28.3125567678,-17.017856743],"39":[43.1975220484,-4.03002122038],"40":[41.1710254065,-4.05415057783],"41":[37.4356699135,-5.68277303032],"42":[41.6207742504,-2.58874304739],"43":[41.0876143957,0.818127863314],"44":[40.6612619615,-0.815532258446],"45":[39.7937341614,-4.14815562595],"46":[39.3702562375,-0.800789615081],"47":[41.6341260695,-4.84719141141],"48":[43.2376797057,-2.85260007926],"49":[41.7271743961,-5.98053925522],"50":[41.6203648019,-1.06449678144],"51":[35.8934069863,-5.34342403891],"52":[35.2908279949,-2.95053552337],"05":[40.5710367492,-4.94553505619],"06":[38.7097707381,-6.14158521981],"07":[39.5751889864,2.91229172079],"03":[38.4786378049,-0.568699068376],"02":[38.8254086192,-1.98037326935],"08":[41.7310008895,1.98405401772],"09":[42.3687127267,-3.58574245567],"04":[37.1960852121,-2.3448128003],"01":[42.8351264353,-2.72060346921]}

    return df, sinTotal, int(min(years)), int(max(years)), df.Provincias.unique(), prov_dict, rev_prov_dict, prov_geo_point_2d

# @st.cache_data(experimental_allow_widgets=True) 
# # Parece que va bien pero al ser experimental no me atrevo a dejarlo
# # From the docs: "We may remove support for this option at any time without notice."
def generate_map(df, year, sex, prov, perMil):

    df = df[(df['Periodo'] == year) & (df['Sexo'] == sex)]

    mapa = folium.Map(location=[40.42, -3.7], zoom_start=5, no_touch=True, control_scale=True)

    coropletas = folium.Choropleth(
        geo_data=prov_geo,
        name='Defunciones',
        data=df,
        columns=['Codigo', 'DefuncionesPerMil' if perMil else 'Defunciones'],
        key_on='properties.codigo', 
        fill_color='Blues' if sex=='Hombres' else 'Oranges' if sex=='Mujeres' else 'Purples',
        fill_opacity=0.75,
        line_opacity=1.0,
        control=False,
        legend_name=f'Defunciones ({"‰" if perMil else "cantidad"})'
    )

    for feature in coropletas.geojson.data['features']:
        code = feature['properties']['codigo']
        feature['properties']['Provincia'] = prov_dict[code]
        feature['properties']['DefuncionesPerMil'] = f'{df[df.Codigo==code].DefuncionesPerMil.values[0]:.2f} ‰'
        feature['properties']['Defunciones'] = f'{df[df.Codigo==code].Defunciones.values[0]:,} difuntos'

    coropletas.add_to(mapa)
    coropletas.geojson.add_child(folium.features.GeoJsonTooltip(['Provincia', 'DefuncionesPerMil' if perMil else 'Defunciones'], labels=False))

    folium.TileLayer('cartodbpositron',name='light mode',control=True).add_to(mapa)
    folium.TileLayer('cartodbdark_matter',name='dark mode',control=True).add_to(mapa)
    folium.LayerControl(collapsed=False).add_to(mapa)

    if prov != 'Total Nacional':
        folium.Marker(prov_geo_point_2d[rev_prov_dict[prov]]).add_to(mapa)

    return st_folium(mapa, width=700, height=450)

###############################

TITLE = 'Defunciones en España'
SHORT_TITLE = 'Defunciones'

st.set_page_config(page_title=SHORT_TITLE, page_icon='⚰️')
st.markdown('# ' + TITLE)
st.sidebar.header(SHORT_TITLE)
st.caption('Fuente: INE')
st.write(
    '''En esta sección, encontrarás información detallada sobre las 
    defunciones en España. Explora datos por sexo, año y provincia, 
    y descubre cómo ha evolucionado el número de defunciones a lo largo del tiempo.''')

st.write(
    '''Sumérgete en las estadísticas demográficas y observa los patrones 
    y tendencias en las defunciones. Además, puedes visualizar los datos 
    en mapas de coropletas, que te ayudarán a comprender las diferencias 
    geográficas en las defunciones en cada provincia.'''
)
st.write('')

###############################

df, sinTotal, min_year, max_year, provs, prov_dict, rev_prov_dict, prov_geo_point_2d = get_data()

c1, c2 = st.columns(2, gap='large')
year = c1.slider('Año', min_year, max_year, max_year)
sex  = c2.radio('Sexo', ['Hombres', 'Ambos sexos', 'Mujeres'], horizontal=True, index=1)

perMil = st.sidebar.checkbox('Mostrar datos por mil habitantes', True)
st.sidebar.write(' ')

#--------------

if sex == 'Ambos sexos': sex = 'Total'

sel = st.sidebar.selectbox('Región destacada:', provs)

st_map = generate_map(sinTotal, year, sex, sel, perMil)

st.expander('Mostrar datos').table(
    df[(df['Sexo']==sex) & (df['Periodo']==year)].set_index('Codigo'))

#--------------

st.header(f'Evolución en {"España" if sel=="Total Nacional" else sel} - {"Ambos sexos" if sex=="Total" else sex}')

df = df[df['Provincias'] == sel]

value = df[(df['Sexo']==sex) & (df['Periodo']==year)]['DefuncionesPerMil' if perMil else 'Defunciones'].values[0]
h = df[(df['Sexo']=='Hombres') & (df['Periodo']==year)]['DefuncionesPerMil' if perMil else 'Defunciones'].values[0]
m = df[(df['Sexo']=='Mujeres') & (df['Periodo']==year)]['DefuncionesPerMil' if perMil else 'Defunciones'].values[0]

fig = px.bar(
    df[(df['Sexo'] != 'Total') if sex=='Total' else (df['Sexo'] == sex)], 
    x='Periodo', y='DefuncionesPerMil' if perMil else 'Defunciones', color='Sexo',
)

if sex=='Total': 
    fig['data'][0]['marker']['color']='royalblue'
    fig['data'][1]['marker']['color']='sandybrown'
elif sex=='Hombres':
    fig['data'][0]['marker']['color']='royalblue'
else:
    fig['data'][0]['marker']['color']='sandybrown'

fig.update_traces(hovertemplate='%{y:.2f} ‰' if perMil else '%{y:,} difuntos')
fig.update_layout(hovermode='closest', showlegend=(sex=='Total'), yaxis=dict(title='Defunciones' + (' (‰)' if perMil else '')))
fig.update_xaxes(showspikes=True, spikecolor="gray")
fig.update_yaxes(showspikes=True, spikecolor="gray")
fig.update_layout(spikedistance=1000, hoverdistance=100)
fig.update_layout(legend=dict(orientation='h', entrywidth=100, yanchor='top', y=1.2, xanchor='left', x=0))
fig.add_annotation(
    x=year, y=value, text=f'{value:.2f} ‰' if perMil else f'{value:,} difuntos', ax=0, ay=-75,
    showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#636363",
    font=dict(size=20, color="black"), align="center",
    bordercolor="#c7c7c7", borderwidth=2, borderpad=4, bgcolor="white", opacity=0.7
)

col1, col2 = st.columns([4,1])
col1.plotly_chart(fig, use_container_width=True)
# Añadimos espacios para conseguir un alineamiento vertical
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.write(' ')
col2.metric('Hombres', f'{h:.2f} ‰' if perMil else f'{h:,}')
col2.metric('Mujeres', f'{m:.2f} ‰' if perMil else f'{m:,}')
