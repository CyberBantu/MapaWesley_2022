# Importando bibliotecas de streamlit
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Configuração inicial
st.set_page_config(layout='wide')

# Importando a base geoespacial
gdf_secao_wesley_c_agrupado_votos = gpd.read_file('gdf_secao_wesley_c_agrupado_votos.shp')

# Inserindo título
st.title('Votos de Wesley Teixeira por seção eleitoral em 2022')
st.write("Os dados utilizados nesta análise foram obtidos no site do Tribunal Superior Eleitoral (TSE). - O TSE não disponibiliza os dados Geograficos das posições das seções, os dados apresentados são estimativas de localizações e pode conter erros, porém não comprometem a confiabilidade total das informações")
# Colocando quem fez os dados
st.markdown("**Dados elaborados por Christian Basilio Oliveira.**")

# Extraindo latitude e longitude da geometria
gdf_secao_wesley_c_agrupado_votos['latitude'] = gdf_secao_wesley_c_agrupado_votos['geometry'].y
gdf_secao_wesley_c_agrupado_votos['longitude'] = gdf_secao_wesley_c_agrupado_votos['geometry'].x

# Criando filtro de Município com drop-down
municipio_selecionado = st.selectbox(
    "Selecione um Município:",
    options=['Todos'] + gdf_secao_wesley_c_agrupado_votos['Municipio'].unique().tolist(),
    index=0  # Por padrão, seleciona 'Todos'
)

# Filtrar as zonas com base no município selecionado
if municipio_selecionado == 'Todos':
    zonas_disponiveis = gdf_secao_wesley_c_agrupado_votos['Zona'].unique().tolist()
else:
    zonas_disponiveis = gdf_secao_wesley_c_agrupado_votos[
        gdf_secao_wesley_c_agrupado_votos['Municipio'] == municipio_selecionado
    ]['Zona'].unique().tolist()

# Criando filtro de Zona com drop-down (dinâmico)
zona_selecionada = st.selectbox(
    "Selecione uma Zona:",
    options=['Todas'] + zonas_disponiveis,
    index=0  # Por padrão, seleciona 'Todas'
)

# Filtrando os dados
dados_filtrados = gdf_secao_wesley_c_agrupado_votos.copy()

if municipio_selecionado != 'Todos':
    dados_filtrados = dados_filtrados[dados_filtrados['Municipio'] == municipio_selecionado]

if zona_selecionada != 'Todas':
    dados_filtrados = dados_filtrados[dados_filtrados['Zona'] == zona_selecionada]

# Calculando o total de votos
total_votos = dados_filtrados['Votos'].sum()

# Exibindo o total de votos
st.markdown(f"### Total de votos: **{total_votos:,}**")

# Titulo de mapa de votos
st.markdown('### Mapa de votos por seção eleitoral')
# Criando o mapa interativo
fig = px.scatter_mapbox(
    dados_filtrados,
    lat='latitude',
    lon='longitude',
    hover_data=['Zona', 'Seção', 'Municipio', 'Endereço', 'Votos'],
    size='Votos',  # Define o tamanho dos círculos com base na quantidade de votos
    zoom=10
)

# Ajustar o estilo do mapa
fig.update_layout(
    mapbox_style='carto-darkmatter',
    height=800,
    width=1400  # Define a largura em pixels
)
fig.update_traces(marker=dict(color='green', opacity=0.5))

# Exibindo o mapa
st.plotly_chart(fig)


# Agrupando votos por municipio
municipio_votos = gdf_secao_wesley_c_agrupado_votos.groupby('Municipio')['Votos'].sum()
# Agrupano por zonas
zona_votos = gdf_secao_wesley_c_agrupado_votos.groupby('Zona')['Votos'].sum()
# Agrupando por secao
secao_votos = gdf_secao_wesley_c_agrupado_votos.groupby('Seção')['Votos'].sum()

# Titulo de grafico de municipios com maior numero de votos
st.markdown('### Municípios com mais votos')
municipio_votos = municipio_votos.sort_values(ascending=False)
municipio_votos = municipio_votos.head(10)
municipio_votos = municipio_votos.reset_index()
fig_muni = px.bar(municipio_votos, x='Municipio', y='Votos', title='Top 10 municipios com mais votos')

st.plotly_chart(fig_muni)

# Titulo de grafico de zonas com maior numero de votos
st.markdown('### Zonas com mais votos')

# Ordena os dados e seleciona os 10 maiores
zona_votos = zona_votos.sort_values(ascending=False)
zona_votos = zona_votos.head(10).reset_index()

# Adiciona o prefixo "Zona" aos valores da coluna 'Zona'
zona_votos['Zona'] = 'Zona ' + zona_votos['Zona'].astype(str)

# Cria o gráfico
fig_zona = px.bar(zona_votos, x='Zona', y='Votos', title='Top 10 zonas com mais votos')

# Exibe o gráfico
st.plotly_chart(fig_zona)


# Exibindo informações sobre o número de seções e zonas filtradas
st.write(f'Wesley Teixeira teve votos em {dados_filtrados["Seção"].nunique()} seções eleitorais, de 952 no Estado.')
st.write(f'Presença em {dados_filtrados["Zona"].nunique()} Zonas de votação de 165 no Estado.')
