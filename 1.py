import tkinter as tk

def cumprimentar():
    nome = entrada_nome.get()
    idade = entrada_idade.get()
    mensagem.config(text=f"Olá, {nome}! Você tem {idade} anos.")

janela = tk.Tk()
janela.title("Meu Projeto")
janela.geometry("400x250")

tk.Label(janela, text="Digite seu nome:").pack()

entrada_nome = tk.Entry(janela)
entrada_nome.pack()

tk.Label(janela, text="Digite sua idade:").pack()

entrada_idade = tk.Entry(janela)
entrada_idade.pack()

tk.Button(janela, text="Enviar",
          command=cumprimentar).pack()

mensagem = tk.Label(janela, text="")
mensagem.pack()

janela.mainloop()
