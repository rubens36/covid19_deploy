import altair as alt, vega_datasets as vd, pandas as pd, datetime
from utils import get_country_data

def get_title(columna):
    titles = {'infectados': 'Cantidad de Casos'}
    return titles[columna]


def get_global_chart(
  data: pd.DataFrame, 
  regiones: list, 
  columna: str, 
  scale: alt.Scale, 
  x_title: str, 
  padding: int=5, 
  width: int=800, 
  height: int=250
  ):

  data = data[data['region_title'].isin(regiones)]
  chart = alt.Chart(data, title='Total de casos confirmados')
  
  if scale.type == 'log':
      chart = chart.transform_filter(alt.datum[columna] > 0)
  
  return (
    chart.mark_line(point={'size': 70})
    .encode(
      x=alt.X('fecha:T', title=x_title),
      y=alt.Y(f"sum({columna}):Q", title=(get_title(columna)), scale=scale),
      tooltip=[
        alt.Tooltip(f"sum({columna}):Q", title=(get_title(columna))),
        alt.Tooltip('fecha', title=x_title, type='temporal')
        ]
    )
    .configure_scale(continuousPadding=padding)
    .properties(
      width=width,
      height=height
    ).interactive()
  )


def get_regional_chart(
  data: pd.DataFrame, 
  regiones: list, 
  feature: str, 
  scale: alt.Scale, 
  x_title: str, 
  color_title: str, 
  padding: int=5, 
  width: int=800, 
  height: int=250, 
  legend_position: str='bottom'):

    data = data[data['region_title'].isin(regiones)]
    chart = alt.Chart(data, title='Total de casos confirmados por región')
    
    if scale.type == 'log':
        chart = chart.transform_filter(alt.datum[feature] > 0)
    
    return (
      chart
      .mark_line(point={'size': 70})
      .encode(
        x=alt.X('fecha:T', title=x_title),
        y=alt.Y(f"{feature}:Q", title=(get_title(feature)), scale=scale),
        color=alt.Color('region_title:N', title=color_title, legend=None),
        tooltip=[
          alt.Tooltip('region_title', title='Región'),
          alt.Tooltip((f"{feature}"), title=(get_title(feature))),
          alt.Tooltip('fecha', title=x_title, type='temporal')
        ]
      )
      .configure_legend(
        fillColor='white',
        columns=8,
        strokeWidth=2,
        strokeColor='#f63366',
        cornerRadius=5,
        padding=10,
        orient=legend_position
      )
      .configure_scale(continuousPadding=5)
      .properties(
        width=width,
        height=height
      ).interactive()
    )


def get_regional_proportion_chart(
  data: pd.DataFrame, 
  regiones: list, 
  feature: str, 
  scale: alt.Scale, 
  x_title: str, 
  color_title: str, 
  padding: int=5, 
  width: int=800, 
  height: int=350, 
  legend_position: str='bottom'):
    
    data = data[data['region_title'].isin(regiones)]
    chart = alt.Chart(data, title='Total de casos confirmados por región cada 100k habitantes')
    
    if scale.type == 'log':
        chart = chart.transform_filter(alt.datum[feature] > 0)
    
    return (
      chart
      .transform_calculate(
        proportion=(alt.datum[feature] / alt.datum.poblacion * 100000)
      )
      .mark_line(point={'size': 70})
      .encode(
        x=alt.X('fecha:T', title=x_title),
        y=alt.Y('proportion:Q', title='Cantidad casos / 100k', scale=scale),
        color=alt.Color('region_title:N', title=color_title),
        tooltip=[
          alt.Tooltip('region_title', title='Región'),
          alt.Tooltip('infectados:Q', title='Casos positivos'),
          alt.Tooltip('poblacion:Q', title='Población'),
          alt.Tooltip('proportion:Q', title='Proporción', format='.2f'),
          alt.Tooltip('fecha:T', title=x_title)
        ]
      )
      .configure_scale(continuousPadding=5)
      .configure_legend(
        fillColor='white',
        columns=8,
        strokeWidth=2,
        strokeColor='#f63366',
        cornerRadius=5,
        padding=10,
        orient=legend_position,
        titleAlign='center',
        titleFontSize=16,
        labelFontSize=11
      )
      .properties(
        width=width,
        height=height
      ).interactive()
    )


