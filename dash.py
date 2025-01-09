import pandas as pd
import streamlit as st
import time

import psycopg2
#import pandas as pd
#import matplotlib as plb

#@st.experimental_singleton
def init_connection():
    return psycopg2.connect(**st.secrets["postgresql"])
conn = init_connection()

#@st.experimental_memo(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

rows = run_query("SELECT * FROM cadastro-pn limit 10")

data = pd.DataFrame(rows)
data.columns=['PkcodigoPn','nome', 'estado', 'cidade',]
st.table(data)



st.title("Análise RPA")

st.set_page_config(page_title="Dashboard", page_icon="🌍", layout="wide")
st.subheader("🔔 Análise Descritiva com Python e Streamlit")
st.markdown("##")

theme_plotly = None




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


