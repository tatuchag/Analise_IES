import os
import pandas as pd 
import numpy as np 
import matplotlib
import matplotlib.pyplot as plt 
import seaborn as sns 
import plotly
import plotly.express as px
import streamlit as st
import geobr
import geopandas as gpd
#from st_aggrid import AgGrid
#from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

# metricas
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, make_scorer
from sklearn.preprocessing import RobustScaler

# ------------------------------------------------------------------------
# Analise IES - 2022
# ------------------------------------------------------------------------
st.set_page_config(page_title='Analise IES', 
                    page_icon=':school:', 
				    layout='wide', 
                    initial_sidebar_state='expanded')


st.title(':school: Mapa das Instituições de Ensino Superior :flag-br:')
st.subheader('Escopo: Todas as IES existentes no Brasil')
st.subheader("Dados de 2022")
st.markdown("---")


# Cabeçalho
titulo_map =  '<p style="font-family:Arial; color:Black; font-size: 18px;">Esta aba apresenta informações consolidadas sobre as Instituições de Ensino Superior (IES) públicas e privadas no Brasil, em todas as esferas (federal, estadual e municipal), conforme suas características organizacionais sob enfoque acadêmico e administrativo.<br><br>Considerando os dados de 2022: o Brasil possui mais de 2,5 mil IES em constante mudança e expansão, que ofertaram cerca de 22 milhões de vagas (25% e 75% nas modalidades presencial e EAD, respectivamente) em mais de 45 mil cursos de diferentes áreas do conhecimento.</p>'
st.markdown(titulo_map, unsafe_allow_html=True)


# ------------------------------------------------------------------------
# Parametros plots seaborn
# ------------------------------------------------------------------------
sns.set(style="darkgrid")


# ------------------------------------------------------------------------
# Funções para Carregar dados 
# ------------------------------------------------------------------------

# dados IES
@st.cache_data
def carrega_ies():
    colunas_CO = ['CO_REGIAO_IES',  'CO_UF_IES', 'CO_MESORREGIAO_IES', 'CO_MICRORREGIAO_IES',
    'CO_MANTENEDORA', 'CO_IES', 'COD_IBGE', 'IN_CAPITAL_IES', 'NU_CEP_IES']
    dict_dtype = {column : 'str'  for column in colunas_CO}
    ies = pd.read_csv('./arquivos/dados_ies_consolidado.csv', sep='|', dtype = dict_dtype, low_memory=False)
    return ies

# dados IES agregados por UF
@st.cache_data
def carrega_ies_agg_UF():
    ies_agg_UF = pd.read_csv('./arquivos/dados_IES_agg_UF.csv', sep='|', 
                   low_memory=False)
    ies_agg_UF = ies_agg_UF.rename(columns={'Total_mun':'Total_mun_IES',
                                        'Total_Pop_IES':'Total_Pop_UF_IES',
                                        'Total_Pop_IBGE_2022':'Total_Pop_UF',
                                        'Total_Mun_IBGE_2022':'Total_Mun_UF',
                                        'Total_Meso':'Total_Meso_UF',
                                        'Total_Micro':'Total_Micro_UF',
                                        'Prop_Mun':'Cob_Mun_com_IES',
                                        'Cob_Meso':'Cob_Meso_com_IES',
                                        'Cob_Micro':'Cob_Micro_com_IES'})

    ies_agg_UF = ies_agg_UF[['SG_UF_IES', 'Total_Pop_UF', 'Total_Mun_UF', 'Total_Meso_UF', 'Total_Micro_UF','Total_IES', 'Total_Priv', 'Total_Publ','Total_mun_IES', 'Total_Pop_UF_IES','Total_Meso_IES','Total_Micro_IES','Cob_Mun_com_IES','Cob_Meso_com_IES','Cob_Micro_com_IES']]
    return ies_agg_UF
    
    
    
# dados IES agregados por Região    
@st.cache_data
def carrega_ies_agg_regiao():
    ies_agg_regiao = pd.read_csv('./arquivos/dados_IES_agg_Regiao.csv', sep='|', 
                   low_memory=False)
    ies_agg_regiao = ies_agg_regiao.rename(columns={'Total_mun':'Total_mun_IES',
                                        'Total_Pop_IES':'Total_Pop_UF_IES',
                                        'Total_Pop_IBGE_2022':'Total_Pop_UF',
                                        'Total_Mun_IBGE_2022':'Total_Mun_UF',
                                        'Total_Meso':'Total_Meso_UF',
                                        'Total_Micro':'Total_Micro_UF',
                                        'Prop_Mun':'Cob_Mun_com_IES',
                                        'Cob_Meso':'Cob_Meso_com_IES',
                                        'Cob_Micro':'Cob_Micro_com_IES'})

    ies_agg_regiao = ies_agg_regiao[['REGIAO', 'NOME_REGIAO', 'Total_Pop_UF', 'Total_Mun_UF', 'Total_Meso_UF','Total_Micro_UF','Total_IES', 'Total_Priv', 'Total_Publ','Total_mun_IES', 'Total_Pop_UF_IES','Total_Meso_IES','Total_Micro_IES']]
    return ies_agg_regiao
    

# ------------------------------------------------------------------------
# Carregar dados
# ------------------------------------------------------------------------
ies = carrega_ies()
ies_agg_UF = carrega_ies_agg_UF()
ies_agg_regiao = carrega_ies_agg_regiao()


# ------------------------------------------------------------------------
# Prepara dados IES agregados por campos especificos
# ------------------------------------------------------------------------				 

# Total IES
total_ies = ies['NO_IES'].count()

# total de IES por Categoria 
total_ies_cat_adm = ies['Tipo_Cat_Admn'].value_counts()
perc_ies_cat_adm = round(total_ies_cat_adm / total_ies * 100,2) 
distr_ies_cat_br = pd.DataFrame({'Total IES'   : total_ies_cat_adm,
                                 'Total IES (%)':  perc_ies_cat_adm}).reset_index()
distr_ies_cat_br = distr_ies_cat_br.rename(columns={'Tipo_Cat_Admn':'Categoria Administrativa'})                                 

# total de IES por Organizacao Academica
total_ies_org_acad = ies['Tipo_Org_Acad'].value_counts()
perc_ies_org_acad = round(total_ies_org_acad / total_ies * 100,2) 
distr_ies_org_acad = pd.DataFrame({'Total IES'   : total_ies_org_acad,
                                   'Total IES (%)':  perc_ies_org_acad}).reset_index()
distr_ies_org_acad = distr_ies_org_acad.rename(columns={'Tipo_Org_Acad':'Organização Acadêmica'})