def generate_regions_map(
  data: pd.DataFrame, 
  date, 
  feature: str, 
  title: str, 
  width: int=600, 
  height: int=600, 
  log_scale: bool=True) -> alt.Chart:
    
    fechas = data['fecha'].apply(lambda x: x.date())
    data = data[(fechas == date)]
    url_geojson = 'https://raw.githubusercontent.com/rubens36/covid19/master/maps/regiones.geojson'
    regions_shape = alt.Data(url=url_geojson, format=alt.DataFormat(property='features', type='json'))
    chart_data = data[(data[feature] > 0)][[feature, 'id']]

    base_chart = (
      alt.Chart(regions_shape, title='Ubicación de los casos confirmados por región')
      .mark_geoshape(stroke='black', strokeWidth=0.5, color='white')
      .encode(
        tooltip=[
          alt.Tooltip('properties.Region:N', title='Región')
        ]
      )
    )

    scale = alt.Scale(type='log', scheme='teals') if log_scale else alt.Scale(type='linear', scheme='teals')

    color_chart = (
      alt.Chart(regions_shape)
      .mark_geoshape(
        stroke='black',
        strokeWidth=0.5
      )
      .encode(
        color=alt.Color(
          f"{feature}:Q",
          title=(get_title(feature)),
          scale=scale
        ),
        tooltip=[
          alt.Tooltip('properties.Region:N', title='Región'),
          alt.Tooltip(f"{feature}:Q", title=(get_title(feature)))
        ]
      )
      .transform_lookup(
        'properties.id',
        from_=alt.LookupData(
          data=chart_data,
          key='id',
          fields=[feature]
        )
      )
    )

    single = alt.selection_single(on='mouseover')
    
    circle_chart = (
      alt.Chart(regions_shape)
      .mark_circle(
        opacity=0.4,
        color='red'
      )
      .encode(
        longitude='properties.centroid_lon:Q',
        latitude='properties.centroid_lat:Q',
        size=(
          alt.condition(single, 
            alt.Size('infectados:Q',
              scale=alt.Scale(range=[50, 4000]),
              legend=None
            ), 
            alt.value(0)
          )
        ),
        tooltip=[
          alt.Tooltip('properties.Region:N', title='Región'),
          alt.Tooltip(f"{feature}:Q", title=(get_title(feature)))
        ]
      )
      .transform_lookup(
        'properties.id',
        from_=alt.LookupData(
          data=chart_data,
          key='id',
          fields=['infectados']
        )
      )
      .properties(selection=single)
    )

    final_chart = ((base_chart + color_chart + circle_chart).configure_view(strokeWidth=0)
      .properties(
        width=width,
        height=height
      )
    )

    return final_chart


def get_international_chart(
  data: pd.DataFrame, 
  paises: list, 
  scale: alt.Scale, 
  padding: int=5, 
  width: int=800, 
  height: int=250, 
  legend_position: str='bottom'
  ):
    
    data = data[data['pais'].isin(paises)]
    chart = alt.Chart(data, title='Comparativa por países')
    chart = chart.transform_filter(alt.datum['casos'] > 0)
    
    return (
      chart
      .mark_line(point={'size': 70})
      .encode(
        x=alt.X('fecha:T', title='Fecha'),
        y=alt.Y('casos:Q', title='Casos', scale=scale),
        color=alt.Color('pais:N', title='País', legend=None),
        tooltip=[
          alt.Tooltip('pais', title='País'),
          alt.Tooltip('casos', title='Casos'),
          alt.Tooltip('fecha', title='Fecha', type='temporal')
        ]
      )
      .configure_legend(
        fillColor='white',
        columns=8,
        strokeWidth=2,
        strokeColor='#f63366',
        cornerRadius=5,
        padding=10,
        orient=legend_position
      )
      .configure_scale(continuousPadding=5)
      .properties(
        width=width,
        height=height
      ).interactive()
    )


def generate_countries_map(
  data: pd.DataFrame, 
  date, 
  interactive: bool=False, 
  width: int=600, 
  height: int=600, 
  log_scale: bool=True) -> alt.Chart:

    fechas = data['fecha'].apply(lambda x: x.date())
    data = data[(fechas == date)]

    scale = alt.Scale(type='log', scheme='teals') if log_scale else alt.Scale(type='linear', scheme='teals')
    url_country_name = 'https://raw.githubusercontent.com/alisle/world-110m-country-codes/master/world-110m-country-codes.json'
    
    country_names = pd.read_json(url_country_name).drop('name', axis=1)
    country_data = get_country_data()
    country_data = country_names.join((country_data.set_index('code')), on='code')
    
    data = pd.merge(left=country_data, right=data, left_on='name', right_on='pais').dropna()
    data = data.astype({'id':int,  'casos':int})
    
    sphere = alt.sphere()
    graticule = alt.graticule()
    source = alt.topo_feature(vd.data.world_110m.url, 'countries')
    
    sphere_chart = alt.Chart(sphere, title='Ubicación de los casos confirmados por país').mark_geoshape(fill='lightblue')
    graticule_chart = alt.Chart(graticule).mark_geoshape(stroke='white', strokeWidth=0.5)
    countries_chart = (
      alt.Chart(source)
      .mark_geoshape()
      .encode(
        color=alt.Color(
          'casos:Q',
          title='Casos',
          scale=scale,
          legend=None
        ),
          tooltip=[
            alt.Tooltip('name:N', title='País'),
            alt.Tooltip('code:N', title='Código'),
            alt.Tooltip('casos:Q', title='Casos')
          ]
      )
      .transform_lookup(
        'id',
        from_=alt.LookupData(data=data, key='id', fields=['code', 'name', 'casos'])
      )
    )

    single = alt.selection_single(on='mouseover', nearest=True, fields=['pais'], empty='all') if interactive else alt.selection_single()
    
    circle_chart = (
      alt.Chart(source)
      .mark_circle(opacity=0.4, color='red')
      .encode(
        longitude='lon:Q',
        latitude='lat:Q',
        size=(
          alt.condition(single, 
            alt.Size(
              'casos:Q',
              scale=alt.Scale(range=[50, 4000]),
              legend=None
            ), 
            alt.value(0)
          )
        ),
        tooltip=[
          alt.Tooltip('pais:N', title='País'),
          alt.Tooltip('code:N', title='Código'),
          alt.Tooltip('casos:Q', title='Casos')
        ]
      )
      .transform_lookup(
        'id',
        from_=alt.LookupData(data=data, key='id', fields=['code', 'pais', 'casos', 'lat', 'lon'])
      )
      .add_selection(single)
    )

    final_chart = (
      (sphere_chart + graticule_chart + countries_chart + circle_chart)
      .project('naturalEarth1')
      .properties(width=800, height=500)
      .configure_view(stroke=None)
    )

    return final_chart
