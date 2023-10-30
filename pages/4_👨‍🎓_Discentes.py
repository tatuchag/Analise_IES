import os
import pandas as pd 
import numpy as np 
import matplotlib
import matplotlib.pyplot as plt 
import seaborn as sns 
import plotly
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------------------
# PARTE 01 - Evolução das Matriculas - Brasil
# ------------------------------------------------------------------------

st.set_page_config(page_title='Analise Discentes', 
                    page_icon=':student:', 
				    layout='wide', 
                    initial_sidebar_state='expanded')
                    
                    
st.title(':chart_with_upwards_trend: :student: Evolução das Matrículas :flag-br:')
st.subheader('Escopo: Cursos Presenciais de Federais Públicas e Privadas')
st.subheader("Dados de 2012-2022")
st.markdown("---")         

# ------------------------------------------------------------------------
# Parametros plots seaborn
# ------------------------------------------------------------------------
sns.set(style="darkgrid")

# ------------------------------------------------------------------------
# Carrega dados Cursos
# ------------------------------------------------------------------------
@st.cache_data
# carregar algumas colunas pois a carga do df é demorado
# dados_cursos_2012_2022.csv alterado para dados_cursos_2012_2022_reduzida01.csv

def carrega_df():
	df_all = pd.read_csv('./arquivos/dados_cursos_2012_2022_reduzida01.csv', sep='|', 
						low_memory=False, 
						usecols=['NU_ANO_CENSO','SG_UF','CO_IES',
                        'Tipo_Cat_Admn','Tipo_Org_Acad','Tipo_Org_Principal', 'Tipo_Grau_Acad','Tipo_Rede',
						'NO_CINE_AREA_GERAL', 'NO_CURSO','QT_CURSO','QT_MAT','QT_ING','QT_CONC','TIPO_INST',
                        'QT_MAT_0_17', 'QT_MAT_18_24', 'QT_MAT_25_29', 'QT_MAT_30_34',
                        'QT_MAT_35_39', 'QT_MAT_40_49', 'QT_MAT_50_59', 'QT_MAT_60_MAIS'
                        ])
	return df_all
df_all = carrega_df()	

# ------------------------------------------------------------------------				  
# Funcoes
# ------------------------------------------------------------------------
def gerar_plot_evol_ano(df, col_ano, col_grupo, col_soma, legenda_outside):

    # exibe primeiros registros do df
    print('Exibindo alguns registros do df consolidado...\n')
    df_plot = df.groupby([col_ano, col_grupo])[col_soma].sum().reset_index().rename(columns={col_soma:'Total'})
    #display(df_plot.head(5))
    
    ano_min = df_plot[col_ano].min()
    ano_max = df_plot[col_ano].max()
    
    print(f'Soma da coluna {col_soma} nos anos de {ano_min} a {ano_max}: {df[col_soma].sum()}')

    f, axes = plt.subplots(1, 1,  figsize=(20,8))

    # controle dos valores do eixo Y 
    data = df_plot.copy()
    y_max = df_plot['Total'].max()
    if y_max >= 10000: 
        data['Total'] = data['Total']/1000
        limite_sup = y_max/1000 * 1.10
        intervalo = round((limite_sup/10)/100)*100
        if intervalo==0: intervalo = limite_sup/10
        text_y_axis = 'Total (x 1000)'
        
    else:  
        limite_sup = y_max * 1.10
        intervalo = limite_sup / 10
        text_y_axis = 'Total'
        
    sns.pointplot(x=col_ano, y='Total', hue=col_grupo, 
                data=data.sort_values(by=([col_ano,'Total']), ascending=[False,False]), ax=axes,
                 markers='o')
    
    #axes.set_title(f'Evolução {col_soma} - PRESENCIAL por Ano', fontsize=20)
    axes.set_xticklabels(axes.get_xticklabels(), rotation=0, ha="right", fontsize=16)
    axes.set(xlabel=''); axes.set_ylabel(text_y_axis, fontsize=18)
    
    major_yticks = np.arange(0, limite_sup, intervalo); 
    axes.set_yticks(major_yticks)
    axes.tick_params(axis='y', labelsize=14)
    axes.grid(color='gray', linestyle='--', linewidth=1.2, axis='both', alpha=.2)

    axes.legend(loc='best', fontsize=18)
    if legenda_outside == 'S':
        axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, 
                    ncol=2, fontsize='large')
    
    return f
    #plt.show()


