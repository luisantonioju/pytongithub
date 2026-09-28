"""
SISTEMA DE CADASTRO DE ALUNOS — PROJETO TEMPLATE
==================================================

Este arquivo é um MODELO (template) para o seu projeto pessoal.

Ele já usa tudo que vimos na Semana 2:
    - Layout com grid() e Frame (organização em blocos)
    - Entry, Label, Radiobutton, Listbox, Button
    - Validação de formulário com messagebox
    - Código organizado em uma classe (POO) + funções auxiliares
    - Salvamento e carregamento de dados em JSON

COMO ADAPTAR PARA O SEU PROJETO:
    1. Troque os campos do formulário (em criar_widgets) pelos do seu tema
       (ex: livro/autor/ano, tarefa/prioridade/prazo, contato/telefone/e-mail...).
    2. Ajuste o dicionário criado em cadastrar_aluno() com os novos campos.
    3. Ajuste a linha exibida na Listbox, em atualizar_lista().
    4. O resto da estrutura (classe, salvar/carregar em JSON, validação,
       botões de ação) pode ser reaproveitado quase sem mudanças.

Para rodar: python cadastro_alunos.py
"""

import tkinter as tk
from tkinter import messagebox
import json
import os

# Nome do arquivo onde os cadastros ficam salvos.
# Fica na mesma pasta do programa.
ARQUIVO_DADOS = "alunos.json"