# total de IES por Organização e Categoria Adm
distr_cat_org_br = ies.groupby(['Tipo_Cat_Admn','Tipo_Org_Acad'])['CO_IES'].count().reset_index()
distr_cat_org_br = distr_cat_org_br.rename(columns={'CO_IES':'Total_IES'})

#--------------------------------------------------------------------------------------------
# Prepara dados IES agregados por UF
#------------------------------------------------------------------------------------------               
# total de IES por UF 
tot_ies_uf = ies.groupby('SG_UF_IES')['NO_IES'].count()
                  
# total de IES por UF e Organização 
tot_ies_org_uf = ies.groupby(['SG_UF_IES','Tipo_Org_Acad'])['NO_IES'].count()
perc_ies_org_uf = round(tot_ies_org_uf / tot_ies_uf *100,2)
distr_ies_org_uf = pd.DataFrame({'Total_Org'   : tot_ies_org_uf,
                                 'Total_Org_p': perc_ies_org_uf}).reset_index()

# total de IES por UF e Tipo Instituicao
tot_ies_tp_uf = ies.groupby(['SG_UF_IES','TIPO_INST'])['NO_IES'].count()
perc_ies_tp_uf = round(tot_ies_tp_uf / tot_ies_uf *100,2)
distr_ies_tp_uf = pd.DataFrame({'Total_IES'   : tot_ies_tp_uf,
                                'Total_IES_p': perc_ies_tp_uf}).reset_index()
                                
#--------------------------------------------------------------------------------------------
# Prepara dados IES agregados por Regiao
#------------------------------------------------------------------------------------------
tot_ies_regiao = ies.groupby('NO_REGIAO_IES')['NO_IES'].count()

# Total IES por Orgao
tot_ies_org_regiao = ies.groupby(['NO_REGIAO_IES','Tipo_Org_Acad'])['NO_IES'].count()
perc_ies_org_regiao = round(tot_ies_org_regiao / tot_ies_regiao *100,2)
distr_ies_org_regiao = pd.DataFrame({'Total_Org'   : tot_ies_org_regiao,
                                 'Total_Org_p': perc_ies_org_regiao}).reset_index()

# Total IES por Tipo Instituição                        
tot_ies_tp_regiao = ies.groupby(['NO_REGIAO_IES','TIPO_INST'])['NO_IES'].count()
perc_ies_tp_regiao = round(tot_ies_tp_regiao / tot_ies_regiao *100,2)
distr_ies_tp_regiao = pd.DataFrame({'Total_IES'   : tot_ies_tp_regiao,
                                'Total_IES_p': perc_ies_tp_regiao}).reset_index()
                         
#--------------------------------------------------------------------------------------------
# Prepara tabs
#------------------------------------------------------------------------------------------          
t_mapa_i, t_mapa, t_br, t_reg, t_uf, t_cob, t_ind, t_corr, t_regr = st.tabs(['Mapa Interativo',
                                                        'Mapa', 
                                                        'Brasil', 
                                                        'Região', 
                                                        'UF',
                                                        'Coberturas',
                                                        'Indicadores',
                                                        'Correlação',
                                                        'Regressão'])
css = '''
<style>
.stTabs [data-baseweb="tab-list"] {
        color:#1221c4;
		gap: 20px; } # afastamento entre as tabs

	.stTabs [data-baseweb="tab"] {
		height: 50px;
        white-space: pre-wrap;
		background-color: white;
		border-radius: 4px 4px 4px 4px;
		gap: 10px;
		padding-top: 10px;
		padding-bottom: 10px;
    }

	.stTabs [aria-selected="true"] {
        color:#e63212;
  		background-color: #f7eb0a; #cor de fundo da tab selecionada;
        border-radius: 4px 4px 4px 4px;
        gap: 10px;
	}   
</style>
'''              
st.markdown(css, unsafe_allow_html=True)
              
# -----------------------------------------------------------------------------------
# Tab 01
# Mapa 01: Distribuição IES no Brasil (2022)
# -----------------------------------------------------------------------------------

with t_mapa_i:
    titulo_map =  '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Mapa com Localização de todas as Instituições de Ensino Superior - Brasil</b></p>'
    st.markdown(titulo_map, unsafe_allow_html=True)
    with open('./data/ies_interativo.html', 'r', encoding='utf-8') as file:
        html_code = file.read()

    # Exibe o conteúdo HTML
    st.components.v1.html(html_code, height=800, scrolling=True)
             
# -----------------------------------------------------------------------------------
# Tab 02
# Mapa 01: Distribuição IES no Brasil (2022)
# -----------------------------------------------------------------------------------
with t_mapa:

    titulo_map01 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Visualização da Distribuição de todas as Instituições de Ensino Superior - Brasil</b></p>'
    st.markdown(titulo_map01, unsafe_allow_html=True)

    # cria o dataframe das IES publicas e privadas
    df_publica = ies[ies['TIPO_INST'] == 'Pública']
    df_privada = ies[ies['TIPO_INST'] == 'Privada']
    states = geobr.read_state(code_state='all')

    fig, ax = plt.subplots(figsize=(6, 6))
    states.boundary.plot(ax=ax, linewidth=0.4, color='black')
    ax.scatter(df_privada['LNG'], df_privada['LAT'], color='#1b9e77', label='Instituição Privada', s=10, alpha=0.7)
    ax.scatter(df_publica['LNG'], df_publica['LAT'], color='#d95f02', label='Instituição Pública', s=10, alpha=0.7)
    ax.set_xlim(-75, -30)  # Ajuste os limites do mapa de acordo com a localização desejada
    ax.set_ylim(-35, 5)
    #ax.set_xlabel('Longitude')
    #ax.set_ylabel('Latitude')
    ax.tick_params(axis='y', labelsize=6)
    ax.tick_params(axis='x', labelsize=6)
    #ax.set_title('Mapa do Brasil com Instituições de Ensino Superior')
    ax.legend(loc='best', fontsize=8)
    st.pyplot(fig,  use_container_width=True)
    plt.close()

    # -------------------
    # Analise
    # -------------------
    st.subheader('Análise:')
    
    write_map01a = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">Nota-se, claramente em todo o país, a predominância de instituições privadas com relação às instituições públicas, com maior concentração tanto das privadas como das públicas nas Regiões Sul, Sudeste e Nordeste.</p>'

    write_map01b = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">As instituições públicas, embora em menor quantidade total, se encontram fortemente concentradas no estado de São Paulo e Rio de Janeiro.</p>'

    write_map01c = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">São pouquíssimas as instituições públicas nas Regiões Norte e Centro-Oeste.</p>'

    st.markdown(write_map01a, unsafe_allow_html=True)
    st.markdown(write_map01b, unsafe_allow_html=True)
    st.markdown(write_map01c, unsafe_allow_html=True)
    st.markdown("---")

