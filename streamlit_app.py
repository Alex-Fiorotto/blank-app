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
                # Day User
                "INGRESSO COMBO": "DAY-USER",
                "INGRESSO ADULTO PROMOCIONAL": "DAY-USER",
                "INGRESSO INFANTIL PROMOCIONAL": "DAY-USER",
                "INTEIRA INFANTIL BILHETERIA": "DAY-USER",
                "INGRESSO ADULTO BILHETERIA": "DAY-USER",
                "INGRESSO INFANTIL + ALMOÇO": "DAY-USER",
                "INGRESSO ESPECIAL": "DAY-USER",

                # Day User (com feijoada)
                "INGRESSO ADULTO + FEIJOADA": "DAY-USER",
                "INGRESSO INFANTIL + FEIJOADA": "DAY-USER",

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

                # Multiclubes
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
            df["Categoria"] = df["Categoria"].fillna("").astype(str).str.strip().str.upper()
            df["Categoria Final"] = df["Categoria"].replace({k.upper(): v for k, v in mapeamento_final.items()})

            # Filtro por período
            datas_disponiveis = sorted(df['Data'].dropna().unique())
            if len(datas_disponiveis) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    data_inicio = st.date_input("Selecione a data inicial", value=min(datas_disponiveis),
                                               min_value=min(datas_disponiveis), max_value=max(datas_disponiveis))
                with col2:
                    data_fim = st.date_input("Selecione a data final", value=max(datas_disponiveis),
                                            min_value=min(datas_disponiveis), max_value=max(datas_disponiveis))

                # Filtra os dados entre as datas selecionadas
                df_filtrado = df[(df['Data'] >= data_inicio) & (df['Data'] <= data_fim)]
                st.success(f"Mostrando dados de **{data_inicio}** até **{data_fim}**")
            else:
                st.warning("Nenhuma data válida encontrada no arquivo. Usando todos os dados disponíveis.")
                df_filtrado = df

            # Contagem por categoria
            if "Categoria Final" not in df_filtrado.columns:
                st.error("⚠️ Coluna 'Categoria Final' não foi criada corretamente. Verifique as categorias do arquivo.")
                st.stop()

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

            # Parte 3: categorias não mapeadas
            todas_categorias_mapeadas = set(k.upper() for k in mapeamento_final.keys())
            mascara_nao_mapeada = ~df_filtrado["Categoria"].str.upper().isin(todas_categorias_mapeadas)
            nao_mapeadas_df = df_filtrado[mascara_nao_mapeada]["Categoria"]
            contagem_nao_mapeadas = nao_mapeadas_df.value_counts()

            if not contagem_nao_mapeadas.empty:
                linhas.append(("", ""))
                linhas.append(("CATEGORIAS NÃO MAPEADAS:", ""))
                for subcat, val in contagem_nao_mapeadas.items():
                    linhas.append((subcat, val))

            resultado_df = pd.DataFrame(linhas, columns=["Categoria", "Quantidade"])

            # Exibição do relatório
            st.subheader(f"Resumo de Acessos {f'(de {data_inicio} a {data_fim})' if len(datas_disponiveis) > 0 else ''}")
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