class App(tk.Tk):
    """
    Janela principal da aplicação.

    Cada widget importante vira um atributo (self.algo) para que qualquer
    método da classe consiga acessá-lo depois — é assim que organizamos
    projetos maiores em vez de deixar tudo em variáveis soltas.
    """

    def __init__(self):
        super().__init__()
        self.title("Sistema de Cadastro de Alunos")
        self.geometry("540x520")
        self.resizable(False, False)
        self.configure(bg="#FFFFFF")

        # Variáveis ligadas aos campos do formulário (StringVar).
        # Elas guardam o valor atual do widget e permitem ler/limpar
        # os campos com .get() / .set(), sem precisar caçar cada widget.
        self.var_nome = tk.StringVar()
        self.var_idade = tk.StringVar()
        self.var_curso = tk.StringVar()
        self.var_turno = tk.StringVar(value="Manhã")

        # Lista em memória com os alunos já cadastrados.
        # Começa carregando o que já existe no arquivo JSON (se existir).
        self.alunos = carregar_dados()

        self.criar_widgets()
        self.atualizar_lista()

    # ------------------------------------------------------------------
    # CONSTRUÇÃO DA INTERFACE
    # ------------------------------------------------------------------
    def criar_widgets(self):
        """Cria e organiza todos os widgets da janela."""

        # ----- Frame 1: dados do aluno (formulário em grid) -----
        frame_dados = tk.Frame(self, padx=20, pady=20)
        frame_dados.pack(fill="x")

        tk.Label(frame_dados, text="Nome Completo:", font=("Calibri", 11)) \
            .grid(row=0, column=0, sticky="w", pady=6)
        tk.Entry(frame_dados, textvariable=self.var_nome, width=32) \
            .grid(row=0, column=1, columnspan=3, sticky="w")

        tk.Label(frame_dados, text="Idade:", font=("Calibri", 11)) \
            .grid(row=1, column=0, sticky="w", pady=6)
        tk.Entry(frame_dados, textvariable=self.var_idade, width=8) \
            .grid(row=1, column=1, sticky="w")

        tk.Label(frame_dados, text="Curso:", font=("Calibri", 11)) \
            .grid(row=2, column=0, sticky="w", pady=6)
        tk.Entry(frame_dados, textvariable=self.var_curso, width=32) \
            .grid(row=2, column=1, columnspan=3, sticky="w")

        tk.Label(frame_dados, text="Turno:", font=("Calibri", 11)) \
            .grid(row=3, column=0, sticky="w", pady=6)
        # Um Radiobutton por opção de turno, todos ligados à mesma StringVar
        # -> só um pode ficar selecionado por vez.
        for i, turno in enumerate(["Manhã", "Tarde", "Noite"]):
            tk.Radiobutton(
                frame_dados, text=turno, variable=self.var_turno, value=turno
            ).grid(row=3, column=1 + i, sticky="w")

        # ----- Frame 2: botões de ação -----
        frame_botoes = tk.Frame(self, padx=20, pady=8)
        frame_botoes.pack(fill="x")

        tk.Button(
            frame_botoes, text="Cadastrar", command=self.cadastrar_aluno,
            bg="#06B6D4", fg="white", activebackground="#0891B2",
            relief="flat", padx=12, pady=6,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            frame_botoes, text="Remover selecionado", command=self.remover_aluno,
            padx=12, pady=6,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            frame_botoes, text="Limpar campos", command=self.limpar_campos,
            padx=12, pady=6,
        ).pack(side="left")

        # ----- Frame 3: lista de alunos cadastrados -----
        frame_lista = tk.Frame(self, padx=20, pady=12)
        frame_lista.pack(fill="both", expand=True)

        tk.Label(frame_lista, text="Alunos cadastrados:", font=("Calibri", 11, "bold")) \
            .pack(anchor="w")

        # Um Frame só para juntar a Listbox com uma barra de rolagem.
        frame_lb = tk.Frame(frame_lista)
        frame_lb.pack(fill="both", expand=True, pady=(6, 0))

        scrollbar = tk.Scrollbar(frame_lb)
        scrollbar.pack(side="right", fill="y")

        self.lista_alunos = tk.Listbox(
            frame_lb, yscrollcommand=scrollbar.set, font=("Consolas", 10)
        )
        self.lista_alunos.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.lista_alunos.yview)

    # ------------------------------------------------------------------
    # AÇÕES DO USUÁRIO
    # ------------------------------------------------------------------
    def cadastrar_aluno(self):
        """Valida os campos e adiciona um novo aluno à lista + arquivo."""
        nome = self.var_nome.get().strip()
        idade = self.var_idade.get().strip()
        curso = self.var_curso.get().strip()
        turno = self.var_turno.get()

        # Validação: nome e curso não podem ficar vazios.
        if not nome or not curso:
            messagebox.showwarning(
                "Campos vazios", "Preencha nome e curso antes de cadastrar."
            )
            return

        # Validação: idade precisa ser um número.
        if not idade.isdigit():
            messagebox.showwarning(
                "Idade inválida", "A idade deve ser um número (ex: 18)."
            )
            return

        # Se passou pelas validações, monta o dicionário do aluno...
        aluno = {"nome": nome, "idade": int(idade), "curso": curso, "turno": turno}
        # ...adiciona na lista em memória...
        self.alunos.append(aluno)
        # ...e salva tudo no arquivo, para não perder ao fechar o programa.
        salvar_dados(self.alunos)

        self.atualizar_lista()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", f"Aluno \"{nome}\" cadastrado!")

    def remover_aluno(self):
        """Remove o aluno selecionado na Listbox."""
        selecionado = self.lista_alunos.curselection()

        if not selecionado:
            messagebox.showwarning(
                "Nenhum aluno selecionado",
                "Clique em um aluno da lista antes de remover.",
            )
            return

        indice = selecionado[0]
        aluno_removido = self.alunos.pop(indice)
        salvar_dados(self.alunos)
        self.atualizar_lista()
        messagebox.showinfo("Removido", f"Aluno \"{aluno_removido['nome']}\" removido.")

    def limpar_campos(self):
        """Limpa o formulário, sem mexer na lista de alunos."""
        self.var_nome.set("")
        self.var_idade.set("")
        self.var_curso.set("")
        self.var_turno.set("Manhã")

    # ------------------------------------------------------------------
    # ATUALIZAÇÃO DA TELA
    # ------------------------------------------------------------------
    def atualizar_lista(self):
        """Redesenha a Listbox a partir de self.alunos."""
        self.lista_alunos.delete(0, "end")
        for aluno in self.alunos:
            linha = (
                f"{aluno['nome']:<20} {aluno['idade']:>3} anos   "
                f"{aluno['curso']:<15} {aluno['turno']}"
            )
            self.lista_alunos.insert("end", linha)


# ----------------------------------------------------------------------
# PERSISTÊNCIA (funções auxiliares, fora da classe)
# ----------------------------------------------------------------------
# Ficam fora da classe porque não dependem da interface — só leem e
# escrevem no arquivo. Isso facilita reaproveitá-las em outro projeto.

def salvar_dados(alunos):
    """Salva a lista de alunos no arquivo JSON."""
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(alunos, arquivo, ensure_ascii=False, indent=2)


def carregar_dados():
    """Carrega a lista de alunos do arquivo JSON, se ele existir."""
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