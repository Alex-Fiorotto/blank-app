import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Relatório de Acessos", layout="centered")

st.title("📊 Relatório de Acessos ao Parque")

# Upload do arquivo
arquivo = st.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

if arquivo:
    try:
        df = pd.read_excel(arquivo)

        # Verifica se há colunas suficientes
        if df.shape[1] < 2:
            st.error("O arquivo deve conter ao menos duas colunas: Código e Categoria.")
        else:
            df.columns = ["Código", "Categoria"]

            # Define as categorias que compõem o grupo DAY-USER
            dayuser_categorias = [
                "INGRESSO ADULTO",
                "INGRESSO COMBO",
                "INGRESSO ESPECIAL",
                "INGRESSO INFANTIL"
            ]

            # Reclassifica para a categoria agrupada
            df["Categoria Agrupada"] = df["Categoria"].apply(
                lambda x: "DAY-USER" if x in dayuser_categorias else x
            )

            # Ordem final das categorias
            ordem_final = [
                "ECOVIP",
                "CORTESIA ECOVIP",
                "DAY-USER",
                "INGRESSO RETORNO",
                "AGEND CONS VENDAS",
                "ANIVERSARIANTES",
                "FUNCIONÁRIOS",
                "BANDA",
                "ALMOÇO",
                "VISITA GUIADA",
                "EXCURSAO",
                "AÇOES PROMOCIONAIS",
                "DESCONHECIDO",
                "TOTAL:",
                "INGRESSO BEBÊ",
                "CASA DA ÁRVORE",
                "ECO LOUNGE",
                "SEGURO CHUVA",
                "TOTAL (LIMBER):"
            ]

            # Contagem das categorias agrupadas
            contagem = df["Categoria Agrupada"].value_counts().reindex(ordem_final, fill_value=0)

            # Mostrar tabela
            st.subheader("Resumo de Categorias")
            st.dataframe(contagem.rename("Quantidade"))

            # Gerar Excel para download
            output = BytesIO()
            contagem_df = contagem.rename("Quantidade").reset_index()
            contagem_df.columns = ["Categoria", "Quantidade"]
            contagem_df.to_excel(output, index=False)
            st.download_button("📥 Baixar Relatório Excel", data=output.getvalue(), file_name="relatorio_acessos.xlsx")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, envie um arquivo Excel com as colunas Código e Categoria.")