#--------------------------------------------------------------------------------------
# Tab 03: Brasil
# Plot 01: Distribuição da Qtd de IES por Org Acadêmica e Cat Administrativa
# Plot 02:  
#--------------------------------------------------------------------------------------    

with t_br:
    titulo_br01 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Qtd de IES por Categ. Administrativa e Org. Acadêmica</b></p>'
    st.markdown(titulo_br01, unsafe_allow_html=True)
    
    text = '<p style="font-family:Calibri Light; color:black; font-size: 16px;">Alguns conceitos são necessários: uma Universidade é uma instituição que oferece programas acadêmicos em várias áreas de conhecimento, enquanto que uma Faculdade oferece programas acadêmicos em uma área específica. Os Centros Universitários são maiores que as Faculdades e menores que as Universidades, e são uma espécie de estágio pelo qual uma faculdade precisa passar para se tornar uma universidade.</p>'
    st.markdown(text, unsafe_allow_html=True)
    
    
    
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(distr_ies_cat_br, hide_index=True, use_container_width=True)
    with col2:
        st.dataframe(distr_ies_org_acad, hide_index=True, use_container_width=True)
    
    titulo_br02 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Visualização Gráfica da Distribuição de IES</b></p>'
    st.markdown(titulo_br02, unsafe_allow_html=True)
    fig = px.bar(distr_cat_org_br,
                 y='Tipo_Cat_Admn', 
                 x='Total_IES', 
                 color='Tipo_Org_Acad',
                 color_discrete_sequence=px.colors.sequential.Viridis_r,
                 barmode = 'stack', width=1100, height=700,
                 labels=dict(Tipo_Org_Acad = 'Organização Acadêmica'))
    fig.update_layout(yaxis=dict(title='', titlefont_size=30, tickfont_size=20),
                      xaxis=dict(title='', tickfont_size=20),      
                      legend=dict(x=0.1,y=-0.6, font = dict(size = 18))) 
    fig.update_xaxes(tickangle=0)
    fig.update_layout(plot_bgcolor='#dbe0f0') 
    fig.update_layout(hoverlabel=dict(bgcolor="white", 
                                      font_size=22,
                                      font_family="Rockwell"))	
    st.plotly_chart(fig, use_container_width=True) 
    plt.close()
    
    # -------------------
    # Analise
    # -------------------
    st.subheader('Análise:')
    write_br01 = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">Observa-se claramente a predominância de IES privadas no país, enquanto que as  públicas representam apenas 11% do total. Com relação à organização acadêmica destas instituições, as Faculdades (76%) e Centros Universitários (15%) somam 2.349 IES - quase 91% do total de todas as instituições.</p>'
    st.markdown(write_br01, unsafe_allow_html=True)
    st.markdown("---")

#--------------------------------------------------------------------------------------
# Tab 04: Região
# Plot 01: Distribuição da Qtd de Instituições de Ensino Superior por Região 
# Plot 02: Proporção de IES por Organização Acadêmica - Regioes 
# Plot 03: Distribuição da Qtd de IES por Categoria - Regiao
# Plot 04: Proporção de IES por Categoria - Regiao
#--------------------------------------------------------------------------------------    
with t_reg:
    
    # Plot 01 - Distribuição da Qtd de Instituições de Ensino Superior 
    titulo_reg01 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Qtd de IES por Região </b></p>'
    st.markdown(titulo_reg01, unsafe_allow_html=True)

    fig = px.bar(ies_agg_regiao.sort_values(by='Total_IES', ascending=False),
             x='NOME_REGIAO', 
             y='Total_IES', 
             color='Total_IES',
             color_continuous_scale='viridis_r',
             width=1100, height=600,
             text='Total_IES')
    fig.update_traces(textfont_size=20, textangle=0, textposition="inside")
    fig.update_layout(yaxis=dict(title='Total IES', titlefont_size=30, tickfont_size=12),
                  xaxis=dict(title='', tickfont_size=20),
                  coloraxis_showscale=False)
    fig.update_xaxes(tickangle = 0)
    fig.update_layout(plot_bgcolor='#dbe0f0') 
    fig.update_layout(hoverlabel=dict(bgcolor="white", 
                                  font_size=18,
                                  font_family="Rockwell"))	
    st.plotly_chart(fig, use_container_width=True)
    plt.close()
    st.markdown("---")  
    
    
    # Plot 02: Proporção de IES por Organização Acadêmica 
    titulo_reg02 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Proporção de IES por Organização Acadêmica - Regiões</b></p>'
    st.markdown(titulo_reg02, unsafe_allow_html=True)
    
    fig = px.bar(distr_ies_org_regiao.sort_values(by='Total_Org_p', ascending=False),
             x='NO_REGIAO_IES', 
             y='Total_Org_p', 
             color='Tipo_Org_Acad',
             color_discrete_sequence=px.colors.qualitative.Dark2,
             barmode = 'group', width=1000, height=800)
    fig.update_layout(yaxis=dict(title='Proporção %', titlefont_size=25, tickfont_size=20),
                  xaxis=dict(title='', tickfont_size=20),      
                  legend=dict(x=0.25,y=-0.4, font = dict(size = 18))) 
    fig.update_layout(plot_bgcolor='#dbe0f0') 
    fig.update_layout(hoverlabel=dict(bgcolor="white", 
                                      font_size=22,
                                      font_family="Rockwell"))
    st.plotly_chart(fig, use_container_width=True)
    plt.close()
    
    # -------------------
    # Analise
    # -------------------
    st.subheader('Análise:')
    write_reg01 = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">Observa-se a prevalência de faculdades e centros universitários em todas as regiões. Além disso, em todas as regiões, a ordem proporcional é sempre a mesma: faculdades, centro-universitários, universidades, Institutos Federais e CEFETs. Quando estratifica-se a análise retirando as faculdades, pode-se observar que a região sul possui, entre os tipos, a maior proporção de universidades que as demais regiões do país. </p>'
    st.markdown(write_reg01, unsafe_allow_html=True)
    st.markdown("---")
    
    # Plot 03: Distribuição da Qtd de IES por Categoria 
    # Plot 04: Proporção de IES por Categoria 
    # Inserir titulos 
    col1, col2 = st.columns(2)
    with col1:
        titulo_reg03 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Qtd de IES por Categoria - Região</b></p>'
        st.markdown(titulo_reg03, unsafe_allow_html=True)
    with col2:
        titulo_reg04 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Proporção de IES por Categoria - Região</b></p>'
        st.markdown(titulo_reg04, unsafe_allow_html=True)
            
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(distr_ies_tp_regiao.sort_values(by='Total_IES', ascending=False),
        x='NO_REGIAO_IES', 
        y='Total_IES', 
        color='TIPO_INST',
        color_discrete_sequence=px.colors.qualitative.Dark2,
        barmode = 'group', width=1000, height=800,
        text='Total_IES')
        fig.update_traces(textfont_size=18, textangle=0, textposition="inside")
        fig.update_layout(yaxis=dict(title='Total IES', titlefont_size=25, tickfont_size=18),
        xaxis=dict(title='', tickfont_size=18),      
        legend=dict(x=0.65,y=0.9, font = dict(size = 20)))
        fig.update_layout(plot_bgcolor='#dbe0f0') 
        fig.update_layout(hoverlabel=dict(bgcolor="white", font_size=18,font_family="Rockwell"))
        st.plotly_chart(fig, use_container_width=True)
        plt.close()

    with col2:
        fig = px.bar(distr_ies_tp_regiao.sort_values(by='Total_IES_p', ascending=False),
        x='NO_REGIAO_IES', 
        y='Total_IES_p', 
        color='TIPO_INST',
        color_discrete_sequence=px.colors.qualitative.Dark2,
        barmode = 'group', width=1000, height=800,
        text='Total_IES_p')
        fig.update_traces(textfont_size=18, textangle=0, textposition="inside")
        fig.update_layout(yaxis=dict(title='Proporção %', titlefont_size=25, tickfont_size=18),
        xaxis=dict(title='', titlefont_size=25, tickfont_size=18),      
        #legend=dict(x=0.25,y=-0.2, font = dict(size = 20))    
        ) 
        fig.update_layout(plot_bgcolor='#dbe0f0') 
        fig.update_layout(showlegend=False)
        fig.update_layout(hoverlabel=dict(bgcolor="white", font_size=22,font_family="Rockwell"))
        st.plotly_chart(fig, use_container_width=True)
        plt.close()
        
    # -------------------
    # Analise
    # -------------------
    st.subheader('Análise:')
    write_reg02 = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">Em números absolutos, quando analisado por categoria administrativa, o que se observa é o mesmo comportamento da distribuição geral das IES nas regiões do país. Uma hierarquização em que a região Sudeste apresenta o maior número de instituições, tanto públicas quanto privadas, seguido das regiões Nordeste, Sul, Centro-Oeste e Norte.</p>'
    write_reg03 = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">Mas números absolutos podem enganar. O gráfico à direita, com as mesmas informações do ponto de vista proporcional em cada região, demonstra que o Sudeste passa a ser a região com a menor proporção de IES privadas e, consequentemente, a maior proporção de IES públicas. Ou seja, ainda que em termos absolutos a região apresente o maior número de IES privadas do país, também é a região com a menor proporção. Isso provavelmente se explica pelos estados do RJ e SP, que possuem uma proporção de IES públicas mais alta do que a maioria dos estados.</p>'
    st.markdown(write_reg02, unsafe_allow_html=True)
    st.markdown(write_reg03, unsafe_allow_html=True)

    st.markdown("---")
    

    