# ------------------------------------------------------------------------				  
# Prepara dataframes
# ------------------------------------------------------------------------
#plot01
serie_matr = df_all.groupby(['NU_ANO_CENSO', 'TIPO_INST'])['QT_MAT'].sum().reset_index().rename(columns={'QT_MAT':'Total_matriculas'})


# ------------------------------------------------------------------------				  
# Plot01:  Evolução da Qtd Matriculas Presenciais por Ano/ Tipo Rede (linha)
# ------------------------------------------------------------------------
titulo_plot01 =  '<p style="font-family:Courier; color:Black; font-size: 23px;"><b>Visualização da Evolução da Qtd de Matrículas PRESENCIAIS por Rede de Ensino</b></p>'
st.markdown(titulo_plot01, unsafe_allow_html=True)

ano_min = serie_matr['NU_ANO_CENSO'].min()
ano_max = serie_matr['NU_ANO_CENSO'].max()

f, axes = plt.subplots(1, 1,  figsize=(20,8))

data = serie_matr.copy()
data['Total_matriculas'] = data['Total_matriculas']/1000

axes = sns.pointplot(x='NU_ANO_CENSO', y='Total_matriculas', hue='TIPO_INST', 
            data=data.sort_values(by=(['NU_ANO_CENSO','Total_matriculas']), ascending=[False,False]), 
             markers='o')

axes.set_xticklabels(axes.get_xticklabels(), rotation=0, ha="right", fontsize=16)
axes.set(xlabel=''); axes.set_ylabel('Total Matriculas (x 1000)', fontsize=18)

limite_sup = serie_matr['Total_matriculas'].max()/1000 * 1.10
intervalo = round((limite_sup/10)/100)*100
major_yticks = np.arange(0, limite_sup, intervalo); 
axes.set_yticks(major_yticks)
axes.tick_params(axis='y', labelsize=14)

axes.grid(color='gray', linestyle='--', linewidth=1.2, axis='both', alpha=.2)

#axes.legend(loc='best', fontsize=18)
axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=3,
           fontsize='x-large')

st.pyplot(f)
st.markdown("---")



# ------------------------------------------------------------------------				  
# Plot02:  Evolução da Qtd Matriculas Presenciais por Ano/ Grau Academico (linha)
# ------------------------------------------------------------------------
titulo_plot02 =  '<p style="font-family:Courier; color:Black; font-size: 23px;"><b>Visualização da Evolução da Qtd de Matrículas PRESENCIAIS por Grau Academico</b></p>'
st.markdown(titulo_plot02, unsafe_allow_html=True)

col_ano = 'NU_ANO_CENSO'
col_grupo = 'Tipo_Grau_Acad'
col_soma = 'QT_MAT'
legenda_outside = 'N'

f = gerar_plot_evol_ano(df_all, col_ano, col_grupo, col_soma, legenda_outside)                                            
st.pyplot(f)
st.markdown("---")


# ------------------------------------------------------------------------				  
# Plot03:  Evolução da Qtd Matriculas Presenciais por Ano/ Area Curso (linha)
# ------------------------------------------------------------------------
titulo_plot03 =  '<p style="font-family:Courier; color:Black; font-size: 23px;"><b>Visualização da Evolução da Qtd de Matrículas PRESENCIAIS por Area Geral do Curso</b></p>'
st.markdown(titulo_plot03, unsafe_allow_html=True)

