import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Relatório de Acessos", layout="centered")
st.title("📊 Relatório de Acessos ao Parque")

# Upload do arquivo
arquivo = st.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

if arquivo:
    try:
        # Leitura do arquivo
        df = pd.read_excel(arquivo)

        # Verifica se tem pelo menos 3 colunas
        if df.shape[1] < 3:
            st.error("O arquivo deve conter três colunas: Localizador, Categoria e Data/Hora.")
        else:
            # Renomeia colunas (ajuste conforme necessário)
            df.columns = ["Localizador", "Categoria", "Data_Hora"]

            # Converte data/hora
            df['Data_Hora'] = pd.to_datetime(df['Data_Hora'], dayfirst=True, errors='coerce')
            df['Data'] = df['Data_Hora'].dt.date

            # Mapeamento final das categorias
            mapeamento_final = {
                # Day User
                "INGRESSO COMBO": "DAY-USER",
                "INGRESSO ADULTO PROMOCIONAL": "DAY-USER",
                "INGRESSO INFANTIL PROMOCIONAL": "DAY-USER",
                "INTEIRA INFANTIL BILHETERIA": "DAY-USER",
                "INGRESSO ADULTO BILHETERIA": "DAY-USER",
                "INGRESSO INFANTIL + ALMOÇO": "DAY-USER",
                "INGRESSO ESPECIAL": "DAY-USER",

                # Almoço
                "INGRESSO ADULTO + ALMOÇO": "ALMOÇO",
                "APENAS ALMOÇO - ADULTO": "ALMOÇO",
                "APENAS ALMOÇO - INFANTIL": "ALMOÇO",

                # Ingresso Bebê
                "INGRESSO BEBÊ": "INGRESSO BEBÊ",
                "INGRESSO BEBÊ + ALMOÇO": "INGRESSO BEBÊ",

                # Visitas Guiadas
                "VISITA GUIADA": "VISITA GUIADA",

                # Excursão
                "INGRESSO EXCURSÃO": "EXCURSAO",

                # EcoVip
                "ECOVIP S/ CADASTRO": "ECOVIP",
                "EcoVip s/ Cadastro": "ECOVIP",
                "EcoVip s/ carteirinha": "ECOVIP",

                # Multiclubes (não é mais DAY-USER)
                "MULTICLUBES - DAY-USE": "MULTICLUBES - DAY-USE",

                # Agendamento Consultores
                "AGENDAMENTO - CONSULTORES": "AGEND CONS VENDAS",

                # Banda
                "INGRESSO BANDA": "BANDA",

                # Aniversariantes
                "INGRESSO ANIVERSARIANTE": "ANIVERSARIANTES",

                # Cortesias / Promoções
                "CORTESIA COLABORADOR": "FUNCIONÁRIOS",
                "CORTESIA AÇÃO PROMOCIONAL": "AÇOES PROMOCIONAIS",
                "CORTESIA RÁDIO TUPA": "AÇOES PROMOCIONAIS",
                "CORTESIA INFLUENCER": "AÇOES PROMOCIONAIS",
                "CORTESIA LIVE": "AÇOES PROMOCIONAIS",

                # Retorno
                "INGRESSO RETORNO": "INGRESSO RETORNO",

                # Outros
                "CASA DA ÁRVORE": "CASA DA ÁRVORE",
                "ECO LOUNGE": "ECO LOUNGE",
                "SEGURO CHUVA": "SEGURO CHUVA"
            }

            # Aplica mapeamento final
            df["Categoria Final"] = df["Categoria"].str.strip().str.upper().replace({k.upper(): v for k, v in mapeamento_final.items()})

            # Filtro por data
            datas_disponiveis = df['Data'].dropna().unique()
            if len(datas_disponiveis) >
