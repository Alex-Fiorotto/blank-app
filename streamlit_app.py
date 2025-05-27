import pandas as pd
import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Relatório de Acessos", layout="centered")
st.title("📊 Relatório de Acessos por Categoria")

# Categorias que farão parte da linha "DAYUSER"
categorias_dayuser = {
    "INGRESSO ADULTO PROMOCIONAL",
    "INGRESSO ADULTO + FEIJOADA",
    "INGRESSO COMBO",
    "INGRESSO ESPECIAL"
}

uploaded_file = st.file_uploader("📁 Envie seu arquivo Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        if 'Categoria' not in df.columns:
            st.error("A planilha precisa conter uma coluna chamada 'Categoria'.")
        else:
            # Contagem por categoria
            resumo = df['Categoria'].value_counts().reset_index()
            resumo.columns = ['Categoria', 'Quantidade de Acessos']

            # Total da categoria agrupada "DAYUSER"
            total_dayuser = df[df['Categoria'].isin(categorias_dayuser)].shape[0]

            # Adiciona a linha DAYUSER
            resumo = pd.concat([
                resumo,
                pd.DataFrame([['DAYUSER', total_dayuser]], columns=['Categoria', 'Quantidade de Acessos'])
            ], ignore_index=True)

            # Mostra resultado
            st.subheader("Resumo dos Acessos:")
            st.dataframe(resumo)

            # Prepara para download
            output = BytesIO()
            resumo.to_excel(output, index=False, engine='openpyxl')
            st.download_button(
                label="📥 Baixar Relatório em Excel",
                data=output.getvalue(),
                file_name="relatorio_acessos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