#--------------------------------------------------------------------------------------
# Tab 05: UF
# Plot 01: Distribuição da Qtd de Instituições de Ensino Superior por UF
# Plot 02: Proporção de IES por Organização Acadêmica - UF
# Plot 03:  Distribuição da Qtd de IES por Categoria  - UF
# Plot 04: Proporção de IES por Categoria - UF
#--------------------------------------------------------------------------------------    

with t_uf:
 
    # Plot 01:  Distribuição da Qtd de Instituições de Ensino Superior 
    titulo_uf01 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Qtd de IES por UF</b></p>'
    st.markdown(titulo_uf01, unsafe_allow_html=True)

    fig = px.bar(ies_agg_UF.sort_values(by='Total_IES', ascending=False),
             x='SG_UF_IES', 
             y='Total_IES', 
             color='Total_IES',
             color_continuous_scale='viridis_r',
             width=1100, height=600)
    fig.update_layout(yaxis=dict(title='Total IES', titlefont_size=30, tickfont_size=12),
                  xaxis=dict(title='', tickfont_size=20),
                  coloraxis_showscale=False)
    fig.update_xaxes(tickangle = -45)
    fig.update_layout(plot_bgcolor='#dbe0f0') 
    fig.update_layout(hoverlabel=dict(bgcolor="white", 
                                  font_size=22,
                                  font_family="Rockwell"))	
    st.plotly_chart(fig, use_container_width=True)
    plt.close()
    
    # -------------------
    # Analise
    # -------------------   
    st.subheader('Análise:')
    write_uf01 = '<p style="font-family:Calibri LightCalibri Light; color:black; font-size: 18px;">As IES estão presentes em todos os estados do território nacional, em maior número nos estados da região sudeste do país (1.098 IES, 42,31%), condizente com a proporção populacional da região que é de aproximadamente 40% da população total do país.</p>'
    st.markdown(write_uf01, unsafe_allow_html=True)
    st.markdown("---")
    
    # Plot 02: Proporção de IES por Organização Acadêmica
    titulo_uf02 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Proporção de IES por Organização Acadêmica - UF </b></p>'
    st.markdown(titulo_uf02, unsafe_allow_html=True)

    fig = px.bar(distr_ies_org_uf.sort_values(by='Total_Org_p', ascending=False),
                 x='SG_UF_IES', 
                 y='Total_Org_p', 
                 color='Tipo_Org_Acad',
                 color_discrete_sequence=px.colors.qualitative.Dark2,
                 barmode = 'group', width=1000, height=800)
    fig.update_layout(yaxis=dict(title='Proporção %', titlefont_size=25, tickfont_size=20),
                     xaxis=dict(title='', tickfont_size=20),      
                     legend=dict(x=0.3,y=-0.4, font = dict(size = 18)))
    fig.update_layout(plot_bgcolor='#dbe0f0') 
    fig.update_layout(hoverlabel=dict(bgcolor="white", 
                                      font_size=22,
                                      font_family="Rockwell"))
    st.plotly_chart(fig, use_container_width=True)
    plt.close()
                 
    # -------------------
    # Analise
    # -------------------
    st.subheader('Análise:')
    write_uf02a = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">A distribuição das IES nos estados, por tipo de organização, segue o mesmo padrão encontrado nos dados agrupados em nível nacional, com predominância significativa de instituições do tipo faculdade. Contudo, essa proporção tem variação entre os estados: enquanto a maioria dos estados possuem majoritariamente faculdades e centros universitários; os estados de Roraima, Rio Grande do Sul, Mato Grosso do Sul e Amapá destacam-se por possuir universidades como o segundo tipo de IES mais prevalente.</p>'
    write_uf02b = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">Amapá, curiosamente, é o unico Estado sem a existência de centro universitário, enquanto que apenas os estados de RJ e MG possuem CEFETs federais.</p>'
    st.markdown(write_uf02a, unsafe_allow_html=True)
    st.markdown(write_uf02b, unsafe_allow_html=True)
    st.markdown("---")
    
    # Plot 03:  Distribuição da Qtd de IES por Categoria 
    titulo_uf03 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Qtd de IES por Categoria - UF</b></p>'
    st.markdown(titulo_uf03, unsafe_allow_html=True)

    fig = px.bar(distr_ies_tp_uf.sort_values(by='Total_IES', ascending=False),
                 x='SG_UF_IES', 
                 y='Total_IES', 
                 color='TIPO_INST',
                 color_discrete_sequence=px.colors.qualitative.Dark2,
                 barmode = 'group', width=1000, height=600)
    fig.update_layout(yaxis=dict(title='Total IES', titlefont_size=25, tickfont_size=22),
                      xaxis=dict(title='', tickfont_size=20),      
                      legend=dict(x=0.35,y=0.9, font = dict(size = 24)))
    fig.update_layout(plot_bgcolor='#dbe0f0') 
    fig.update_layout(hoverlabel=dict(bgcolor="white", 
                                      font_size=22,
                                      font_family="Rockwell"))
    st.plotly_chart(fig, use_container_width=True)
    plt.close()
    st.markdown("---")
        
    # Plot 04: Proporção de IES por Categoria 
    titulo_uf04 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Distribuição da Proporção de IES por Categoria - UF</b></p>'
    st.markdown(titulo_uf04, unsafe_allow_html=True)

    fig = px.bar(distr_ies_tp_uf.sort_values(by='Total_IES_p', ascending=False),
                 x='SG_UF_IES', 
                 y='Total_IES_p', 
                 color='TIPO_INST',
                 color_discrete_sequence=px.colors.qualitative.Dark2,
                 barmode = 'stack', width=1000, height=600)
    fig.update_layout(yaxis=dict(title='Proporção %', titlefont_size=20, tickfont_size=22),
                      xaxis=dict(title='', titlefont_size=25, tickfont_size=22),    
                      legend=dict(x=0.35,y=0.5, font = dict(size = 24))) # 
    fig.update_layout(plot_bgcolor='#dbe0f0') 
    fig.update_layout(hoverlabel=dict(bgcolor="white", 
                                      font_size=22,
                                      font_family="Rockwell"))
    st.plotly_chart(fig, use_container_width=True)
    plt.close()
    
    # -------------------
    # Analise
    # -------------------
    st.subheader('Análise:')
    write_uf03a = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">Em nível nacional, as instituições privadas (com e sem fins lucrativos) ocupam a proporção de 87,98% do total de IES no Brasil. Pode-se observar um cenário aproximado com predominância de instituições privadas quando analisado por UF, destacando-se o estado de MT com a maior proporção de instituições privadas (94,44%) e Roraima com a menor proporção (66.67%).</p>'
    write_uf03b = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">Observa-se que a proporção entre IES público e privadas em cada estado possui um variação, como por exemplo, as IES públicas que tem uma prevalência entre 5,56%  em MT e 33,33% em RR. Ainda assim, é possível identificar que na maioria dos estados (67%) a proporção de IES públicas não chega a 10%.</p>'
    st.markdown(write_uf03a, unsafe_allow_html=True)
    st.markdown(write_uf03b, unsafe_allow_html=True)
    st.markdown("---")
    

