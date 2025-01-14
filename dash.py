import pandas as pd
import streamlit as st
import psycopg2
import plotly.graph_objects as go
from datetime import datetime, timedelta
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

    # Exibir animação de carregamento até o gráfico ser selecionado
    loading_message = st.empty()

    # Exibindo a animação (um simples texto "Carregando...")
    with loading_message:
        # Efeito de digitação com cursor piscando e centralizado
        st.markdown("""
        <style>
        .typing-container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;  /* Preenche a altura da tela */
        }

        .typing-text {
            font-size: 2.5em;
            font-family: 'Courier New', Courier, monospace;
            color: #34e340;
            white-space: nowrap;
            overflow: hidden;
            border-right: .15em solid #8c2f16;
            width: 0;
            animation: typing 3s steps(40, end) forwards, blink 0.75s step-end infinite;
        }

        /* Animação para a digitação */
        @keyframes typing {
            0% { width: 0; }
            65% { width: 50%; }
        }

        /* Animação para o cursor piscando */
        @keyframes blink {
            50% { border-color: #801e05; }
        }

        </style>
        <div class="typing-container">
            <div class="typing-text">Grupo Campanha</div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(7)

    # Remover animação assim que o gráfico for exibido
    loading_message.empty()

    # Função para exibir gráficos ou tabelas com base na análise selecionada
    def exibir_analise():
        # Visualização "Hora"
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

        fig = go.Figure()

        # Adicionar uma linha para cada ano
        anos = df_pedidos2023['data_lancamento'].dt.year.unique()

        # Definir as cores específicas para os anos
        color_map = {
            2023: '#0a450a',
            2024: '#14cc14',
            2025: '#ad051c'
        }

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
                name=f"Ano {ano}",
                line=dict(width=2, color=color_map.get(ano, '#cccccc')),  # Cor com base no mapa de cores
                marker=dict(size=6)
            ))

        fig.update_layout(
            title="Quantidade de Lançamentos por Hora e Ano",
            xaxis_title="Hora do Dia",
            yaxis_title="Quantidade de Lançamentos",
            plot_bgcolor='rgb(17,17,17)',  # Cor de fundo
            paper_bgcolor='rgb(17,17,17)',  # Cor do papel
            font=dict(color="white"),  # Cor da fonte
            hovermode='closest'  # Hover em cada ponto
        )

        st.plotly_chart(fig)

        # Visualização "Anual"
        st.write(f"Analisando pedidos por mês")

        # Agrupar os dados por mês
        df_agrupado_anual = df_pedidos2023.groupby(
            df_pedidos2023['data_lancamento'].dt.to_period('M')).size().reset_index(name='quantidade_lancamentos')
        df_agrupado_anual['month'] = df_agrupado_anual['data_lancamento'].dt.month

        # Convertemos os números de mês em objetos datetime para usar o strftime e garantir os nomes em português
        df_agrupado_anual['month_name'] = pd.to_datetime(df_agrupado_anual['month'].astype(str),
                                                         format='%m').dt.strftime('%B')

        # Ordenar os meses pela ordem correta (de janeiro a dezembro)
        df_agrupado_anual['month_name'] = pd.Categorical(df_agrupado_anual['month_name'], categories=[
            'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro',
            'novembro', 'dezembro'
        ], ordered=True)

        # Agrupar os dados por ano
        df_agrupado_anual['year'] = df_agrupado_anual['data_lancamento'].dt.year

        # Ordenar pelos meses e anos
        df_agrupado_anual = df_agrupado_anual.sort_values(by=['month', 'year'])

        # Gerar gráfico de barras agrupadas para os lançamentos por mês e ano
        fig = go.Figure()

        # Adicionando as barras para cada ano
        for year in df_agrupado_anual['year'].unique():
            year_data = df_agrupado_anual[df_agrupado_anual['year'] == year]
            fig.add_trace(go.Bar(
                x=year_data['month_name'],
                y=year_data['quantidade_lancamentos'],
                name=str(year),
                marker=dict(color=color_map.get(year, '#cccccc'))  # Cor específica para o ano
            ))

        fig.update_layout(
            title="Quantidade de Lançamentos por Mês e Ano",
            xaxis_title="Mês",
            yaxis_title="Quantidade de Lançamentos",
            barmode='group',  # Modo de barras agrupadas
            plot_bgcolor='rgb(17,17,17)',  # Cor de fundo
            paper_bgcolor='rgb(17,17,17)',  # Cor do papel
            font=dict(color="white"),  # Cor da fonte
            hovermode='closest'  # Hover em cada ponto
        )

        st.plotly_chart(fig)

        # **Gráfico de comparação anual** - Contagem de pedidos por ano
        st.write("Comparando o número total de pedidos por ano")

        # Agrupar os dados por ano e contar o número de registros (pedidos)
        df_total_anual = df_pedidos2023.groupby(df_pedidos2023['data_lancamento'].dt.year).size().reset_index(
            name='quantidade_pedidos')

        # Gerar gráfico de barras para o total de pedidos por ano
        fig_total = go.Figure()

        # Adicionando barras para cada ano
        for ano in [2023, 2024, 2025]:
            if ano in df_total_anual['data_lancamento'].values:
                df_ano = df_total_anual[df_total_anual['data_lancamento'] == ano]
                fig_total.add_trace(go.Bar(
                    x=df_ano['data_lancamento'],
                    y=df_ano['quantidade_pedidos'],
                    name=str(ano),
                    marker=dict(color=color_map.get(ano, '#cccccc'))  # Cor de barras conforme o ano
                ))

        # Atualizar layout para gráfico de barras
        fig_total.update_layout(
            title="Total de Pedidos por Ano",
            xaxis_title="Ano",
            yaxis_title="Total de Pedidos",
            yaxis=dict(tickformat="d"),  # Formatar o eixo Y para mostrar números inteiros
            plot_bgcolor='rgb(17,17,17)',  # Cor de fundo
            paper_bgcolor='rgb(17,17,17)',  # Cor do papel
            font=dict(color="white"),  # Cor da fonte
            hovermode='closest'  # Hover em cada ponto
        )

        st.plotly_chart(fig_total)

    # Chama a função para exibir a análise
    exibir_analise()

if __name__ == "__main__":
    main()
