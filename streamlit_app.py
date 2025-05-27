import pandas as pd
import streamlit as st
from io import BytesIO

# Mapeamento dos tipos de acesso
def classificar_tipo(categoria):
    categoria = categoria.upper()

    if categoria in {
        "INGRESSO ADULTO PROMOCIONAL",
        "INGRESSO ADULTO + FEIJOADA",
        "INGRESSO COMBO",
        "INGRESSO ESPECIAL"
    }:
        return "DAY-USER PAGANTE"
    elif "ANIVERSARIANTE" in categoria or categoria == "INGRESSO BEBE":
        return "DAY-USER NÃO PAGANTE"
    else:
        return "OUTROS"

# Função para gerar os relatórios
def gerar_relatorios(df):
    df['Tipo de Acesso'] = df['Categoria'].apply(classificar_tipo)

    resumo_por_tipo = (
        df['Tipo de Acesso']
        .value_counts()
        .reset_index()
        .rename(columns={'index': 'Tipo de Acesso', 'Tipo de Acesso': 'Total de Acessos'})
    )

    analitico = (
        df.groupby(['Tipo de Acesso', 'Categoria'])
        .size()
        .reset_index(name='Quantidade')
        .sort_values(by=['Tipo de Acesso', 'Categoria'])
    )

    return resumo_por_tipo, analitico

# Função para gerar Excel com abas
def exportar_para_excel(resumo, analitico):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        resumo.to_excel(writer, index=False, sheet_name='Resumo por Tipo')
        analitico.to_excel(writer, index=False, sheet_name='Analítico por Categoria')
    buffer.seek(0)
    return buffer

# === INTERFACE STREAMLIT ===

st.set_page_config(page_title="Relatório de Acessos", layout="centered")
st.title("📊 Relatório de Acessos por Tipo")

uploaded_file = st.file_uploader("📂 Envie a planilha de acessos (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        if 'Categoria' not in df.columns:
            st.error("A planilha deve conter uma coluna chamada **Categoria**.")
        else:
            st.success("Arquivo carregado com sucesso!")

            resumo_por_tipo, analitico = gerar_relatorios(df)

            st.subheader("📌 Total por Tipo de Acesso")
            st.dataframe(resumo_por_tipo, use_container_width=True)

            st.subheader("📋 Analítico por Categoria")
            st.dataframe(analitico, use_container_width=True)

            # Download
            excel_file = exportar_para_excel(resumo_por_tipo, analitico)
            st.download_button(
                label="📥 Baixar relatório em Excel",
                data=excel_file,
                file_name="relatorio_acessos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