#--------------------------------------------------------------------------------------
# Tab 06: Coberturas
# Plot 01: Cobertura de Municipios 
# Plot 02: Cobertura de Mcrorregioes
# -----------------------------------------------------------------------------------

with t_cob:
    # Plot 01: Cobertura de Municipios 
    titulo_cob01 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Cobertura de Municipios com existência de IES</b></p>'
    st.markdown(titulo_cob01, unsafe_allow_html=True)

    fig = plt.figure(figsize=(20, 15))
    axes = fig.add_subplot(111)
    cores = sns.color_palette("mako", 27) # magma
    interval_x = np.arange(0,625,25) # intervalo eixos população
    interval_y = np.arange(0,60000000,5000000) # intervalo eixos população

    g = sns.barplot(x='SG_UF_IES', 
                    y='Total_IES', 
                    data=ies_agg_UF.sort_values(by='Total_IES', ascending=False),
                    palette = cores, 
                    label='Total_IES')
    axes.set_ylabel('Total IES', fontsize=18)
    axes.yaxis.set_ticks(interval_x)
    axes.set(xlabel='') 

    ax2 = axes.twinx()
    ax2.plot(ies_agg_UF.sort_values(by='Total_IES', ascending=False)['SG_UF_IES'], 
             ies_agg_UF.sort_values(by='Total_IES', ascending=False)['Total_Pop_UF_IES'],
            color='#ffff00', label='Total_Pop_IES')
    ax2.set_ylabel("População dos municipios com IES", fontsize=20)

    ax3 = axes.twinx()
    ax3.plot(ies_agg_UF.sort_values(by='Total_IES', ascending=False)['SG_UF_IES'], 
             ies_agg_UF.sort_values(by='Total_IES', ascending=False)['Total_Pop_UF'],
            color='#ff8000', label='Total_Pop_IBGE')
    #ax3.set_ylabel("População total da UF")

    axes.grid(visible=False)

    ax2.grid(visible=True, linestyle = "dashed", color='white')
    ax2.yaxis.set_ticks(interval_y)
    #ax2.yaxis.set_visible(False) # remove yticks

    ax3.grid(visible=False)
    ax3.yaxis.set_ticks(interval_y)
    ax3.yaxis.set_visible(True) # remove yticks

    lines1, labels1 = axes.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax3.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc="upper center", fontsize=18)

    valores_prop_mun =  ies_agg_UF.sort_values(by='Total_IES', ascending=False)['Cob_Mun_com_IES'].values
    for i, p in enumerate(axes.patches):
            axes.annotate('{:,.0f}%'.format(valores_prop_mun[i]), 
                          (p.get_x()+0.1, p.get_height()+10) , 
                         fontsize=16, weight='bold', color='#730099')

    st.pyplot(fig)
    plt.close()

    # -------------------
    # Analise
    # -------------------
    st.subheader('Análise:')
    write_cob01 = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">O gráfico acima mostra o percentual de municipios com a existência de pelo menos uma instituição de ensino. Desta forma, embora SP tenha o maior número de instituições, é o estado do Rio de Janeiro que possui a maior cobertura de IES (32% dos seus municípios com alguma instituição), seguido pelos estados do Espírito Santo e São Paulo, ambos com cobertura de 24%. Na PB e RN, apenas 4 a 5% dos municípios possuem algum tipo de IES</p>'
    st.markdown(write_cob01, unsafe_allow_html=True)
    st.markdown("---")
    
    
    # Plot 02: Cobertura de Microregioes 
    titulo_cob02 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Cobertura de Microrregiões com existência de IES</b></p>'
    st.markdown(titulo_cob02, unsafe_allow_html=True)

    # prepara dados
    colunas_int = ['SG_UF_IES','Total_IES', 'Cob_Mun_com_IES','Cob_Meso_com_IES','Cob_Micro_com_IES']
    df_coberturas = ies_agg_UF[colunas_int]
    df_coberturas_m = df_coberturas.melt(id_vars=['SG_UF_IES'])

    f, axes = plt.subplots(1, 1,  figsize=(20, 10))
    cores = sns.color_palette("Paired")

    dados = df_coberturas_m[df_coberturas_m['variable'].isin(['Cob_Mun_com_IES','Cob_Micro_com_IES'])]

    # ordem das UFs no eixo x
    my_order = list(df_coberturas.sort_values(by='Total_IES', ascending=False)['SG_UF_IES'])

    sns.barplot(x='SG_UF_IES', y='value', hue='variable', 
                data=dados,
                ax=axes, 
                palette=cores, 
                order=my_order,
                hue_order=['Cob_Micro_com_IES','Cob_Mun_com_IES'])

    #axes.set_title('Distribuição IES no Brasil - Cobertura Microrregiões (2022)', fontsize=20)
    axes.set_xlabel('')
    axes.set_ylabel("Percentual (%)", fontsize = 20)
    xlocs, xlabels = plt.xticks()
    ylocs, ylabels = plt.yticks()
    plt.setp(xlabels, rotation=0, fontsize=15)
    plt.setp(ylabels, fontsize=15)

    dados2 = df_coberturas[['SG_UF_IES','Total_IES']].sort_values(by='Total_IES', ascending=False)
    x=dados2['SG_UF_IES']
    y=dados2['Total_IES']
    axes2 = axes.twinx()
    axes2.plot(x, y, color='#cc0000', label='Total IES')
    axes2.set_ylabel("Total de IES na UF", fontsize = 20)
    axes2.grid(visible=False)

    for i, j in zip(x, y):
        axes2.text(i,j, str(j), ha='center', va='bottom', color='#cc0000', fontsize=14)
        axes.legend(loc='best', fontsize=18)
    st.pyplot(f)
    plt.close()
    

    # -------------------
    # Analise
    # -------------------
    st.subheader('Análise:')
    write_cob02a = '<p style="font-family:Calibri Light; color:black; font-size: 18px;">O gráfico acima mostra a cobertura de municípios em microrregiões com a existência de pelo menos uma instituição de ensino. Desta forma, se tem uma razoável cobertura de IES em boa parte dos estados, ao se considerar esta perspectiva de microrregiões.</p>'
    write_cob02b = '<p style="font-family:Calibri Light; color:red; font-size: 16px;">Obs. a linha vermelha representa o total de instituições de ensino em cada UF.</p>'

    st.markdown(write_cob02a, unsafe_allow_html=True)
    st.markdown(write_cob02b, unsafe_allow_html=True)
    st.markdown("---")
    
    