col_ano = 'NU_ANO_CENSO'
col_grupo = 'NO_CINE_AREA_GERAL'
col_soma = 'QT_MAT'
legenda_outside = 'S'

df_areas = df_all[~df_all['NO_CINE_AREA_GERAL'].isin(['Programas básicos'])]
f = gerar_plot_evol_ano(df_areas, col_ano, col_grupo, col_soma, legenda_outside)                                            
st.pyplot(f)
st.markdown("---")

# ------------------------------------------------------------------------				  
# Plot04:  Evolução da Qtd Matriculas Presenciais por Ano/ Faixa Idade (linha)
# ------------------------------------------------------------------------
# Preparar dados
serie_matr_faixas_t1 = df_all.melt(id_vars=['NU_ANO_CENSO','CO_IES','NO_CURSO','QT_MAT'], var_name='Faixa_etaria', 
                                   value_name = 'Total_MAT',
                                   value_vars=['QT_MAT_0_17', 'QT_MAT_18_24', 'QT_MAT_25_29', 'QT_MAT_30_34',
                                               'QT_MAT_35_39', 'QT_MAT_40_49', 'QT_MAT_50_59', 'QT_MAT_60_MAIS'])
serie_matr_faixas_t2 = serie_matr_faixas_t1.groupby(['NU_ANO_CENSO', 'CO_IES','NO_CURSO','QT_MAT','Faixa_etaria'])['Total_MAT']\
                                            .sum().reset_index()
                                            
serie_matr_faixas = serie_matr_faixas_t2.groupby(['NU_ANO_CENSO','Faixa_etaria'])['Total_MAT'].sum().reset_index()

# Exibir plot
titulo_plot04 =  '<p style="font-family:Courier; color:Black; font-size: 23px;"><b>Visualização da Evolução da Qtd de Matrículas PRESENCIAIS por Faixa de Idade</b></p>'
st.markdown(titulo_plot04, unsafe_allow_html=True)
                                            
col_ano = 'NU_ANO_CENSO'
col_grupo = 'Faixa_etaria'
col_soma = 'Total_MAT'
legenda_outside = 'S'

f = gerar_plot_evol_ano(serie_matr_faixas, col_ano, col_grupo, col_soma, legenda_outside)                                            
st.pyplot(f)
st.markdown("---")
                      

# ------------------------------------------------------------------------
# PARTE 02 - Evolução das Matriculas - UFs
# ------------------------------------------------------------------------
                    
st.title(':chart_with_upwards_trend: :student: Evolução das Matrículas :classical_building:')
st.subheader('Escopo: Cursos Presenciais de Federais Públicas e Privadas')
st.subheader("Dados de 2012-2022")
st.markdown("---")       


# ------------------------------------------------------------------------				  
# Prepara dataframes
# ------------------------------------------------------------------------
# Total e Perc Matr por Ano, UF, Rede de Ensino
tot_matr_uf = df_all.groupby(['NU_ANO_CENSO', 'SG_UF'])['QT_MAT'].sum()
tot_matr_uf_re = df_all.groupby(['NU_ANO_CENSO', 'SG_UF', 'TIPO_INST'])['QT_MAT'].sum()
perc_matr_uf_re = round((tot_matr_uf_re / tot_matr_uf*100),2)

distr_matr_uf_re = pd.DataFrame({'Total_Mat'  : tot_matr_uf_re,
                                 'Total_Mat_p': perc_matr_uf_re}).reset_index()

distr_matr_uf_re['Total_Mat_mil'] = distr_matr_uf_re['Total_Mat']/1000

# Total de ingressantes por Ano e por UF
tot_ing_uf = df_all.groupby(['NU_ANO_CENSO', 'SG_UF'])['QT_ING'].sum().reset_index().rename(columns={'QT_ING':'Total_Ingr'})
tot_ing_uf['Total_Ingr_mil'] = tot_ing_uf['Total_Ingr'] / 1000


