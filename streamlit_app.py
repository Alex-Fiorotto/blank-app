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

            mapeamento = {
    "INGRESSO ADULTO": "INGRESSO ADULTO PROMOCIONAL",
    "INGRESSO INFANTIL": "INGRESSO INFANTIL PROMOCIONAL",
    "INGRESSO ANIVERSARIANTE": "ANIVERSARIANTES",
    "INGRESSO EXCURSÃO": "EXCURSAO",
    "INGRESSO BANDA": "BANDA",
    "CORTESIA COLABORADOR": "FUNCIONÁRIOS",
    "AGENDAMENTO – CONSULTORES": "AGEND CONS VENDAS",
    "CORTESIA AÇÃO PROMOCIONAL": "AÇOES PROMOCIONAIS",
    # Novos mapeamentos para ECOVIP
    "ECOVIP S/ CADASTRO": "ECOVIP",
    "ECOVIP S/ CARTEIRINHA": "ECOVIP",
    "EcoVip s/ Cadastro": "ECOVIP",
    "EcoVip s/ carteirinha": "ECOVIP"
            }

            # Aplica o mapeamento
            df["Categoria Normalizada"] = df["Categoria"].replace(mapeamento)

            # Define categorias dos grupos
            dayuser_categorias = [
                "INGRESSO ADULTO PROMOCIONAL",
                "INGRESSO COMBO",
                "INGRESSO ESPECIAL",
                "INGRESSO INFANTIL PROMOCIONAL",
                "INGRESSO ADULTO + FEIJOADA",
                "INGRESSO INFANTIL + FEIJOADA"
            ]

            ecovip_categorias = [
                "EcoVip s/ Cadastro",
                "EcoVip s/ carteirinha"
            ]

            # Agrupamento das categorias finais
            def agrupar_categoria(cat):
    cat_str = str(cat).upper()  # Garante que é string e em maiúsculas
    if cat_str in [c.upper() for c in dayuser_categorias]:
        return "DAY-USER"
    elif any(ecovip in cat_str for ecovip in ["ECOVIP", "ECO VIP"]):  # Verifica variações
        return "ECOVIP"
    return cat

            df["Categoria Final"] = df["Categoria Normalizada"].apply(agrupar_categoria)

            # Ordem das categorias no relatório
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

            contagem = df["Categoria Final"].value_counts()

            total1 = contagem.reindex(primeira_parte, fill_value=0).sum()
            total2 = contagem.reindex(segunda_parte, fill_value=0).sum()

            linhas = []
            for cat in primeira_parte:
                linhas.append((cat, contagem.get(cat, 0)))

            linhas.append(("TOTAL:", total1))
            linhas.append(("", ""))  # linha em branco

            for cat in segunda_parte:
                linhas.append((cat, contagem.get(cat, 0)))

            linhas.append(("TOTAL (LIMBER):", total2))

            resultado_df = pd.DataFrame(linhas, columns=["Categoria", "Quantidade"])

            st.subheader("Resumo de Categorias")
            st.table(resultado_df)

            # Exportação
            output = BytesIO()
            resultado_df.to_excel(output, index=False)
            st.download_button("📥 Baixar Relatório Excel", data=output.getvalue(), file_name="relatorio_acessos.xlsx")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, envie um arquivo Excel com as colunas Código e Categoria.")
