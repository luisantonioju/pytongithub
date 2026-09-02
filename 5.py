import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

ARQUIVO = "achou.json"

CORES = {
    "verde": "#2E7D32",
    "verde_claro": "#E8F5E9",
    "violeta": "#6A1B9A",
    "violeta_claro": "#F3E5F5",
    "branco": "#FFFFFF",
    "texto": "#263238"
}


# Carrega os itens salvos no arquivo JSON.
def carregar_itens():
    if not os.path.exists(ARQUIVO):
        return []

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (json.JSONDecodeError, OSError):
        return []


# Salva a lista de itens no arquivo JSON.
def salvar_itens():
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(itens, arquivo, ensure_ascii=False, indent=4)


itens = carregar_itens()


# Mostra os itens de acordo com os filtros escolhidos.
def atualizar_lista(*args):
    lista.delete(0, tk.END)

    palavra = busca_var.get().strip().lower()
    bloco = filtro_bloco_var.get()

    for item in itens:
        texto = f"{item['descricao']} - {item['bloco']}"
        if item["status"] == "Devolvido":
            texto += " [DEVOLVIDO]"

        encontrou_palavra = not palavra or palavra in texto.lower()
        encontrou_bloco = bloco == "Todos" or item["bloco"] == bloco

        if encontrou_palavra and encontrou_bloco:
            lista.insert(tk.END, texto)


# Cadastra um novo objeto perdido.
def cadastrar():
    descricao = descricao_var.get().strip()
    bloco = bloco_var.get()

    if not descricao:
        messagebox.showwarning("Atenção", "Digite a descrição do item.")
        entrada_descricao.focus()
        return

    if bloco == "Selecione o local":
        messagebox.showwarning("Atenção", "Selecione o bloco/local.")
        return

    itens.append({
        "descricao": descricao,
        "bloco": bloco,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Disponível"
    })

    salvar_itens()
    descricao_var.set("")
    bloco_var.set("Selecione o local")
    atualizar_lista()
    messagebox.showinfo("Sucesso", "Item cadastrado com sucesso!")
    entrada_descricao.focus()


# Marca o item selecionado como devolvido.
def marcar_devolvido():
    selecionado = lista.curselection()

    if not selecionado:
        messagebox.showwarning("Atenção", "Selecione um item na lista.")
        return

    palavra = busca_var.get().strip().lower()
    bloco = filtro_bloco_var.get()
    encontrados = []

    for indice, item in enumerate(itens):
        texto = f"{item['descricao']} - {item['bloco']}"
        if (not palavra or palavra in texto.lower()) and (bloco == "Todos" or item["bloco"] == bloco):
            encontrados.append(indice)

    indice_real = encontrados[selecionado[0]]

    if itens[indice_real]["status"] == "Devolvido":
        messagebox.showinfo("Informação", "Este item já foi marcado como devolvido.")
        return

    itens[indice_real]["status"] = "Devolvido"
    salvar_itens()
    atualizar_lista()
    messagebox.showinfo("Sucesso", "Item marcado como devolvido!")


# Janela principal.
janela = tk.Tk()
janela.title("Achados e Perdidos - Campus Unimar")
janela.geometry("850x650")
janela.minsize(720, 580)
janela.configure(bg=CORES["verde_claro"])

# Estilo dos componentes ttk.
style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox", padding=7, fieldbackground=CORES["branco"])
style.configure("Verde.TButton", background=CORES["verde"], foreground=CORES["branco"], padding=9, font=("Arial", 10, "bold"))
style.map("Verde.TButton", background=[("active", "#1B5E20")])
style.configure("Violeta.TButton", background=CORES["violeta"], foreground=CORES["branco"], padding=9, font=("Arial", 10, "bold"))
style.map("Violeta.TButton", background=[("active", "#4A148C")])

# Cabeçalho.
cabecalho = tk.Frame(janela, bg=CORES["violeta"], height=90)
cabecalho.pack(fill="x")
cabecalho.pack_propagate(False)

tk.Label(
    cabecalho,
    text="ACHADOS E PERDIDOS",
    font=("Arial", 24, "bold"),
    bg=CORES["violeta"],
    fg=CORES["branco"]
).pack(pady=(12, 2))

tk.Label(
    cabecalho,
    text="Central de objetos encontrados no Campus Unimar",
    font=("Arial", 11),
    bg=CORES["violeta"],
    fg=CORES["branco"]
).pack()

# Área de cadastro.
frame_cadastro = tk.LabelFrame(
    janela,
    text="  Cadastrar item encontrado  ",
    font=("Arial", 11, "bold"),
    bg=CORES["branco"],
    fg=CORES["verde"],
    padx=15,
    pady=12
)
frame_cadastro.pack(fill="x", padx=20, pady=18)