# -----------------------------------------------------------------------------------
# Tab 07
# Grafico dispersao
# -----------------------------------------------------------------------------------
# Carrega dataframe

@st.cache_data
def carrega_ies_ind_mun():
    col = ['Cod_Mesorregiao','Cod_Microrregiao','COD_IBGE','CAPITAL']
    dict_dtype = {column : 'str'  for column in col}
    ies_ind_mun = pd.read_csv('./arquivos/total_ies_com_ind_mun.csv', sep='|', 
                   dtype = dict_dtype, low_memory=False)
    return ies_ind_mun
    
    
@st.cache_data
def carrega_definicao_ind():    
    def_indicadores = pd.read_csv('./arquivos/definicao_indicadores.csv', sep='|', 
    low_memory=False, encoding='iso-8859-1')
    return def_indicadores

# carregar dados    
ies_ind_mun =  carrega_ies_ind_mun()    
def_indicadores = carrega_definicao_ind()
lista_indicadores = list(def_indicadores['Indicador'])
    
with t_ind:
    titulo_01 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Relação dos Indicadores Sociais com Qtd de IES nos municipios</b></p>'
    st.markdown(titulo_01, unsafe_allow_html=True)
    
    st.write("Selecionando-se um indicador social da lista disponível, será apresentado um gráfico de dispersão deste indicador com o total de IES em cada município. O objetivo é detectar se há alguma relação do indicador com o total de IES. Ressalta-se que municípios sem IES não estão contemplados no gráfico; os indicadores são do ano base de 2010. Abaixo do gráfico há uma tabela com a lista da descrição de todos os indicadores sociais.") 
    
    # prepara lista de opções de indicadores
    col1, col2, col3 = st.columns(3)
    with col1:
        label01 = '<p style="font-family:Courier; color:#992600; font-size: 16px;"><b>Selecione um indicador:</b></p>'
        st.markdown(label01, unsafe_allow_html=True) 
    with col2:
        ind_selected = st.selectbox(label="Selecione um indicador:", options=lista_indicadores, label_visibility="collapsed", index=218)
    with col3:    
        st.subheader(':dart:')
    
    # escreve o indicador
    nome_ind = def_indicadores[def_indicadores['Indicador']==ind_selected]['NOME LONGO'].values[0]
    descr_ind = def_indicadores[def_indicadores['Indicador']==ind_selected]['DEFINIÇÃO'].values[0]
    
       
    ind01 = f'<p style="font-family:Courier; color:Black; font-size: 16px;"><b>{ind_selected}:</b>{nome_ind}</p>'
    st.markdown(ind01, unsafe_allow_html=True)
    ind02 = f'<p style="font-family:Courier; color:Black; font-size: 16px;"><b>Descrição: </b>{descr_ind}</p>'
    st.markdown(ind02, unsafe_allow_html=True)
    
    # Plot Dispersão (scatter)
    # ---------------------------------------
    fig = px.scatter(ies_ind_mun,
                 x=ind_selected, 
                 y='Total_IES', 
                 log_x = False, 
                 color='NOME_REGIAO', 
                 color_discrete_sequence=px.colors.qualitative.Set2,
                 hover_name='NOME_MUNICIPIO',
                 width=900, height=600)
    fig.update_traces(marker=dict(size = 12,line = dict(width = 2)),selector=dict(mode = 'markers'))
    fig.update_layout(plot_bgcolor='#dbe0f0')
    fig.update_layout(yaxis=dict(title='Total IES', titlefont_size=18, tickfont_size=16),
                              xaxis=dict(titlefont_size=18, tickfont_size=14),  
                              legend=dict(x=0.1,y=-0.5, font = dict(size = 16)))
    fig.update_layout(hoverlabel=dict(bgcolor="white", 
                                      font_size=16,
                                      font_family="Rockwell"))
    st.plotly_chart(fig, use_container_width=False)
    plt.close()
    st.markdown("---")
    
    # Dataframe indicadores
    # ---------------------------------------
    # exibe o dataframe dos indicadores
    titulo_02 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Descrição dos Indicadores Sociais</b></p>'
    st.markdown(titulo_02, unsafe_allow_html=True)
    st.write("Os dados dos indicadores sociais por município estão disponíveis na plataforma Atlas do Desenvolvimento Humano no Brasil (http://www.atlasbrasil.org.br/acervo/atlas). São mais de 200 indicadores que contemplam diversos temas: economia, censo demográfico, educação, etc.")
    st.write("Como exemplos podem ser citados: IDHM, Esperança de vida ao nascer, Renda per capita, População por faixa etária, População urbana, Taxa de analfabetismo por faixa etária (11 a 14 anos, 15 a 17 anos, etc.), Percentual da população com ou sem atraso idade-série em diversas modalidades de ensino;  Percentual da população de certas faixas etárias frequentando ou não determinada modalidade de ensino; Percentual de crianças que não frequenta a escola, por faixa etária; entre muitos outros.")
    st.write("Para acessar a descrição completa de um indicador, basta selecionar a respectiva coluna com um duplo clique.")
    
    # gb = GridOptionsBuilder.from_dataframe(def_indicadores)
    # gb.configure_pagination(enabled=True, paginationPageSize=10) #paginationPageSize nao funciona
    # #paginationAutoPageSize=True    
    # gb.configure_column(field='Indicador', width=100)
    # gb.configure_column(field='NOME LONGO', width=200, wrapText=True)
    # gb.configure_column(field='DEFINIÇÃO', width=700, wrapText = True)
    # gb.configure_column('Indicador', cellStyle={'color': 'blue'})
    # #gb.configure_side_bar() #Add a sidebar
    # # gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    # gridOptions = gb.build()
    
    # AgGrid(def_indicadores,  
           # gridOptions=gridOptions,
           # fit_columns_on_grid_load=True)
           # # data_return_mode='AS_INPUT'
           # # update_mode='MODEL_CHANGED'
           # #enable_enterprise_modules=True
           # #height=1000 # se colocar nao funciona paginacao
           # # reload_data=True)
           
    # #AgGrid(def_indicadores)
    st.dataframe(def_indicadores, hide_index=True, use_container_width=True, height=2000)
    #st.table(def_indicadores)
    #st.markdown(def_indicadores.to_html(escape=False), unsafe_allow_html=True)
    st.markdown("---")

