import pandas as pd
import streamlit as st
import time
import psycopg2
import plotly.express as px

def main():

    st.set_page_config(
        page_title="Análise - Pedido de compras ",
        page_icon="📊",
        layout="wide"
    )

    # Função para conectar ao banco de dados
    def conectar_banco():
        return psycopg2.connect(
            host='192.168.0.250',
            database='DB-ACOMPANHAMENTOS-RPA',
            user='postgres',
            password='postgres'
        )


    # Função para carregar pedidos de compra de 2023
    def carregar_dados_2023(cursor):
        cursor.execute("""
            SELECT data_lancamento, nome_filial, codigo_filial, nome_usuario, numero_documento, 
            nome_cliente_fornecedor, codigo_parceiro, total_documento, hora_geracao
            FROM public.pedidos_compras WHERE data_lancamento BETWEEN '2023-08-09' and '2023-12-31' limit 10000;
        """)
        return pd.DataFrame(cursor.fetchall(), columns=[
            'data_lancamento', 'nome_filial', 'codigo_filial', 'nome_usuario', 'numero_documento',
            'nome_cliente_fornecedor', 'codigo_parceiro', 'total_documento', 'hora_geracao'
        ])

    # Conexão e consulta ao banco
    connection = conectar_banco()
    cursor = connection.cursor()

    df_pedidos2023 = carregar_dados_2023(cursor)

    # Função para exibir o menu lateral e capturar as escolhas do usuário
    def menu_lateral():
        with st.sidebar:
            st.header("Menu de análises 🔍")

            # Multiselect para escolher visualizações
            escolherVisualizacao = st.selectbox(
                "Monte sua consulta",
                ["Hora", "Dia", "Robô"],
                index=None,
                placeholder="Escolha os parâmetros"
            )

            # Seleção do período desejado para análise
            escolherAnalise = st.select_slider(
                "Período desejado",
                options=["Anual", "Semestral", "Trimestral", "Mensal", "Semanal"],
            )
        return escolherVisualizacao, escolherAnalise

    # Chama o menu e pega a escolha do usuário
    escolherVisualizacao, escolherAnalise = menu_lateral()


    # Função para exibir gráficos ou tabelas com base na análise selecionada
    def exibir_analise(escolherAnalise):
        if escolherAnalise == "Anual":

            with st.spinner("Carregando..."):
                time.sleep(2)
                st.success("Pronto!")
                st.write("Gráfico anual")

                # Agregar dados para contar a quantidade de pedidos por filial
                df_agrupado = df_pedidos2023.groupby('nome_filial').size().reset_index(name='quantidade_lancamentos')

                # Gráfico de barra com o Plotly, agora utilizando a quantidade de lançamentos
                fig = px.bar(df_agrupado, x='nome_filial', y='quantidade_lancamentos', color='nome_filial',
                             barmode='group', title="Quantidade de Lançamentos por Filial em 2023")

                # Personalizar os rótulos dos eixos e título da legenda
                fig.update_layout(
                    xaxis_title="Filial",
                    yaxis_title="Total de lançamentos 2023",
                    coloraxis_colorbar_title="Filiais",  # Título da legenda de cores
                    xaxis={'categoryorder': 'total ascending'}  # Ordenar as filiais pela quantidade de lançamentos
                )

                st.plotly_chart(fig)

        elif escolherVisualizacao is None:
            st.subheader("Olá! ☺️ Acesse o menu lateral e escolha sua Consulta.")

        else:
            st.write("Erro: Selecione um período válido.")


    # Chama a função para exibir a análise com base na escolha do usuário
    exibir_analise(escolherAnalise)

if __name__ == "__main__":
    main()
