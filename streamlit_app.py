import streamlit as st
import pandas as pd
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Relatório de Acessos", layout="centered")
st.title("📊 Relatório de Acessos ao Parque")

# Upload do arquivo
arquivo = st.file_uploader("Faça o upload do arquivo Excel", type=["xlsx"])

if arquivo:
    try:
        # Leitura do arquivo
        df = pd.read_excel(arquivo)
        
        # Verificação das colunas
        if df.shape[1] < 2:
            st.error("O arquivo deve conter ao menos duas colunas: Localizador e Categoria.")
        else:
            # Renomeia colunas
            df.columns = ["Localizador", "Categoria"]
            
            # Mapeamento de categorias
            mapeamento = {
                "INGRESSO ADULTO": "INGRESSO ADULTO PROMOCIONAL",
                "INGRESSO INFANTIL": "INGRESSO INFANTIL PROMOCIONAL",
                "INGRESSO ANIVERSARIANTE": "ANIVERSARIANTES",
                "INGRESSO EXCURSÃO": "EXCURSAO",
                "INGRESSO EXCURSÃO": "EXCURSAO",  # variação de digitação
                "INGRESSO BANDA": "BANDA",
                "CORTESIA COLABORADOR": "FUNCIONÁRIOS",
                "AGENDAMENTO – CONSULTORES": "AGEND CONS VENDAS",
                "AGENDAMENTO - CONSULTORES": "AGEND CONS VENDAS",
                "CORTESIA AÇÃO PROMOCIONAL": "AÇOES PROMOCIONAIS",
                "FEIJOADA 30": "ALMOÇO",
                # Mapeamentos para ECOVIP
                "ECOVIP S/ CADASTRO": "ECOVIP",
                "ECOVIP S/ CARTEIRINHA": "ECOVIP",
                "EcoVip s/ Cadastro": "ECOVIP",
                "EcoVip s/ carteirinha": "ECOVIP",
                "ECO VIP": "ECOVIP",
                "MULTICLUBES - DAY-USE": "DAY-USER"
            }
            
            # Normalização das categorias
            df["Categoria Normalizada"] = df["Categoria"].str.upper().replace(mapeamento)
            
            # Categorias para agrupamento
            dayuser_categorias = [
                "INGRESSO ADULTO PROMOCIONAL",
                "INGRESSO COMBO",
                "INGRESSO ESPECIAL",
                "INGRESSO INFANTIL PROMOCIONAL",
                "INGRESSO ADULTO + FEIJOADA",
                "INGRESSO INFANTIL + FEIJOADA",
                "MULTICLUBES - DAY-USE"
            ]
            
            # Função para agrupamento final
            def agrupar_categoria(cat):
                cat_str = str(cat).strip().upper()
                
                if cat_str in [c.upper() for c in dayuser_categorias]:
                    return "DAY-USER"
                elif "ECOVIP" in cat_str or "ECO VIP" in cat_str:
                    return "ECOVIP"
                return cat
            
            # Aplica o agrupamento final
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
            
            # Contagem por categoria
            contagem = df["Categoria Final"].value_counts()
            
            # Cálculo dos totais
            total1 = contagem.reindex(primeira_parte, fill_value=0).sum()
            total2 = contagem.reindex(segunda_parte, fill_value=0).sum()
            
            # Preparação dos dados para exibição
            linhas = []
            for cat in primeira_parte:
                linhas.append((cat, contagem.get(cat, 0)))
            
            linhas.append(("TOTAL:", total1))
            linhas.append(("", ""))  # linha em branco
            
            for cat in segunda_parte:
                linhas.append((cat, contagem.get(cat, 0)))
            
            linhas.append(("TOTAL (LIMBER):", total2))
            
            resultado_df = pd.DataFrame(linhas, columns=["Categoria", "Quantidade"])
            
            # Exibição dos resultados
            st.subheader("Resumo de Categorias")
            st.dataframe(resultado_df, hide_index=True)
            
            # Adicionando gráfico de barras
            st.subheader("Distribuição de Acessos")
            st.bar_chart(contagem[primeira_parte])
            
            # Exportação para Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                resultado_df.to_excel(writer, index=False, sheet_name='Resumo')
                df.to_excel(writer, sheet_name='Dados Completos')
            
            st.download_button(
                "📥 Baixar Relatório Completo",
                data=output.getvalue(),
                file_name="relatorio_acessos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Opcional: Mostrar dados brutos
            if st.checkbox("Mostrar dados brutos"):
                st.subheader("Dados Brutos")
                st.dataframe(df)
    
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {str(e)}")
        st.error("Verifique se o arquivo está no formato correto.")
else:
    st.info("Por favor, envie um arquivo Excel com as colunas Localizador e Categoria.") file_name="relatorio_acessos.xlsx"

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.info("Por favor, envie um arquivo Excel com as colunas Código e Categoria.")
