import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Relatório de Acessos", layout="centered")

st.title("📊 Relatório de Acessos ao Parque")

arquivo = st.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

if arquivo:
    try:
        df = pd.read_excel(arquivo)

        if df.shape[1] < 2:
            st.error("O arquivo deve conter ao menos duas colunas: Código e Categoria.")
        else:
            df.columns = ["Código", "Categoria"]

            # Atualiza nomes conforme solicitado
            df["Categoria"] = df["Categoria"].replace({
                "INGRESSO ADULTO": "INGRESSO ADULTO PROMOCIONAL",
                "INGRESSO INFANTIL": "INGRESSO INFANTIL PROMOCIONAL"
            })

            # Define categorias do grupo DAY-USER
            dayuser_categorias = [
                "INGRESSO ADULTO PROMOCIONAL",
                "INGRESSO COMBO",
                "INGRESSO ESPECIAL",
                "INGRESSO INFANTIL PROMOCIONAL"
            ]

            df["Categoria Agrupada"] = df["Categoria"].apply(
                lambda x: "DAY-USER" if x in dayuser_categorias else x
            )

            # Contagem
            contagem = df["Categoria Agrupada"].value_counts()

            # Lista de categorias na ordem desejada
            primeira_parte = [
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
            ]

            segunda_parte = [
                "INGRESSO BEBÊ",
                "CASA DA ÁRVORE",
                "ECO LOUNGE",
                "SEGURO CHUVA",
            ]

            # Soma da primeira parte (TOTAL:)
            total1 = contagem.reindex(primeira_parte, fill_value=0).sum()

            # Monta DataFrame formatado
            linhas = []

            for categoria in primeira_parte:
                linhas.append((categoria, contagem.get(categoria, 0)))

            linhas.append(("TOTAL:", total1))
            linhas.append(("", ""))  # linha em branco

            for categoria in segunda_parte:
                linhas.append((categoria, contagem.get(categoria, 0)))

            total2 = contagem.reindex(segunda_parte, fill_value=0).sum()
            linhas.append(("TOTAL (LIMBER):", total2))

            resultado_df = pd.DataFrame(linhas, columns=["Categoria", "Quantidade"])

            # Exibir resultado
            st.subheader("Resumo de Categorias")
            st.table(resultado_df)  # Exibe sem barra de rolagem

            # Download Excel
            output = BytesIO()
            resultado_df.to_excel(output, index=False)
            st.download_button("📥 Baixar Relatório Excel", data=output.getvalue(), file_name="relatorio_acessos.xlsx")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, envie um arquivo Excel com as colunas Código e Categoria.")
