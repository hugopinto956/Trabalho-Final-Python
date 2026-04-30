import mysql.connector
import hashlib
from datetime import date


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="troca_livros"
)

cursor = db.cursor(dictionary=True)

def encriptar(palavra):
    return hashlib.sha256(palavra.encode()).hexdigest()

def input_ou_voltar(msg):
    valor = input(msg).strip()
    return None if valor in ("0", "") else valor

#__________Registo Utilizador__________
def registar():
    print("\nRegisto (0 para voltar)")
    nome  = input_ou_voltar("Nome: ")
    if nome  is None: return
    email = input_ou_voltar("Email: ")
    if email is None: return
    senha = input_ou_voltar("Senha: ")
    if senha is None: return
    try:
        cursor.execute(
            "INSERT INTO UTILIZADOR (nome, email, password) VALUES (%s,%s,%s)",
            (nome, email, encriptar(senha))
        )
        db.commit()
        print("Utilizador registado!")
    except Exception as e:
        print("Erro ao registar:", e)

def login():
    print("\nLogin (0 para voltar)")

    nome = input_ou_voltar("Nome: ")
    if nome is None:
        return None

    senha = input_ou_voltar("Senha: ")
    if senha is None:
        return None

    h = encriptar(senha)

    cursor.execute(
        "SELECT * FROM UTILIZADOR WHERE nome=%s AND password=%s",
        (nome, h)
    )

    usuario = cursor.fetchone()

    if usuario:
        print("Login efetuado!")
        return usuario

    print("Login falhou! Verifique nome ou senha")
    return None

# Menu Utilizador

def menu_utilizador(usuario):
    while True:
        print(f"\nBem-vindo {usuario['nome']}")
        print("1 Adicionar livro")
        print("2 Ver os meus livros")
        print("3 Ver livros disponíveis")
        print("4 Pedir livro")
        print("5 Ver pedidos recebidos")
        print("6 Aceitar / Recusar pedido")
        print("7 Histórico de trocas")
        print("0 Sair")
        op = input("Escolha: ").strip()
        if   op == "1": adicionar_livro(usuario)
        elif op == "2": meus_livros(usuario)
        elif op == "3": ver_livros_disponiveis(usuario)
        elif op == "4": pedir_livro(usuario)
        elif op == "5": ver_pedidos_recebidos(usuario)
        elif op == "6": responder_pedido(usuario)
        elif op == "7": historico_trocas(usuario)
        elif op == "0": break
        else: print("Opção inválida!")

 
# ─────────────────────────────────────────────
#  1 - ADICIONAR LIVRO
# ─────────────────────────────────────────────
def adicionar_livro(usuario):
    print("\nAdicionar Livro (0 para voltar)")
 
    titulo = input_ou_voltar("Título: ")
    if titulo is None: return
 
    autor = input_ou_voltar("Autor: ")
    if autor is None: return
 
    genero = input_ou_voltar("Género (opcional, Enter para ignorar): ")
 
    print("Estado de conservação: 1 Novo  2 Bom  3 Usado")
    op = input("Escolha (1/2/3): ").strip()
    estados = {"1": "Novo", "2": "Bom", "3": "Usado"}
    estado = estados.get(op)
    if not estado:
        print("Estado inválido!")
        return
 
    try:
        cursor.execute(
            "INSERT INTO LIVRO (titulo, autor, genero, estado_conservacao, id_utilizador) VALUES (%s,%s,%s,%s,%s)",
            (titulo, autor, genero or None, estado, usuario["id_utilizador"])
        )
        db.commit()
        print("Livro adicionado com sucesso!")
    except Exception as e:
        print("Erro ao adicionar livro:", e)
 
 
# ─────────────────────────────────────────────
#  2 - VER OS MEUS LIVROS
# ─────────────────────────────────────────────
def meus_livros(usuario):
    cursor.execute("""
        SELECT * FROM LIVRO
        WHERE id_utilizador = %s
    """, (usuario["id_utilizador"],))

    livros = cursor.fetchall()

    if not livros:
        print("Nenhum livro registado.")
        return

    print(f"\n{'ID':<5} {'Título':<30} {'Autor':<25} {'Estado':<10}")
    print("─" * 75)

    for l in livros:
        print(f"{l['id_livro']:<5} {l['titulo']:<30} {l['autor']:<25} {l['estado_conservacao']:<10}")
        
# ─────────────────────────────────────────────
#  3 - VER LIVROS DISPONÍVEIS
# ─────────────────────────────────────────────
def ver_livros_disponiveis(usuario):
    cursor.execute("""
        SELECT L.id_livro, L.titulo, L.autor, L.estado_conservacao, U.nome AS dono
        FROM LIVRO L
        JOIN UTILIZADOR U ON L.id_utilizador = U.id_utilizador
        WHERE L.disponivel = TRUE
    """)
    livros = cursor.fetchall()
 
    if not livros:
        print("Não há livros disponíveis no momento.")
        return False
 
    print(f"\n{'ID':<5} {'Título':<30} {'Autor':<25} {'Estado':<10} {'Dono'}")
    print("─" * 80)
    for l in livros:
        print(f"{l['id_livro']:<5} {l['titulo']:<30} {l['autor']:<25} {l['estado_conservacao']:<10} {l['dono']}")
    return True