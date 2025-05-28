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
            # Renomeia colunas
            df.columns = ["Localizador", "Categoria", "Data_Hora"]

            # Converte data/hora
            df['Data_Hora'] = pd.to_datetime(df['Data_Hora'], dayfirst=True, errors='coerce')
            df['Data'] = df['Data_Hora'].dt.date

            # Mapeamento final das categorias
            mapeamento_final = {
                "INGRESSO COMBO": "DAY-USER",
                "INGRESSO ADULTO PROMOCIONAL": "DAY-USER",
                "INGRESSO INFANTIL PROMOCIONAL": "DAY-USER",
                "INGRESSO BEBÊ": "INGRESSO BEBÊ",
                "INGRESSO ANIVERSARIANTE": "ANIVERSARIANTES",
                "INGRESSO ADULTO + FEIJOADA": "DAY-USER",
                "INGRESSO INFANTIL + FEIJOADA": "DAY-USER",
                "FEIJOADA 30": "ALMOÇO",
                "CORTESIA AÇÃO PROMOCIONAL": "AÇOES PROMOCIONAIS",
                "ECOVIP S/ CADASTRO": "ECOVIP",
                "EcoVip s/ Cadastro": "ECOVIP",
                "MULTICLUBES - DAY-USE": "DAY-USER",
                "VISITA GUIADA": "VISITA GUIADA",
                "AGENDAMENTO - CONSULTORES": "AGEND CONS VENDAS",
                "INGRESSO BANDA": "BANDA",
                "INGRESSO ESPECIAL": "DAY-USER",
                "CORTESIA COLABORADOR": "FUNCIONÁRIOS",
                "CASA DA ÁRVORE": "CASA DA ÁRVORE",
                "ECO LOUNGE": "ECO LOUNGE",
                "SEGURO CHUVA": "SEGURO CHUVA"
            }

            # Aplica mapeamento final
            df["Categoria Final"] = df["Categoria"].str.strip().str.upper().replace({k.upper(): v for k, v in mapeamento_final.items()})

            # Categorias que aparecem no relatório
            ordem_relatorio = [
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
                "",  # linha em branco
                "TOTAL:",
                "",
                "INGRESSO BEBÊ",
                "CASA DA ÁRVORE",
                "ECO LOUNGE",
                "SEGURO CHUVA",
                "",
                "TOTAL (LIMBER):"
            ]

            # Filtro por data
            datas_disponiveis = df['Data'].dropna().unique()
            if len(datas_disponiveis) > 0:
                data_selecionada = st.selectbox(
                    "Selecione a data para análise:",
                    options=["Todos os dias"] + sorted(datas_disponiveis.tolist())
                )

                if data_selecionada != "Todos os dias":
                    df_filtrado = df[df['Data'] == data_selecionada]
                else:
                    df_filtrado = df
            else:
                st.warning("Nenhuma data válida encontrada no arquivo.")
                df_filtrado = df

            # Contagem por categoria
            contagem = df_filtrado["Categoria Final"].value_counts()

            # Gera linhas do relatório
            linhas = []
            total1 = 0
            parte1 = [
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
                "AÇOES PROMOCIONAIS"
            ]
            for cat in parte1:
                valor = contagem.get(cat, 0)
                total1 += valor
                linhas.append((cat, valor))
            linhas.append(("TOTAL:", total1))
            linhas.append(("", ""))  # linha em branco

            parte2 = [
                "INGRESSO BEBÊ",
                "CASA DA ÁRVORE",
                "ECO LOUNGE",
                "SEGURO CHUVA"
            ]
            total2 = 0
            for cat in parte2:
                valor = contagem.get(cat, 0)
                total2 += valor
                linhas.append((cat, valor))
            linhas.append(("TOTAL (LIMBER):", total2))

            resultado_df = pd.DataFrame(linhas, columns=["Categoria", "Quantidade"])

            # Exibição do relatório
            st.subheader(f"Resumo de Acessos {f'- {data_selecionada}' if data_selecionada != 'Todos os dias' else ''}")
            st.dataframe(resultado_df, hide_index=True)

            # Exportação para Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                resultado_df.to_excel(writer, index=False, sheet_name='Resumo')

                if len(datas_disponiveis) > 1:
                    resumo_diario = df.groupby(['Data', 'Categoria Final']).size().unstack(fill_value=0)
                    resumo_diario.to_excel(writer, sheet_name='Por Data')

                df.to_excel(writer, sheet_name='Dados Completos')

            st.download_button(
                label="📥 Baixar Relatório Completo",
                data=output.getvalue(),
                file_name=f"relatorio_acessos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Mostrar dados brutos (opcional)
            if st.checkbox("Mostrar dados brutos"):
                st.subheader("Dados Brutos")
                st.dataframe(df)

    except Exception as e:
        st.error("Ocorreu um erro ao processar o arquivo. Verifique se o formato está correto.")
        st.error(f"Detalhes técnicos: {e}")
else:
    st.info("Por favor, envie um arquivo Excel com as colunas: Localizador, Categoria e Data/Hora.")
