import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

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

def processar_arquivo():
    caminho = filedialog.askopenfilename(filetypes=[("Arquivos Excel", "*.xlsx")])
    if not caminho:
        return

    try:
        df = pd.read_excel(caminho)

        if 'Categoria' not in df.columns:
            messagebox.showerror("Erro", "A planilha deve conter uma coluna chamada 'Categoria'.")
            return

        # Aplica classificação
        df['Tipo de Acesso'] = df['Categoria'].apply(classificar_tipo)

        # Totalizador por tipo
        resumo_por_tipo = df['Tipo de Acesso'].value_counts().reset_index()
        resumo_por_tipo.columns = ['Tipo de Acesso', 'Total de Acessos']

        # Relatório analítico por categoria dentro de cada tipo
        analitico = df.groupby(['Tipo de Acesso', 'Categoria']).size().reset_index(name='Quantidade')

        # Cria planilha com duas abas
        nome_saida = os.path.join(os.path.dirname(caminho), "relatorio_acessos_formatado.xlsx")
        with pd.ExcelWriter(nome_saida, engine='openpyxl') as writer:
            resumo_por_tipo.to_excel(writer, index=False, sheet_name="Resumo por Tipo")
            analitico.to_excel(writer, index=False, sheet_name="Analítico por Categoria")

        messagebox.showinfo("Sucesso", f"Relatório com tipos salvo em:\n{nome_saida}")

    except Exception as e:
        messagebox.showerror("Erro ao processar", str(e))


# Interface gráfica
root = tk.Tk()
root.title("Relatório de Acessos por Tipo")
root.geometry("450x200")

label = tk.Label(root, text="Clique para selecionar a planilha de acessos com categorias")
label.pack(pady=20)

botao = tk.Button(root, text="Selecionar Planilha", command=processar_arquivo)
botao.pack(pady=10)

root.mainloop()
