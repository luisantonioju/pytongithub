"""
SISTEMA DE CADASTRO — PROJETO TEMPLATE
=================================================

Este arquivo é um MODELO (template) adaptado para o projeto do Sistemaaaaaaaaaaatttttttt da
Unimar — Bloco 5 (cursos voltados para a área de T.I.).

Ele já usa tudo que vimos na Semana 2:
    - Layout com grid() e Frame (organização em blocos)
    - Entry, Label, Radiobutton, Listbox, Button
    - Validação de formulário com messagebox
    - Código organizado em uma classe (POO) + funções auxiliares
    - Salvamento e carregamento de dados em JSON

COMO ADAPTAR PARA O SEU PROJETO:
    1. Troque os campos do formulário (em criar_widgets) pelos do seu tema.
    2. Ajuste o dicionário criado em cadastrar_produto() com os novos campos.
    3. Ajuste a linha exibida na Listbox, em atualizar_lista().
    4. O resto da estrutura (classe, salvar/carregar em JSON, validação,
       botões de ação) pode ser reaproveitado quase sem mudanças.

Para rodar: python 3.py
"""

import tkinter as tk
from tkinter import messagebox
import json
import os

# Nome do arquivo onde os cadastros ficam salvos.
# Fica na mesma pasta do programa.
ARQUIVO_DADOS = "sistema.json"