# Variáveis.
descricao_var = tk.StringVar()
bloco_var = tk.StringVar(value="Selecione o local")
busca_var = tk.StringVar()
filtro_bloco_var = tk.StringVar(value="Todos")

# Descrição.
tk.Label(frame_cadastro, text="Descrição do item:", bg=CORES["branco"], fg=CORES["texto"], font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
entrada_descricao = tk.Entry(frame_cadastro, textvariable=descricao_var, font=("Arial", 11), relief="solid", bd=1)
entrada_descricao.grid(row=1, column=0, sticky="ew", padx=(0, 15), ipady=6)

# Local/bloco.
tk.Label(frame_cadastro, text="Bloco / local:", bg=CORES["branco"], fg=CORES["texto"], font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w", pady=5)
bloco_combo = ttk.Combobox(
    frame_cadastro,
    textvariable=bloco_var,
    values=["Bloco 1", "Bloco 2", "Bloco 3", "Bloco 4", "Bloco 5", "Biblioteca", "Cantina", "Pátio", "Estacionamento", "Outro"],
    state="readonly"
)
bloco_combo.grid(row=1, column=1, sticky="ew", ipady=4)

frame_cadastro.columnconfigure(0, weight=3)
frame_cadastro.columnconfigure(1, weight=2)

# Botão cadastrar.
ttk.Button(frame_cadastro, text="+ Cadastrar", style="Verde.TButton", command=cadastrar).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))

# Área de busca.
frame_busca = tk.LabelFrame(
    janela,
    text="  Buscar objetos  ",
    font=("Arial", 11, "bold"),
    bg=CORES["branco"],
    fg=CORES["violeta"],
    padx=15,
    pady=12
)
frame_busca.pack(fill="x", padx=20, pady=(0, 12))

# Palavra-chave.
tk.Label(frame_busca, text="Palavra-chave:", bg=CORES["branco"], fg=CORES["texto"], font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
entrada_busca = tk.Entry(frame_busca, textvariable=busca_var, font=("Arial", 10), relief="solid", bd=1)
entrada_busca.grid(row=1, column=0, sticky="ew", padx=(0, 15), ipady=5)

# Filtro por bloco.
tk.Label(frame_busca, text="Filtrar por bloco/local:", bg=CORES["branco"], fg=CORES["texto"], font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w")
filtro_combo = ttk.Combobox(
    frame_busca,
    textvariable=filtro_bloco_var,
    values=["Todos", "Bloco 1", "Bloco 2", "Bloco 3", "Bloco 4", "Bloco 5", "Biblioteca", "Cantina", "Pátio", "Estacionamento", "Outro"],
    state="readonly"
)
filtro_combo.grid(row=1, column=1, sticky="ew", ipady=3)

frame_busca.columnconfigure(0, weight=3)
frame_busca.columnconfigure(1, weight=2)

busca_var.trace_add("write", atualizar_lista)
filtro_bloco_var.trace_add("write", atualizar_lista)

# Lista de itens.
frame_lista = tk.Frame(janela, bg=CORES["verde_claro"])
frame_lista.pack(fill="both", expand=True, padx=20, pady=5)

tk.Label(
    frame_lista,
    text="Itens registrados",
    font=("Arial", 12, "bold"),
    bg=CORES["verde_claro"],
    fg=CORES["verde"]
).pack(anchor="w", pady=(0, 6))

frame_listbox = tk.Frame(frame_lista, bg=CORES["branco"], bd=1, relief="solid")
frame_listbox.pack(fill="both", expand=True)

lista = tk.Listbox(
    frame_listbox,
    font=("Arial", 11),
    bg=CORES["branco"],
    fg=CORES["texto"],
    selectbackground=CORES["violeta"],
    selectforeground=CORES["branco"],
    activestyle="none",
    bd=0,
    highlightthickness=0
)
lista.pack(side="left", fill="both", expand=True, padx=5, pady=5)

scroll = tk.Scrollbar(frame_listbox, command=lista.yview)
scroll.pack(side="right", fill="y")
lista.config(yscrollcommand=scroll.set)

# Botão de devolução.
tk.Button(
    janela,
    text="✓ Marcar selecionado como devolvido",
    command=marcar_devolvido,
    bg=CORES["violeta"],
    fg=CORES["branco"],
    activebackground="#4A148C",
    activeforeground=CORES["branco"],
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2",
    padx=10,
    pady=10
).pack(fill="x", padx=20, pady=(8, 18))

atualizar_lista()
entrada_descricao.focus()
janela.mainloop()
