import pandas as pd, numpy as np, re, streamlit as st
from datetime import datetime

@st.cache
def read_national_data(path, sheet_name, encoding='utf-8'):
    df = pd.read_excel(path, sheet_name=sheet_name, encoding=encoding)
    poblacion_regiones = get_poblacion_regiones()
    res_df = df.join((poblacion_regiones.set_index('region_title')), on='region_title')
    daily_df = get_daily_data(res_df)
    res_df, daily_df = transform_data(res_df), transform_data(daily_df)
    
    if 'fecha' in res_df.columns:
        res_df['fecha'] = pd.to_datetime((res_df['fecha']), format='%d-%m-%Y')
    
    if 'fecha' in daily_df.columns:
        daily_df['fecha'] = pd.to_datetime((daily_df['fecha']), format='%d-%m-%Y')
    
    return res_df, daily_df


def get_international_df(url):
    df = pd.read_csv(url)
    
    for col in ('Province/State', 'Lat', 'Long'):
        df.drop(col, axis=1, inplace=True)

    transforms = {
        'Cabo Verde':'Cape Verde',
        'Congo (Brazzaville)':'Congo [Republic]',
        'Congo (Kinshasa)':'Congo [DRC]',
        'Korea, South':'South Korea',
        'Taiwan*':'Taiwan',
        'US':'United States'
    }

    df['Country/Region'].replace(transforms, inplace=True)
    df = df.groupby('Country/Region').sum().reset_index()
    return df


@st.cache
def get_country_data():
    path = 'https://raw.githubusercontent.com/rubens36/covid19/master/data/countries.csv'
    return pd.read_csv(path, delimiter=';', encoding='latin-1')


@st.cache
def read_international_data():
    BASEURL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series'
    urls = [f"{BASEURL}/time_series_covid19_confirmed_global.csv",
     f"{BASEURL}/time_series_covid19_deaths_global.csv",
     f"{BASEURL}/time_series_covid19_recovered_global.csv"]
    results = [get_international_df(url) for url in urls]
    daily_data = [get_daily_data(res, date_re='\\d+/\\d+/\\d+') for res in results]
    results += daily_data
    return tuple(map(transform_international_data, results))


def get_daily_data(df, date_re='\\d{4}(-\\d{2}){2}'):
    dates_columns = get_dates((df.columns), date_re=date_re)
    res_df = pd.DataFrame()
    for col in df.columns:
        if col not in dates_columns:
            res_df[col] = df[col]

    actual = np.zeros((len(df)), dtype=int)
    for idx, col in enumerate(dates_columns):
        anterior = actual
        actual = df[col].copy()
        res_df[col] = actual - anterior

    return res_df


def get_dates(data, date_re='\\d{4}(-\\d{2}){2}'):
    dates_columns = [element for element in list(data) if re.match(date_re, str(element))]
    key = None if type(dates_columns[0]) != str else (lambda x: datetime.strptime(x, '%m/%d/%y'))
    return sorted(dates_columns, key=key)


def get_poblacion_regiones():
    res_dict = {
        'region_title':[
            'Metropolitana', 'Valparaíso', 'Biobío', 'Maule', 'Araucanía',
            "O'Higgins", 'Los Lagos', 'Coquimbo', 'Antofagasta', 'Ñuble', 'Los Ríos',
            'Tarapacá', 'Atacama', 'Arica y Parinacota', 'Magallanes', 'Aysén'
        ],
        'poblacion':[
            7112808, 1815902, 1556805, 1044950, 957224, 914555, 828708,
            757586, 607534, 480609, 384837, 330558, 286168, 226068, 166533, 103158
        ]
    }

    return pd.DataFrame.from_dict(res_dict)


def transform_data(df: pd.DataFrame):
    return df.melt(
        id_vars=['region_title', 'region', 'id', 'poblacion'], 
        var_name='fecha',
        value_name='infectados'
    )


def transform_international_data(df):
    df = pd.melt(df, id_vars=['Country/Region'], var_name='fecha', value_name='casos')
    df['fecha'] = pd.to_datetime((df.fecha), infer_datetime_format=True)
    return df.rename(columns={'Country/Region': 'pais'})


def show_credentials():
    st.sidebar.markdown('* * *')
    st.sidebar.subheader('Credenciales:')
    st.sidebar.text('')
    st.sidebar.markdown('Desarrollador: **Rubén Sánchez Acosta**')
    st.sidebar.markdown('Correo: **ruben.sanchez01@ucn.cl**')
    st.sidebar.markdown('Código: [github.com/rubens36](https://github.com/github.com/rubens36)')


if __name__ == '__main__':
    cd = get_country_data()
    casos = read_international_data()[0]
    res_df = cd.join((casos.set_index('name')), on='pais')
    paises = casos['pais'].unique()
    paises2 = list(cd['name'])
    for pais in paises:
        if pais not in paises2:
            print(pais)

    print()
    print()