import pandas as pd
import streamlit as st
import psycopg2
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image
import locale
import time

# Definir o locale para português (Brasil) para que os nomes dos meses apareçam em português
locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')


def main():
    st.set_page_config(
        page_title="Análise - Pedido de compras",
        page_icon="📊",
        layout="wide"
    )

    # Definir as cores para os anos
    color_map = {
        2023: '#0a450a',
        2024: '#14cc14',
        2025: '#ad051c'
    }

    # Função para conectar ao banco de dados
    def conectar_banco():
        return psycopg2.connect(
            host='192.168.0.250',
            database='DB-ACOMPANHAMENTOS-RPA',
            user='postgres',
            password='postgres'
        )

    # Função para carregar pedidos de compra
    def carregar_dados_2023(cursor):
        cursor.execute(""" 
            SELECT data_lancamento, nome_filial, codigo_filial, nome_usuario, numero_documento, 
            nome_cliente_fornecedor, codigo_parceiro, total_documento, hora_geracao
            FROM public.pedidos_compras WHERE data_lancamento BETWEEN '2023-08-09' and CURRENT_DATE;
        """)
        return pd.DataFrame(cursor.fetchall(), columns=[
            'data_lancamento', 'nome_filial', 'codigo_filial', 'nome_usuario', 'numero_documento',
            'nome_cliente_fornecedor', 'codigo_parceiro', 'total_documento', 'hora_geracao'
        ])

    # Conexão e consulta ao banco
    connection = conectar_banco()
    cursor = connection.cursor()

    df_pedidos2023 = carregar_dados_2023(cursor)

    # Garantir que a coluna 'data_lancamento' está no formato datetime e tratar erros de conversão
    df_pedidos2023['data_lancamento'] = pd.to_datetime(df_pedidos2023['data_lancamento'], errors='coerce')

    # Função para exibir gráficos ou tabelas com base na análise selecionada
    def exibir_analise():
        # Menu lateral de seleção de visualização
        visualizacao = st.sidebar.selectbox(
            "Selecione a visualização",
            ("Pedidos por Hora", "Pedidos por Mês", "Comparação Anual", "Relatório Cruzado")
        )

        # Visualização "Relatório Cruzado"
        if visualizacao == "Relatório Cruzado":
            st.write("Relatório Cruzado - Pedidos Totais por Ano")

            with st.spinner("Carregando..."):
                time.sleep(2)

            # Agrupar os dados por ano e mês
            df_pedidos2023['ano'] = df_pedidos2023['data_lancamento'].dt.year
            df_pedidos2023['mes'] = df_pedidos2023['data_lancamento'].dt.month
            df_pedidos2023['semana'] = df_pedidos2023['data_lancamento'].dt.isocalendar().week

            # Total de lançamentos por mês e semana
            df_total_mes = df_pedidos2023.groupby(['ano', 'mes']).size().reset_index(name='total_mes')
            df_total_semana = df_pedidos2023.groupby(['ano', 'semana']).size().reset_index(name='total_semana')

            # Fornecedor com mais pedidos
            fornecedor_top = df_pedidos2023.groupby('nome_cliente_fornecedor').size().reset_index(
                name='total_fornecedor')
            fornecedor_top = fornecedor_top.sort_values(by='total_fornecedor', ascending=False).head(1)

            # Filial com maior valor movimentado
            filial_top = df_pedidos2023.groupby('nome_filial')['total_documento'].sum().reset_index(name='valor_filial')
            filial_top = filial_top.sort_values(by='valor_filial', ascending=False).head(1)

            # Inicializar página
            if 'pagina_mes' not in st.session_state:
                st.session_state.pagina_mes = 1
            if 'pagina_semana' not in st.session_state:
                st.session_state.pagina_semana = 1

            # Exibindo dados agregados com estilização
            st.write("Total de Lançamentos por Mês")
            start_idx = (st.session_state.pagina_mes - 1) * 10
            end_idx = st.session_state.pagina_mes * 10

            # Converter a coluna 'total_mes' para numérico e formatar corretamente
            df_total_mes['total_mes'] = pd.to_numeric(df_total_mes['total_mes'], errors='coerce')

            st.dataframe(df_total_mes[start_idx:end_idx].style.format({"total_mes": "{:,.0f}"}), use_container_width=True)

            st.write("Total de Lançamentos por Semana")
            start_idx_semana = (st.session_state.pagina_semana - 1) * 10
            end_idx_semana = st.session_state.pagina_semana * 10

            # Converter a coluna 'total_semana' para numérico e formatar corretamente
            df_total_semana['total_semana'] = pd.to_numeric(df_total_semana['total_semana'], errors='coerce')

            st.dataframe(df_total_semana[start_idx_semana:end_idx_semana].style.format({"total_semana": "{:,.0f}"}), use_container_width=True)

            st.write(
                f"Fornecedor com mais pedidos: {fornecedor_top['nome_cliente_fornecedor'].values[0]} com {fornecedor_top['total_fornecedor'].values[0]} pedidos")
            st.write(
                f"Filial com maior valor movimentado: {filial_top['nome_filial'].values[0]} com R${filial_top['valor_filial'].values[0]:,.2f}")

            # Criando um gráfico comparativo para as análises
            fig_comparativo = go.Figure()

            # Adicionando gráfico de barras para lançamentos por mês
            fig_comparativo.add_trace(go.Bar(
                x=df_total_mes['ano'].astype(str) + '-' + df_total_mes['mes'].astype(str),
                y=df_total_mes['total_mes'],
                name='Lançamentos por Mês',
                marker=dict(color='rgba(0, 123, 255, 0.6)')
            ))

            # Adicionando gráfico de barras para lançamentos por semana
            fig_comparativo.add_trace(go.Bar(
                x=df_total_semana['ano'].astype(str) + '-W' + df_total_semana['semana'].astype(str),
                y=df_total_semana['total_semana'],
                name='Lançamentos por Semana',
                marker=dict(color='rgba(255, 159, 64, 0.6)')
            ))

            # Exibindo gráfico comparativo
            fig_comparativo.update_layout(
                title="Comparação de Lançamentos: Mês vs Semana",
                xaxis_title="Ano e Mês / Semana",
                yaxis_title="Quantidade de Lançamentos",
                plot_bgcolor='rgb(17,17,17)',  # Cor de fundo
                paper_bgcolor='rgb(17,17,17)',  # Cor do papel
                font=dict(color="white"),  # Cor da fonte
                barmode='group',  # Barras agrupadas
                hovermode='closest'
            )

            st.plotly_chart(fig_comparativo)

            # Botões de navegação para a tabela de meses
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Página Anterior (Meses)", key="anterior_mes") and st.session_state.pagina_mes > 1:
                    st.session_state.pagina_mes -= 1
            with col2:
                if st.button("Próxima Página (Meses)", key="proxima_mes") and st.session_state.pagina_mes * 10 < len(df_total_mes):
                    st.session_state.pagina_mes += 1

            # Botões de navegação para a tabela de semanas
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Página Anterior (Semanas)", key="anterior_semana") and st.session_state.pagina_semana > 1:
                    st.session_state.pagina_semana -= 1
            with col2:
                if st.button("Próxima Página (Semanas)", key="proxima_semana") and st.session_state.pagina_semana * 10 < len(df_total_semana):
                    st.session_state.pagina_semana += 1

        # Visualização "Hora"
        if visualizacao == "Pedidos por Hora":
            st.write(f"Analisando pedidos por hora")

            # Garantir que 'hora_geracao' não contenha valores vazios
            df_pedidos2023['hora_geracao'] = df_pedidos2023['hora_geracao'].fillna('00:00')

            # Extrair hora corretamente
            df_pedidos2023['hora'] = df_pedidos2023['hora_geracao'].apply(lambda x: str(x).split(':')[0] if x else '0')
            df_pedidos2023['hora'] = pd.to_numeric(df_pedidos2023['hora'], errors='coerce')

            # Tratar qualquer valor de hora inválido ou NaN
            df_pedidos2023['hora'] = df_pedidos2023['hora'].fillna(0).astype(int)

            # Agrupar os dados por hora
            df_agrupado_hora = df_pedidos2023.groupby(['data_lancamento', 'hora']).size().reset_index(
                name='quantidade_lancamentos')

            # Adicionar a coluna formatada de hora
            df_agrupado_hora['hora_formatada'] = df_agrupado_hora['hora'].apply(lambda x: f"{x:02}:00h")

            fig = go.Figure()

            # Adicionar uma linha para cada ano
            anos = df_pedidos2023['data_lancamento'].dt.year.unique()

            for ano in anos:
                df_ano = df_agrupado_hora[df_agrupado_hora['data_lancamento'].dt.year == ano]

                # Garantir que todas as horas (0 a 23) estejam representadas no gráfico
                df_ano_completo = pd.DataFrame({
                    'hora': range(24),
                    'quantidade_lancamentos': [df_ano[df_ano['hora'] == h]['quantidade_lancamentos'].sum() if len(
                        df_ano[df_ano['hora'] == h]) > 0 else 0 for h in range(24)]
                })

                # Adicionando linha para cada ano
                fig.add_trace(go.Scatter(
                    x=df_ano_completo['hora'],
                    y=df_ano_completo['quantidade_lancamentos'],
                    mode='lines+markers',
                    name=f"Pedidos de {ano}",
                    line=dict(color=color_map[ano], width=2),
                    marker=dict(size=6)
                ))

            # Personalizando o layout do gráfico
            fig.update_layout(
                title="Pedidos de Compras por Hora",
                xaxis_title="Hora",
                yaxis_title="Quantidade de Pedidos",
                plot_bgcolor='rgb(17,17,17)',  # Cor de fundo
                paper_bgcolor='rgb(17,17,17)',  # Cor do papel
                font=dict(color="white"),  # Cor da fonte
                hovermode="closest",
                showlegend=True
            )

            st.plotly_chart(fig)

    # Chama a função de exibição
    exibir_analise()

    connection.close()


if __name__ == "__main__":
    main()