# ------------------------------------------------------------------------				  
# Plot01: Total Matriculas e Ingressantes por Rede Ensino 
# ------------------------------------------------------------------------
cores = sns.color_palette("terrain")
l_anos = range(2012,2023,1)

col1, col2, col3 = st.columns(3)
with col1:
    label01 = '<p style="font-family:Courier; color:#992600; font-size: 20px;"><b>Selecione um ano específico:</b></p>'
    st.markdown(label01, unsafe_allow_html=True) 
    
with col2:
    ano_selecionado = st.selectbox(label="Selecione um ano específico:", options=l_anos, label_visibility="collapsed")
    
with col3:    
    st.subheader(':date:')
    
    
if ano_selecionado:
    titulo_plot01 =  f'<p style="font-family:Courier; color:Black; font-size: 23px;"><b>Total de Matrículas e Ingressantes - {ano_selecionado}</b></p>'
    st.markdown(titulo_plot01, unsafe_allow_html=True)   
    data = distr_matr_uf_re[distr_matr_uf_re['NU_ANO_CENSO']==ano_selecionado].sort_values(by='SG_UF', ascending=True)    
    f, axes = plt.subplots(1, 1,  figsize=(16, 8))
    g = sns.barplot(x='SG_UF', y='Total_Mat_mil', hue='TIPO_INST', data=data, orient='v', ax=axes, palette = cores)
    #axes.set_title(titulo, fontsize=18)
    major_yticks = np.arange(0, 1600, 200)
    axes.set_yticks(major_yticks)
    axes.set(xlabel=''); axes.set(ylabel='')
    axes.legend(loc='upper center', fontsize=18).set_visible(False)
    axes.grid(visible=False)
    
    ax2 = axes.twinx()
    dados2 = tot_ing_uf[tot_ing_uf['NU_ANO_CENSO']==ano_selecionado].sort_values(by='SG_UF', ascending=True)
    ax2.plot(dados2['SG_UF'], dados2['Total_Ingr_mil'],color='#ff3333', label='Total_Ingr_mil')
    ax2.set_ylabel("Total Ingressantes")
    ax2.set_yticks(major_yticks)
    ax2.grid(visible=True, linestyle = "dashed", color='white')
    
    lines1, labels1 = axes.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper center", fontsize=18)    
    st.pyplot(f)
    
    
 

# para mostrar todos os anos
# for ano in range(2012, 2023, 1): # a = para cada ano 
    # data = distr_matr_uf_re[distr_matr_uf_re['NU_ANO_CENSO']==ano].sort_values(by='SG_UF', ascending=True)
    # f, axes = plt.subplots(1, 1,  figsize=(16, 8))
    # g = sns.barplot(x='SG_UF', y='Total_Mat_mil', hue='TIPO_INST', data=data, orient='v', ax=axes, palette = cores)
    
    # titulo = 'Total de Matrículas e Ingressantes - ' + str(ano)
    
    # axes.set_title(titulo, fontsize=18)
    # major_yticks = np.arange(0, 1600, 200)
    # axes.set_yticks(major_yticks)
    # axes.set(xlabel=''); axes.set(ylabel='')
    # axes.legend(loc='upper center', fontsize=18).set_visible(False)
    # axes.grid(visible=False)
    
    # ax2 = axes.twinx()
    # dados2 = tot_ing_uf[tot_ing_uf['NU_ANO_CENSO']==ano].sort_values(by='SG_UF', ascending=True)
    # ax2.plot(dados2['SG_UF'], dados2['Total_Ingr_mil'],color='#ff3333', label='Total_Ingr_mil')
    # ax2.set_ylabel("Total Ingressantes")
    # ax2.set_yticks(major_yticks)
    # ax2.grid(visible=True, linestyle = "dashed", color='white')
    
    # lines1, labels1 = axes.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper center", fontsize=18)    
    # st.pyplot(f)

    

                          
                                            
                                            