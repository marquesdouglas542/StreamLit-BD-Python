import streamlit as st
import time
import psycopg2
#import pandas as pd
#import matplotlib as plb

st.title("Análise RPA")

escolherAnalise = st.selectbox(
    "Monte sua análise",
    ("Anual", "Semestral", "Trimestral", "Semanal"),
    index = None,
    placeholder = "Selecione um período"
)
if escolherAnalise == "Anual":
    st.write("Gráfico anual")
    with st.spinner("carregando..."):
        time.sleep(5)

        if st.success:
            st.write("Gráfico do Ano")
            # Aqui Vou colocar o gráfico

        else:
            st.write("Falha ao carregar gráfico")

elif escolherAnalise == "Semestral":

    with st.spinner("carregando..."):
        time.sleep(5)
        st.success("pronto!")

        if st.success:
            st.write("Gráfico dos últimos 6 meses")
            #Aqui Vou colocar o gráfico
        else:
            st.write("Falha ao carregar gráfico")

elif escolherAnalise == "Trimestral":
    st.write("Gráfico do Trimestre")

    if st.success:
            st.write("Gráfico Trimestral")
        # Aqui Vou colocar o gráfico
    else:
        st.write("Falha ao carregar gráfico")

elif escolherAnalise == "Semanal":
    st.write("Gráfico da Semana")

    if st.success:
        st.write("Gráfico Semanal")
        # Aqui Vou colocar o gráfico
    else:
        st.write("Falha ao carregar gráfico")

else:
    st.write("Não encontrado")


