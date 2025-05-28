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

            # Parte 1: principais categorias
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

            linhas = []
            total1 = 0
            for cat in parte1:
                valor = contagem.get(cat, 0)
                total1 += valor
                linhas.append((cat, valor))
            linhas.append(("TOTAL:", total1))
            linhas.append(("", ""))  # linha em branco

            # Parte 2: categorias secundárias
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

            # Parte 3: categorias não mapeadas
            categorias_presentes = df_filtrado["Categoria"].str.strip().str.upper()
            categorias_mapeadas_keys = set(k.upper() for k in mapeamento_final.keys())

            mascara_nao_mapeada = ~categorias_presentes.isin(categorias_mapeadas_keys)
            nao_mapeadas_df = df_filtrado.loc[mascara_nao_mapeada, "Categoria"]
            contagem_nao_mapeadas = nao_mapeadas_df.value_counts().reset_index()
            contagem_nao_mapeadas.columns = ["Categoria", "Quantidade"]

            if not contagem_nao_mapeadas.empty:
                linhas.append(("", ""))
                linhas.append(("CATEGORIAS NÃO MAPEADAS:", ""))
                for _, row in contagem_nao_mapeadas.iterrows():
                    linhas.append((row["Categoria"], row["Quantidade"]))

            resultado_df = pd.DataFrame(linhas, columns=["Categoria", "Quantidade"])

            # Exibição do relatório com expansão por categoria
            st.subheader(f"Resumo de Acessos {f'- {data_selecionada}' if data_selecionada != 'Todos os dias' else ''}")

            for _, row in resultado_df.iterrows():
                categoria = row["Categoria"]
                quantidade = row["Quantidade"]

                if categoria == "":
                    st.write("")
                    continue

                col1, col2 = st.columns([4, 1])
                col1.write(f"**{categoria}**")
                col2.write(str(quantidade))

                # Se for um grupo com composição, mostra detalhes
                if categoria in parte1 or categoria in parte2:
                    with st.expander("🔍 Ver detalhes"):
                        # Filtra as categorias originais que formam esse grupo
                        df_grupo = df_filtrado[df_filtrado["Categoria Final"] == categoria]
                        contagem_grupo = df_grupo["Categoria"].value_counts().reset_index()
                        contagem_grupo.columns = ["Categoria Original", "Quantidade"]

                        if not contagem_grupo.empty:
                            st.dataframe(contagem_grupo, hide_index=True)
                        else:
                            st.info("Nenhuma categoria original encontrada.")

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
