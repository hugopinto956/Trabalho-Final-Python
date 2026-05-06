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
#  3 - VER LIVROS DISPONIVEIS
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
 
 
# ─────────────────────────────────────────────
#  4 - PEDIR LIVRO
# ─────────────────────────────────────────────
def pedir_livro(usuario):
    if not ver_livros_disponiveis(usuario): return
 
    id_livro = input_ou_voltar("\nID do livro que queres pedir (0 para voltar): ")
    if id_livro is None: return
    if not id_livro.isdigit():
        print("ID inválido!")
        return
 
    cursor.execute(
        "SELECT * FROM LIVRO WHERE id_livro=%s AND disponivel=TRUE",
        (int(id_livro),)
    )
    livro = cursor.fetchone()
 
    if not livro:
        print("Livro não encontrado ou não disponível.")
        return
    if livro["id_utilizador"] == usuario["id_utilizador"]:
        print("Não podes pedir a troca do teu próprio livro.")
        return
 
    try:
        cursor.execute(
            "INSERT INTO TROCA (data_troca, id_livro, id_utilizador_origem, id_utilizador_destino) VALUES (%s,%s,%s,%s)",
            (date.today(), livro["id_livro"], usuario["id_utilizador"], livro["id_utilizador"])
        )
        db.commit()
        print("Pedido do livro enviado com sucesso! Estado: pendente.")
    except Exception as e:
        print("Erro ao pedir livro:", e)
 
 
# ─────────────────────────────────────────────
#  5 - VER PEDIDOS RECEBIDOS
# ─────────────────────────────────────────────
def ver_pedidos_recebidos(usuario):
    cursor.execute("""
        SELECT T.id_troca, L.titulo, U.nome AS solicitante, T.data_troca
        FROM TROCA T
        JOIN LIVRO L      ON T.id_livro = L.id_livro
        JOIN UTILIZADOR U ON T.id_utilizador_origem = U.id_utilizador
        WHERE T.id_utilizador_destino=%s AND T.estado_troca='pendente'
    """, (usuario["id_utilizador"],))
    pedidos = cursor.fetchall()
 
    if not pedidos:
        print("Não tens pedidos pendentes.")
        return False
 
    print(f"\n{'ID Troca':<10} {'Livro':<30} {'Solicitante':<25} {'Data'}")
    print("─" * 75)
    for p in pedidos:
        print(f"{p['id_troca']:<10} {p['titulo']:<30} {p['solicitante']:<25} {p['data_troca']}")
    return True
 
 
# ─────────────────────────────────────────────
#  6 - ACEITAR / RECUSAR PEDIDO
# ─────────────────────────────────────────────
def responder_pedido(usuario):
    if not ver_pedidos_recebidos(usuario): return
 
    id_troca = input_ou_voltar("\nID da troca (0 para voltar): ")
    if id_troca is None: return
    if not id_troca.isdigit():
        print("ID inválido!")
        return
 
    cursor.execute(
        "SELECT * FROM TROCA WHERE id_troca=%s AND id_utilizador_destino=%s AND estado_troca='pendente'",
        (int(id_troca), usuario["id_utilizador"])
    )
    troca = cursor.fetchone()
 
    if not troca:
        print("Troca não encontrada ou já respondida.")
        return
 
    resposta = input("Aceitar (a) ou Recusar (r)? ").strip().lower()
    if resposta not in ("a", "r"):
        print("Resposta inválida.")
        return
 
    novo_estado = "aceite" if resposta == "a" else "recusada"
    try:
        cursor.execute(
            "UPDATE TROCA SET estado_troca=%s WHERE id_troca=%s",
            (novo_estado, troca["id_troca"])
        )
        if resposta == "a":
            cursor.execute(
                "UPDATE LIVRO SET disponivel=FALSE WHERE id_livro=%s",
                (troca["id_livro"],)
            )
        db.commit()
        print(f"Pedido {novo_estado} com sucesso!")
    except Exception as e:
        print("Erro ao responder pedido:", e)
 
 
# ─────────────────────────────────────────────
#  7 - HISTORICO DE TROCAS
# ─────────────────────────────────────────────
def historico_trocas(usuario):
    cursor.execute("""
        SELECT T.id_troca, L.titulo, UO.nome AS origem, UD.nome AS destino,
               T.data_troca, T.estado_troca
        FROM TROCA T
        JOIN LIVRO      L  ON T.id_livro = L.id_livro
        JOIN UTILIZADOR UO ON T.id_utilizador_origem  = UO.id_utilizador
        JOIN UTILIZADOR UD ON T.id_utilizador_destino = UD.id_utilizador
        WHERE T.id_utilizador_origem=%s OR T.id_utilizador_destino=%s
        ORDER BY T.data_troca DESC
    """, (usuario["id_utilizador"], usuario["id_utilizador"]))
    trocas = cursor.fetchall()
 
    if not trocas:
        print("Ainda não tens trocas.")
        return
 
    print(f"\n{'ID':<5} {'Livro':<25} {'De':<20} {'Para':<20} {'Data':<12} {'Estado'}")
    print("─" * 90)
    for t in trocas:
        print(f"{t['id_troca']:<5} {t['titulo']:<25} {t['origem']:<20} {t['destino']:<20} {str(t['data_troca']):<12} {t['estado_troca']}")

        #__________Menu Principal__________
def principal():
    while True:
        print("\n1 Registar")
        print("2 Login")
        print("3 Sair")
        op = input("Escolha: ").strip()
        if   op == "1": registar()
        elif op == "2":
            usuario = login()
            if usuario:
                menu_utilizador(usuario)
        elif op == "3": break
        else: print("Opção inválida!")

if __name__ == "__main__":
    principal()