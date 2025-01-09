from operator import index

import pandas as pd
import streamlit as st
import time
import psycopg2
#import matplotlib as plb


#ConeXão com o POSTGRE
connection = psycopg2.connect(host='192.168.0.250',
                                  database='DB-CONTAS A RECEBER',
                                  user='postgres',
                                  password='postgres')
cursor = connection.cursor()

exibir_Filiais = cursor.execute("""
   SELECT "Id", "Nome", "FkUnidadeDeNegocio"
   FROM public.filial;
 """)
exibeFilial = cursor.fetchall()
exibir_Parceiro = cursor.execute("""
    SELECT "Nome", "NomeFantasia", "Estado", "Cidade", "Bairro", "Cep"
    	FROM public."cadastro-pn";
""")

exibeParceiro = cursor.fetchall()

dadosFilial = pd.DataFrame(exibeFilial)
dadosFilial.columns=['id', 'Nome', 'FkUnidadeDeNegocio']

dadosParceiro = pd.DataFrame(exibeParceiro)
dadosParceiro.columns=['Nome', 'NomeFantasia', 'Estado', 'Cidade', 'Bairro', 'Cep' ]

#Funciona como um container para o menu lateral



with st.sidebar:

    st.header("Menu de análises 🔍")

    escolherVisualizacao = st.multiselect(
        "Monte sua consulta",
        ("Hora", "Dia", "Robô", "a", "b", "c", "d"),
        placeholder="Por..."
    )

    #Menu dropdown para escolher análise
    escolherAnalise = st.select_slider(
        "Período desejado",

        options = [
            "Anual",
            "Semestral",
            "Trimestral",
            "Bimestral",
            "Mensal",
            "Semanal",
        ],
    )

if escolherAnalise == "Anual":

    with st.spinner("carregando..."):
        time.sleep(3)

        if st.success:
            st.write("Gráfico anual")
            st.table(dadosFilial) #Exibe a Tabela apos 3 segundos de carregamento
        else:
            st.write("Falha ao carregar gráfico")

elif escolherAnalise == "Semestral":
    with st.spinner("carregando..."):
        time.sleep(3)
        st.success("pronto!")

        if st.success:
           st.write("Gráfico dos últimos 6 meses")
           st.table(dadosParceiro)
            #Aqui Vou colocar o gráfico
        else:
            st.write("Falha ao carregar gráfico")
elif escolherAnalise == None:
    st.subheader("Olá! ☺️ aqui você verá sua análise. Acesse o menu lateral e escolha seus parâmetros")
else:
    st.write('Erro')


