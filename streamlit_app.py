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

def gerar_relatorio(df):
    # Aplica classificação
    df['Tipo de Acesso'] = df['Categoria'].apply(classificar_tipo)

    # Totalizador por tipo
    resumo_por_tipo = df['Tipo de Acesso'].value_counts().reset_index()
    resumo_por_tipo.columns = ['Tipo de Acesso', 'Total de Acessos']

    # Relatório analítico
    analitico = df.groupby(['Tipo de Acesso', 'Categoria']).size().reset_index(name='Quantidade')

    # Gerar Excel com abas
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        resumo_por_tipo.to_excel(writer, index=False, sheet_name='Resumo por Tipo')
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
            relatorio = gerar_relatorio(df)
            st.download_button(
                label="📥 Baixar relatório Excel",
                data=relatorio,
                file_name="relatorio_acessos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")