# -----------------------------------------------------------------------------------
# Tab 08
# Correlação
# -----------------------------------------------------------------------------------    
def corr_spearman(df, lista_col, col_top, k):
    k = k+1 # número de variáveis
    corrmat = abs(df[lista_col].corr(method='spearman')) # correlação de spearman
    cols = corrmat.nlargest(k, col_top).index # o k-ésimo maior valor
    cm = np.corrcoef(df[cols].values.T) # calcula a correlação
    
    sns.set(font_scale=0.4)
    f, ax = plt.subplots(figsize=(8, 5))
    
    mask = np.zeros_like(cm) 
    mask[np.triu_indices_from(mask)] = True 
    sns.set_style("white")
    hm = sns.heatmap(cm, cbar=True, 
                     annot=True, 
                     square=True, 
                     fmt='.2f',
                     annot_kws={'size': 5}, 
                     yticklabels=cols.values, 
                     xticklabels=cols.values, 
                     mask = mask)
    return f, cm, cols, corrmat
    
with t_corr:
    titulo_01 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Correlação da Quantidade de IES com Indicadores Sociais</b></p>'
    st.markdown(titulo_01, unsafe_allow_html=True)
    
    st.write("Um coeficiente de correlação mede o grau pelo qual duas variáveis quantitativas estão associadas ou relacionadas entre si. Embora a correlação não implique em causalidade, pode ser interessante quantificar a relação entre as variáveis através de inúmeras medidas, como o coeficiente de Pearson ou o coeficiente de Spearman. Optou-se pelo uso do coeficiente de Pearson, no qual quanto mais próximo do valor -1 ou 1, maior a correlação. O sinal positivo indica uma correlação direta; o sinal negativo, inversa. Valores próximos de zero indicam uma correlação fraca ou desprezível.")     
    
    st.write("Nota-se que a variável 'Quantidade de IES' em cada município apresenta correlação alta com variáveis que contabilizam quantidades populacionais em diferentes contextos e faixas etárias.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        label01 = '<p style="font-family:Courier; color:#992600; font-size: 16px;"><b>Selecione a quantidade de variáveis:</b></p>'
        st.markdown(label01, unsafe_allow_html=True) 
    with col2:
        k_selected = st.selectbox(label="Selecione a quantidade de variáveis", options=[5,10,15,20], label_visibility="collapsed", index=2)
    with col3:    
        st.subheader(':dart:')
    
    
    lista_ind = list(ies_ind_mun.columns[17:249]) + ['Total_IES'] 
    k = k_selected # the k largest correlations
    col_top = 'Total_IES'
    f, cm, cols, corrmat = corr_spearman(ies_ind_mun, lista_ind, col_top, k)
    
    st.pyplot(f, use_container_width=False)
    plt.close()
    
    st.markdown("---")
    df_ind_corr = def_indicadores[def_indicadores['Indicador'].isin(cols)][['Indicador','NOME LONGO']]
    st.dataframe(df_ind_corr, hide_index=True, use_container_width=True, height=800)
    
# -----------------------------------------------------------------------------------
# Tab 09
# Regressão
# -----------------------------------------------------------------------------------  

# definição de funções
def plot_real_predicted_values(regressor, x_test, y_test, x_pred, y_pred):
    fig = plt.figure(figsize=(4.5,2))
    l = plt.plot(y_pred, y_test, 'bo', label='Dados Reais') 
    plt.setp(l, markersize=5)        
    plt.setp(l, markerfacecolor='C6') 
    xl = np.arange(min(y_test), 1.2*max(y_test),(max(y_test)-min(y_test))/10)
    yl = xl
    plt.plot(xl, yl, 'b--', label='Dados preditos')
    plt.title("Real vs Predito (" + regressor + ")", fontsize=10)
    plt.ylabel("Valores Reais", fontsize=9)
    plt.xlabel("Valores Preditos", fontsize=9)
    plt.legend(loc='best')
    return fig
    
def linear_regression(df, x_data, y_label, p_test, random_state):
    st.markdown('<p style="font-family:Courier; color:Black; font-size: 16px;"><b>Criação e Execução do Modelo de Regressão Linear</b></p>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Courier; color:Red; font-size: 14px; padding:0px; margin:0px;"><b>Estimando a variavel: Total de IES</b>', unsafe_allow_html=True)
    
    # Selecionar variáveis preditoras e a target
    # -------------------------------------------------------
    df_pred = x_data
    df_y = df.loc[:,y_label]
    x = df_pred.to_numpy(); y = df_y.to_numpy().reshape(-1, 1)
    
    # Normalização dos dados
    # -------------------------------------------------------
    scaler_Rbt = RobustScaler().fit(x)
    scaler_Rbt_y = RobustScaler().fit(y)
    x_norm = scaler_Rbt.transform(x)
    y_norm = scaler_Rbt_y.transform(y)
    
    # Separar dados de treino e testes
    # -------------------------------------------------------
    x_train, x_test, y_train, y_test = train_test_split(x_norm, 
                                                        y_norm, 
                                                        test_size = p_test, 
                                                        random_state = random_state)
    # Resumo dos dados 
    # -------------------------------------------------------
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px; padding:0px; margin:0px;">Total de registros (observações):  {x.shape[0]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px; padding:0px; margin:0px;">Total de variaveis preditoras (atributos):  {x.shape[1]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px; padding:0px; margin:0px;">Lista das variaveis preditoras:  {list(x_data.columns)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px; padding:0px; margin:0px;">Percentual utilizado para gerar base de teste:  {p_test}</p>', unsafe_allow_html=True)    
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px; ">Número aleatório para gerar bases de treino e testes:  {str(random_state)}</p>', unsafe_allow_html=True)    
            
    # Criar modelo de regressão linear 
    # -------------------------------------------------------------
    lr = LinearRegression()     
    lr.fit(x_train, y_train)    
    
    # Executa Cross Validation para sets de dados de treino
    # -------------------------------------------------------------
    CV_r2 = []
    CV_r2.append(cross_val_score(estimator = lr, X = x_train, y = y_train, cv = 10, scoring='r2'))
    mediaCV = np.round(CV_r2[0].mean(),5)
    
    # Calcula metricas de treino
    # -------------------------------------------------------------
    y_pred = lr.predict(x_train)
    R2_train = np.round(r2_score(y_train, y_pred)*100,2)
    RMSE_train = np.round(np.sqrt(mean_squared_error(y_train, y_pred)),2)

    # Calcula metricas de testes
    # -------------------------------------------------------------
    y_pred = lr.predict(x_test) 
    R2_test = np.round(r2_score(y_test, y_pred)*100,2)
    RMSE_test = np.round(np.sqrt(mean_squared_error(y_test, y_pred)),2)
    
    # Exibir as métricas 
    # -------------------------------------------------------------   
    st.markdown('<p style="font-family:Courier; color:Red; font-size: 14px; padding:0px; margin:0px;"><b>Exibindo os resultados do modelo: </b></p>', unsafe_allow_html=True)    
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px; padding:0px; margin:0px;">- CV: {str(mediaCV)}</p>', unsafe_allow_html=True)    
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px; padding:0px; margin:0px;">- R2_score (train): {R2_train}%</p>', unsafe_allow_html=True)        
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px; padding:0px; margin:0px;">- R2_score (test): {R2_test}%</p>', unsafe_allow_html=True)           
    st.markdown(f'<p style="font-family:Courier; color:Black; font-size: 14px;">- RMSE (test): {RMSE_test}</p>', unsafe_allow_html=True)               
    
    # Gera plots
    # -------------------------------------------------------------    
    st.markdown('<p style="font-family:Courier; color:Red; font-size: 14px; padding:0px; margin:0px;"><b>Exibindo gráficos de valores preditos e reais:</b></p>', unsafe_allow_html=True)  
    fig = plot_real_predicted_values("linear regression", x_test, y_test, x_test, y_pred)    
    return fig 
    

with t_regr:    
    titulo_01 = '<p style="font-family:Courier; color:Blue; font-size: 20px;"><b>Regressão Linear: estimar a quantidade de IES em um município a partir de algumas variáveis</b></p>'
    st.markdown(titulo_01, unsafe_allow_html=True)
    
    st.write("A utilização de algoritmos supervisionados de Machine Learning - como a Regressão Linear e suas extensões (Lasso e Ridge), Árvores de Decisão e Máquina de Vetores de Suporte proporcionam a geração de modelos preditivos.") 
    
    st.write("Neste caso, selecione algumas variáveis (até quinze variáveis previamente selecionadas conforme relevante grau de correlação), o percentual de registros de municípios para compor a base de teste e um número aleatório (utilizado para a divisão dos dados em treino e testes) - e veja a acurácia do modelo de Regressão Linear Múltipla em prever a quantidade de IES nos municípios.")  
    
     # variaveis pre selecionadas que fornecem um bom CV (random=42, perc=0.30)   
    best_features = ['HOMEM40A44','MULH20A24','MULH25A29','MULH30A34','MULH35A39','MULH40A44','MULHERTOT',
    'PEA','PEA18M','PESO15','PESO18','PESO25','Pop_urbana','PIA','PIA18M']
    
    # lista de variaveis
    var = list(df_ind_corr['Indicador'].values)
    
    
    label01 = '<p style="font-family:Courier; color:#992600; font-size: 16px;"><b>Selecione as variáveis preditoras: </b></p>'
    st.markdown(label01, unsafe_allow_html=True) 
    options = st.multiselect(label='Selecione as variáveis de interesse:',options=best_features, label_visibility="collapsed",placeholder='Selecionar variáveis', default=best_features)
        
    # informar percentual para base de testes    
    col3, col4 = st.columns(2)
    with col3:
        label02 = '<p style="font-family:Courier; color:#992600; font-size: 16px;"><b>Selecione o percentual de registros para teste: </b></p>'
        st.markdown(label02, unsafe_allow_html=True) 
    with col4:
        perc_selected = st.selectbox(label='Selecione o percentual para testes:',options=[5,10,15,20,25,30], index=5,label_visibility="collapsed")        
        
    # informar randomm number  
    col5, col6 = st.columns(2)
    with col5:
        label03 = '<p style="font-family:Courier; color:#992600; font-size: 16px;"><b>Selecione um número aleatório para gerar a base de testes: </b></p>'
        st.markdown(label03, unsafe_allow_html=True) 
    with col6:
        random_selected = st.number_input(label = 'Selecione um número aleatório:', min_value=1, max_value=99, value=42, step=1, label_visibility="collapsed")
        
    st.markdown("---")

    # prepara dados
    #ies_ind_mun

    best_features = options
    x_data = ies_ind_mun.loc[:,best_features]
        
    
    # executa Regressao
    fig = linear_regression(ies_ind_mun, x_data, 'Total_IES', perc_selected, random_selected)
    
    st.pyplot(fig, use_container_width=False)
    plt.close()
    
