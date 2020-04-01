import streamlit as st
import altair as alt
import datetime

from utils import (
    read_national_data, 
    read_international_data, 
    show_credentials 
)

from graphs import (
    get_global_chart,
    get_regional_chart,
    get_regional_proportion_chart,
    generate_regions_map,
    get_international_chart,
    generate_countries_map
)

st.sidebar.info("Herramienta desarrollada para la evaluación del \
    comportamiento del covid-19. Se centra en el análisis detallado \
    de la enfermedad en Chile y compara este comportamiento con el \
    de otros países.")

st.title("🦠😷 Evolución del Covid-19 en Chile")

scale_select = st.checkbox("Escala logarítmica")

if scale_select:
    scale = alt.Scale(type='log', scheme='teals')
else:
    scale = alt.Scale(type='linear', scheme='teals')

data_select = st.radio(
    "Seleccione la manera en que desea mostrar los datos:", 
    options=["Casos Totales", "Casos Diarios"]
)

page_select = st.sidebar.selectbox(
    "Seleccione el alcance de las visualizaciones:", 
    options=["Nacional", "Internacional"]
)

today = datetime.date.today()
default_date = today - datetime.timedelta(days=1)

if page_select == "Nacional":
    url_casos_chile = "https://github.com/rubens36/covid19/blob/master/data/Infectados%20Covid%20Chile.xlsx?raw=true"

    total_data, daily_data = read_national_data(url_casos_chile, "original")

    if data_select == "Casos Totales":
        data = total_data
    else:
        data = daily_data


    regiones = list(total_data["region_title"].unique())
    regiones = st.multiselect("Seleccione las regiones que desea incluir en el gráfico:", options=regiones, default=regiones)


    global_graph = get_global_chart(data, regiones, "infectados", scale, "Fecha")
    st.altair_chart(global_graph)

    regional_graph = get_regional_chart(data, regiones, "infectados", scale, "Fecha", "Región")
    st.altair_chart(regional_graph)

    proportion_graph = get_regional_proportion_chart(data, regiones, "infectados", scale, "Fecha", "Región")
    st.altair_chart(proportion_graph)

    date_select = st.date_input("Selecciona el día que deseas inspeccionar:", value=default_date, key="national_date")
    
    map_national_graph = generate_regions_map(data, date_select, "infectados", "Title")
    st.altair_chart(map_national_graph)
elif page_select == "Internacional":
    confirmed, deaths, recovered, confirmed_daily, deaths_daily, recovered_daily = read_international_data()
    
    data = {
        "total": {
            "confirmed": confirmed,
            "deaths": deaths,
            "recovered": recovered,
        },
        "daily": {
            "confirmed": confirmed_daily,
            "deaths": deaths_daily,
            "recovered": recovered_daily,
        }
    }

    if data_select == "Casos Totales":
        data = data["total"]
    else:
        data = data["daily"]

    data_select = st.selectbox(
        "Seleccione los tipos de datos que desea visualizar:", 
        options=["Casos confirmados", "Cantidad de muertes", "Cantidad de recuperados"]
    )

    if data_select == "Casos confirmados":
        data = data["confirmed"]
    elif data_select == "Cantidad de muertes":
        data = data["deaths"]
    else:
        data = data["recovered"]

    default_paises = ["Chile", "Cuba", "Mexico", "Brazil", "Argentina"]
    paises_select = st.multiselect(
        "Seleccione los países que desea incluir en el gráfico:", 
        options=list(data['pais']), 
        default=default_paises
    )
    international_graph = get_international_chart(data, paises_select, scale)
    st.altair_chart(international_graph)

    date_select = st.date_input("Selecciona el día que deseas inspeccionar:", value=default_date, key="international_date")
    
    interactive_select = st.checkbox("Interactivo")
    countries_graph = generate_countries_map(data, date_select,interactive=interactive_select)

    st.altair_chart(countries_graph)

show_credentials()