class App(tk.Tk):
    """
    Janela principal da aplicação.

    Cada widget importante vira um atributo (self.algo) para que qualquer
    método da classe consiga acessá-lo depois — é assim que organizamos
    projetos maiores em vez de deixar tudo em variáveis soltas.
    """

    def __init__(self):
        super().__init__()
        self.title("Sstema Unimar — Bloco 5 | Cadastro")
        self.geometry("650x570")
        self.resizable(False, False)
        self.configure(bg="#F4F7FB")

        # Variáveis ligadas aos campos do formulário (StringVar).
        # Elas guardam o valor atual do widget e permitem ler/limpar
        # os campos com .get() / .set(), sem precisar caçar cada widget.
        self.var_produto = tk.StringVar()
        self.var_categoria = tk.StringVar()
        self.var_preco = tk.StringVar()
        self.var_quantidade = tk.StringVar()
        self.var_turno = tk.StringVar(value="Todos")

        # Lista em memória com os produtos já cadastrados.
        # Começa carregando o que já existe no arquivo JSON (se existir).
        self.produtos = carregar_dados()

        self.criar_widgets()
        self.atualizar_lista()

    # ------------------------------------------------------------------
    # CONSTRUÇÃO DA INTERFACE
    # ------------------------------------------------------------------
    def criar_widgets(self):
        """Cria e organiza todos os widgets da janela."""

        # ----- Cabeçalho do sistema -----
        frame_titulo = tk.Frame(self, bg="#123B5D", padx=20, pady=16)
        frame_titulo.pack(fill="x")

        tk.Label(frame_titulo, text="Sistema UNIMAR",
                 font=("Calibri", 20, "bold"), fg="white",
                 bg="#123B5D").pack(anchor="w")
        tk.Label(frame_titulo,
                 text="Bloco 5 • Área de T.I. | Cadastro",
                 font=("Calibri", 10), fg="#DCEAF5",
                 bg="#123B5D").pack(anchor="w", pady=(3, 0))

        # ----- Frame 1: dados do produto (formulário em grid) -----
        frame_dados = tk.Frame(self, bg="#FFFFFF", padx=20, pady=18)
        frame_dados.pack(fill="x", padx=16, pady=(16, 8))

        tk.Label(frame_dados, text="Produto:",
                 font=("Calibri", 11, "bold"), bg="#FFFFFF",
                 fg="#243447").grid(row=0, column=0, sticky="w", pady=6)
        tk.Entry(frame_dados, textvariable=self.var_produto, width=38,
                 font=("Calibri", 11)).grid(row=0, column=1,
                 columnspan=3, sticky="w")

        tk.Label(frame_dados, text="Categoria:",
                 font=("Calibri", 11, "bold"), bg="#FFFFFF",
                 fg="#243447").grid(row=1, column=0, sticky="w", pady=6)
        tk.Entry(frame_dados, textvariable=self.var_categoria, width=38,
                 font=("Calibri", 11)).grid(row=1, column=1,
                 columnspan=3, sticky="w")

        tk.Label(frame_dados, text="Preço (R$):",
                 font=("Calibri", 11, "bold"), bg="#FFFFFF",
                 fg="#243447").grid(row=2, column=0, sticky="w", pady=6)
        tk.Entry(frame_dados, textvariable=self.var_preco, width=12,
                 font=("Calibri", 11)).grid(row=2, column=1, sticky="w")

        tk.Label(frame_dados, text="Estoque:",
                 font=("Calibri", 11, "bold"), bg="#FFFFFF",
                 fg="#243447").grid(row=2, column=2, sticky="w", padx=(20, 6))
        tk.Entry(frame_dados, textvariable=self.var_quantidade, width=10,
                 font=("Calibri", 11)).grid(row=2, column=3, sticky="w")

        tk.Label(frame_dados, text="Disponível no turno:",
                 font=("Calibri", 11, "bold"), bg="#FFFFFF",
                 fg="#243447").grid(row=3, column=0, sticky="w", pady=6)
        # Um Radiobutton por opção de turno, todos ligados à mesma StringVar
        # -> só um pode ficar selecionado por vez.
        for i, turno in enumerate(["Todos", "Manhã", "Tarde", "Noite"]):
            tk.Radiobutton(frame_dados, text=turno,
                           variable=self.var_turno, value=turno,
                           bg="#FFFFFF", fg="#243447",
                           activebackground="#FFFFFF").grid(
                           row=3, column=1 + i, sticky="w")

        # ----- Frame 2: botões de ação -----
        frame_botoes = tk.Frame(self, bg="#F4F7FB", padx=16, pady=8)
        frame_botoes.pack(fill="x")

        tk.Button(frame_botoes, text="Cadastrar produto",
                  command=self.cadastrar_produto, bg="#06B6D4", fg="white",
                  activebackground="#0891B2", relief="flat",
                  padx=12, pady=7).pack(side="left", padx=(0, 8))
        tk.Button(frame_botoes, text="Remover selecionado",
                  command=self.remover_produto, padx=12, pady=7).pack(
                  side="left", padx=(0, 8))
        tk.Button(frame_botoes, text="Limpar campos",
                  command=self.limpar_campos, padx=12, pady=7).pack(side="left")

        # ----- Frame 3: lista de produtos cadastrados -----
        frame_lista = tk.Frame(self, bg="#FFFFFF", padx=16, pady=14)
        frame_lista.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        tk.Label(frame_lista, text="Produtos cadastrados na cantina:",
                 font=("Calibri", 11, "bold"), bg="#FFFFFF",
                 fg="#243447").pack(anchor="w")

        # Um Frame só para juntar a Listbox com uma barra de rolagem.
        frame_lb = tk.Frame(frame_lista, bg="#FFFFFF")
        frame_lb.pack(fill="both", expand=True, pady=(6, 0))

        scrollbar = tk.Scrollbar(frame_lb)
        scrollbar.pack(side="right", fill="y")

        self.lista_produtos = tk.Listbox(
            frame_lb, yscrollcommand=scrollbar.set, font=("Consolas", 9),
            height=8, selectbackground="#06B6D4", selectforeground="white"
        )
        self.lista_produtos.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.lista_produtos.yview)

    # ------------------------------------------------------------------
    # AÇÕES DO USUÁRIO
    # ------------------------------------------------------------------
    def cadastrar_produto(self):
        """Valida os campos e adiciona um novo produto à lista + arquivo."""
        produto = self.var_produto.get().strip()
        categoria = self.var_categoria.get().strip()
        preco = self.var_preco.get().strip().replace(",", ".")
        quantidade = self.var_quantidade.get().strip()
        turno = self.var_turno.get()

        # Validação: produto e categoria não podem ficar vazios.
        if not produto or not categoria:
            messagebox.showwarning("Campos vazios",
                                   "Preencha produto e categoria antes de cadastrar.")
            return

        # Validação: preço precisa ser um número válido.
        try:
            preco_numero = float(preco)
            if preco_numero < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Preço inválido",
                                   "Informe um preço válido (ex: 8,50).")
            return

        # Validação: estoque precisa ser um número inteiro.
        if not quantidade.isdigit():
            messagebox.showwarning("Estoque inválido",
                                   "O estoque deve ser um número inteiro (ex: 20).")
            return

        # Se passou pelas validações, monta o dicionário do produto...
        produto_cadastrado = {
            "produto": produto,
            "categoria": categoria,
            "preco": round(preco_numero, 2),
            "quantidade": int(quantidade),
            "turno": turno,
        }
        # ...adiciona na lista em memória...
        self.produtos.append(produto_cadastrado)
        # ...e salva tudo no arquivo, para não perder ao fechar o programa.
        salvar_dados(self.produtos)

        self.atualizar_lista()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", f"Produto \"{produto}\" cadastrado!")

    def remover_produto(self):
        """Remove o produto selecionado na Listbox."""
        selecionado = self.lista_produtos.curselection()

        if not selecionado:
            messagebox.showwarning("Nenhum produto selecionado",
                                   "Clique em um produto da lista antes de remover.")
            return

        indice = selecionado[0]
        produto_removido = self.produtos.pop(indice)
        salvar_dados(self.produtos)
        self.atualizar_lista()
        messagebox.showinfo("Removido",
                            f"Produto \"{produto_removido['produto']}\" removido.")

    def limpar_campos(self):
        """Limpa o formulário, sem mexer na lista de produtos."""
        self.var_produto.set("")
        self.var_categoria.set("")
        self.var_preco.set("")
        self.var_quantidade.set("")
        self.var_turno.set("Todos")

    # ------------------------------------------------------------------
    # ATUALIZAÇÃO DA TELA
    # ------------------------------------------------------------------
    def atualizar_lista(self):
        """Redesenha a Listbox a partir de self.produtos."""
        self.lista_produtos.delete(0, "end")
        for produto in self.produtos:
            linha = (
                f"{produto['produto']:<22} {produto['categoria']:<14} "
                f"R$ {produto['preco']:>7.2f}  "
                f"Est.: {produto['quantidade']:>3}  {produto['turno']}"
            )
            self.lista_produtos.insert("end", linha)


# ----------------------------------------------------------------------
# PERSISTÊNCIA (funções auxiliares, fora da classe)
# ----------------------------------------------------------------------
# Ficam fora da classe porque não dependem da interface — só leem e
# escrevem no arquivo. Isso facilita reaproveitá-las em outro projeto.

def salvar_dados(produtos):
    """Salva a lista de produtos no arquivo JSON."""
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(produtos, arquivo, ensure_ascii=False, indent=2)


def carregar_dados():
    """Carrega a lista de produtos do arquivo JSON, se ele existir."""
    if not os.path.exists(ARQUIVO_DADOS):
        return []
    with open(ARQUIVO_DADOS, encoding="utf-8") as arquivo:
        return json.load(arquivo)


# ----------------------------------------------------------------------
# PONTO DE ENTRADA DO PROGRAMA
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
