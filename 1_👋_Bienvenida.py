import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)
TITLE = 'Datos Demográficos de España'


def run():

    st.set_page_config(
        page_title="Bienvenido",
        page_icon="👋",
    )

    st.markdown('# ¡Bienvenido a nuestra página de Información Demográfica de España!')

    st.sidebar.info("☝️ Selecciona un apartado para empezar")

    st.markdown(
        '''En esta plataforma, encontrarás datos demográficos actualizados y 
        relevantes sobre España, uno de los países más fascinantes de Europa. 
        Nuestro objetivo es brindarte una visión completa y detallada de la 
        población española, su distribución, características demográficas y 
        mucho más. ¡Empecemos! 
    ''')
    st.markdown('**👈 Selecciona un apartado de la barra lateral** para comenzar a descubrir datos interesantísimos sobre nuestro país.')

    st.markdown(
        """
        ## ¿Por qué son importantes los datos demográficos?
        Los datos demográficos son fundamentales para comprender y analizar una sociedad. Proporcionan información valiosa sobre la composición de la población, su crecimiento, distribución geográfica, estructura por edades y otros factores clave. Estos datos son utilizados por gobiernos, investigadores, planificadores urbanos, empresas y muchas otras organizaciones para tomar decisiones informadas y desarrollar estrategias que beneficien a la sociedad en su conjunto.

        ## Explora la información demográfica de España
        En nuestra página, encontrarás una amplia gama de datos demográficos sobre España. Algunas de las secciones más destacadas incluyen:

        - **Visión general**: Descubre gráficos de líneas que muestran la evolución de la población, nacimientos, defunciones y matrimonios desde 1975 hasta la fecha más actualizada.
        - **Crecimiento natural** de la población: Obtén información detallada sobre cómo los nacimientos y las defunciones contribuyen al cambio en el tamaño de la población en España.
        - **Población total** por sexo y distribución geográfica: Explora gráficos que muestran la distribución de la población por género y su reparto geográfico en las diferentes regiones de España.
        - **Nacimientos y defunciones** por sexo, año y provincia: Sumérgete en los datos detallados sobre nacimientos y defunciones, y observa las variaciones geográficas a través de mapas de coropletas.
        - **Matrimonios**: Compara el número de matrimonios entre dos años específicos y obtén información sobre el número de matrimonios por año y provincia.
        - **Nombres más famosos de bebés**: Utiliza nuestro buscador para verificar si un nombre está clasificado como el más popular en cada provincia y explora los nombres más populares en un mapa con el top-1 por provincias.

        ¡Explora nuestra página y adéntrate en la fascinante demografía de España!        

        ## Fuentes confiables y actualizadas
        Para garantizar la precisión y confiabilidad de nuestros datos, nos basamos en fuentes oficiales y actualizadas. Estas incluyen:
        - Instituto Nacional de Estadística (INE): El INE es la principal institución encargada de recopilar y proporcionar datos demográficos en España. Nos apoyamos en sus informes y estadísticas para ofrecerte información precisa y actualizada sobre la población, nacimientos, defunciones y matrimonios.
        - Centro Nacional de Información Geográfica (CNIG): El CNIG nos provee de datos geográficos precisos y actualizados, incluyendo la cartografía utilizada en nuestros mapas de coropletas.
    """
    )
    st.write(' ')
    st.markdown('¡Esperamos que disfrutes explorando los datos demográficos de España en nuestra página web! ¡Gracias por visitarnos y esperamos que encuentres la información que estás buscando!')

    st.divider()
    st.markdown('Autor de la web: Mario Andreu Villar (marioandreuvillar@gmail.com)')
    st.markdown('Última revisión: Junio del 2023')



if __name__ == "__main__":
    run()
