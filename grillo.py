
import csv
import os

# CONFIGURAÇÃO (variáveis globais: escopo de módulo, visíveis em todas as funções)

# A pasta "dados" fica ao lado deste arquivo, não importa de onde o programa é executado.
PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")

# Descrição de cada entidade (um CRUD para cada uma):
#   campos     -> nome do campo e o tipo que ele deve ter
#   rotulos    -> texto mostrado ao usuário
#   limites    -> valores mínimo e máximo permitidos (números)
#   refs       -> campo que aponta para outra entidade (chave estrangeira);
#                 o 2º valor diz se o 0 é aceito como "nenhum"
#   dependentes-> quem usa esta entidade (impede excluir algo que está em uso)
ENTIDADES = {
    "professores": {
        "titulo": "Professor",
        "arquivo": "professores.csv",
        "campos": {"id": int, "nome": str, "email": str, "disciplina": str, "ativo": bool},
        "rotulos": {
            "nome": "Nome",
            "email": "E-mail",
            "disciplina": "Disciplina",
            "ativo": "Ativo? (s/n)",
        },
        "limites": {},
        "refs": {},
        "dependentes": [("conteudos", "professor_id")],
    },
    "alunos": {
        "titulo": "Aluno",
        "arquivo": "alunos.csv",
        "campos": {
            "id": int,
            "nome": str,
            "serie": int,
            "turma": str,
            "nota_confianca": float,
            "dificuldade_id": int,
        },
        "rotulos": {
            "nome": "Nome",
            "serie": "Série do ensino médio (1 a 3)",
            "turma": "Turma (ex.: A)",
            "nota_confianca": "Confiança em matemática (1 a 5)",
            "dificuldade_id": "ID do conteúdo em que mais trava (0 = nenhum)",
        },
        "limites": {"serie": (1, 3), "nota_confianca": (1, 5)},
        "refs": {"dificuldade_id": ("conteudos", True)},
        "dependentes": [],
    },
    "conteudos": {
        "titulo": "Conteúdo/Questão",
        "arquivo": "conteudos.csv",
        "campos": {
            "id": int,
            "titulo": str,
            "tipo_dificuldade": str,
            "roteiro": str,
            "resposta_final": str,
            "professor_id": int,
        },
        "rotulos": {
            "titulo": "Título do conteúdo (ex.: Regra de sinais)",
            "tipo_dificuldade": "Tipo de dificuldade (ex.: álgebra)",
            "roteiro": "Perguntas do tutor, separadas por ';'",
            "resposta_final": "Resposta final (só o professor vê)",
            "professor_id": "ID do professor responsável",
        },
        "limites": {},
        "refs": {"professor_id": ("professores", False)},
        "dependentes": [("alunos", "dificuldade_id")],
    },
}


# NAVEGAÇÃO (voltar / menu principal em qualquer etapa)

class VoltarMenu(Exception):
    """Sinal lançado quando o usuário digita 'v': volta para a seção anterior."""


class IrMenuPrincipal(Exception):
    """Sinal lançado quando o usuário digita 'm': volta direto ao menu principal."""


def entrada(mensagem):
    texto = input(mensagem).strip()
    if texto.lower() == "v":
        raise VoltarMenu()
    if texto.lower() == "m":
        raise IrMenuPrincipal()
    return texto


# ARQUIVOS (CSV <-> lista de dicionários)

def converter_valor(texto, tipo):
    """Converte um texto lido do CSV para o tipo certo (int, float, bool ou str).

    Parâmetros: texto (str do arquivo) e tipo (int, float, bool ou str).
    Retorno: o valor já convertido. Pode lançar ValueError se o texto for inválido.
    """
    if tipo is bool:
        return texto == "True"
    if tipo is int:
        return int(texto)
    if tipo is float:
        return float(texto)
    return texto


def carregar(entidade):
    """Lê o arquivo CSV da entidade e devolve uma LISTA de dicionários.

    Se o arquivo ainda não existe (primeira execução), devolve uma lista vazia.
    Linhas corrompidas são ignoradas, em vez de derrubar o programa.
    """
    config = ENTIDADES[entidade]
    caminho = os.path.join(PASTA, config["arquivo"])
    registros = []  # lista local: só existe dentro desta função (escopo local)

    try:
        with open(caminho, newline="", encoding="utf-8") as arquivo:
            leitor = csv.DictReader(arquivo)
            for linha in leitor:
                try:
                    registro = {
                        campo: converter_valor(linha[campo], tipo)
                        for campo, tipo in config["campos"].items()
                    }
                    registros.append(registro)
                except (ValueError, KeyError, TypeError):
                    print(f"  [aviso] linha inválida ignorada em {config['arquivo']}")
    except FileNotFoundError:
        pass  # arquivo ainda não existe: começa vazio
    return registros


def salvar(entidade, registros):
    """Grava a lista de dicionários no arquivo CSV da entidade (sobrescreve o arquivo).

    Cria a pasta "dados" se ela não existir. Em caso de erro de disco,
    avisa o usuário em vez de encerrar o programa.
    """
    config = ENTIDADES[entidade]
    try:
        os.makedirs(PASTA, exist_ok=True)
        caminho = os.path.join(PASTA, config["arquivo"])
        with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
            escritor = csv.DictWriter(arquivo, fieldnames=list(config["campos"]))
            escritor.writeheader()
            escritor.writerows(registros)
    except OSError as erro:
        print(f"  [erro] não foi possível salvar {config['arquivo']}: {erro}")


# ENTRADA DE DADOS (validação com while + try/except)

def ler_texto(mensagem, atual=None):
    """Pede um texto não vazio ao usuário.

    Se 'atual' for informado (modo edição), apertar Enter mantém o valor atual.
    Retorno: o texto digitado (str).
    """
    while True:
        sufixo = f" [{atual}]" if atual is not None else ""
        texto = entrada(f"  {mensagem}{sufixo}: ").strip()
        if texto:
            return texto
        if atual is not None:
            return str(atual)
        print("  Campo obrigatório.")


def ler_numero(mensagem, tipo, minimo=None, maximo=None, atual=None):
    """Pede um número (int ou float) e repete enquanto o valor for inválido.

    Parâmetros: mensagem, tipo (int ou float), minimo/maximo opcionais e
    atual (valor mantido se o usuário apertar Enter na edição).
    Retorno: o número já convertido.
    """
    while True:
        sufixo = f" [{atual}]" if atual is not None else ""
        texto = entrada(f"  {mensagem}{sufixo}: ").strip().replace(",", ".")
        if texto == "" and atual is not None:
            return atual
        try:
            numero = tipo(texto)
        except ValueError:
            print("  Digite um número válido.")
            continue
        if minimo is not None and numero < minimo:
            print(f"  O valor mínimo é {minimo}.")
        elif maximo is not None and numero > maximo:
            print(f"  O valor máximo é {maximo}.")
        else:
            return numero


def ler_booleano(mensagem, atual=None):
    """Pede 's' ou 'n' e devolve True ou False."""
    while True:
        sufixo = f" [{'s' if atual else 'n'}]" if atual is not None else ""
        texto = entrada(f"  {mensagem}{sufixo}: ").strip().lower()
        if texto == "" and atual is not None:
            return atual
        if texto in ("s", "sim"):
            return True
        elif texto in ("n", "nao", "não"):
            return False
        print("  Responda com 's' ou 'n'.")


def ler_referencia(mensagem, entidade_alvo, aceita_zero, atual=None):
    """Pede um ID e confirma que ele existe na outra entidade (integridade referencial).

    aceita_zero=True permite digitar 0 para dizer "nenhum".
    """
    while True:
        valor = ler_numero(mensagem, int, minimo=0, atual=atual)
        if valor == 0 and aceita_zero:
            return 0
        if buscar_por_id(carregar(entidade_alvo), valor) is not None:
            return valor
        print(f"  ID {valor} não encontrado em '{entidade_alvo}'. Cadastre-o antes.")


def coletar_dados(entidade, atual=None):
    """Pergunta ao usuário cada campo da entidade e devolve um dicionário novo.

    Serve tanto para CRIAR (atual=None) quanto para EDITAR (atual=registro existente,
    onde Enter mantém o valor antigo). O 'id' nunca é perguntado.
    """
    config = ENTIDADES[entidade]
    dados = {}
    for campo, tipo in config["campos"].items():  # for percorre campo a campo
        if campo == "id":
            continue
        rotulo = config["rotulos"][campo]
        valor_atual = atual[campo] if atual else None

        if campo in config["refs"]:
            alvo, aceita_zero = config["refs"][campo]
            dados[campo] = ler_referencia(rotulo, alvo, aceita_zero, valor_atual)
        elif tipo is bool:
            dados[campo] = ler_booleano(rotulo, valor_atual)
        elif tipo in (int, float):
            minimo, maximo = config["limites"].get(campo, (None, None))
            dados[campo] = ler_numero(rotulo, tipo, minimo, maximo, valor_atual)
        else:
            dados[campo] = ler_texto(rotulo, valor_atual)
    return dados


# CRUD (usado pelas 3 entidades: professores, alunos e conteúdos)

def proximo_id(registros):
    """Calcula o próximo ID livre: maior ID existente + 1 (ou 1 se a lista está vazia)."""
    maior = 0
    for registro in registros:
        if registro["id"] > maior:
            maior = registro["id"]
    return maior + 1


def buscar_por_id(registros, id_procurado):
    """Procura na lista o registro com o ID informado.

    Retorno: o dicionário encontrado ou None se não existir.
    """
    for registro in registros:
        if registro["id"] == id_procurado:
            return registro
    return None


def criar(entidade):
    """CREATE: pede os dados, gera um ID novo, adiciona na lista e salva no CSV."""
    registros = carregar(entidade)
    print(f"\n--- Novo {ENTIDADES[entidade]['titulo']} ---")
    novo = {"id": proximo_id(registros)}
    novo.update(coletar_dados(entidade))
    registros.append(novo)  # operação de lista: adicionar no final
    salvar(entidade, registros)
    print(f"  Cadastrado com ID {novo['id']}.")


def mostrar_registro(entidade, registro):
    """Imprime um registro em uma linha, com 'campo: valor' separados por ' | '."""
    partes = []
    for campo in ENTIDADES[entidade]["campos"]:
        valor = registro[campo]
        if isinstance(valor, bool):
            valor = "sim" if valor else "não"
        partes.append(f"{campo}: {valor}")
    print("  " + " | ".join(partes))


def listar(entidade, filtro=""):
    """READ: mostra todos os registros (ou só os que contêm o texto 'filtro').

    A busca ignora maiúsculas/minúsculas e procura em todos os campos.
    """
    registros = carregar(entidade)
    print(f"\n--- {ENTIDADES[entidade]['titulo']}s ---")
    encontrados = 0
    for registro in registros:
        texto = " ".join(str(v) for v in registro.values()).lower()
        if filtro.lower() in texto:
            mostrar_registro(entidade, registro)
            encontrados += 1
    if encontrados == 0:
        print("  Nenhum registro encontrado.")


def editar(entidade):
    """UPDATE: pede um ID, mostra o registro e permite alterar cada campo."""
    registros = carregar(entidade)
    id_alvo = ler_numero("ID para editar", int, minimo=1)
    registro = buscar_por_id(registros, id_alvo)
    if registro is None:
        print("  ID não encontrado.")
        return
    print("  (Enter mantém o valor atual)")
    registro.update(coletar_dados(entidade, atual=registro))
    salvar(entidade, registros)
    print("  Atualizado.")


def esta_em_uso(entidade, id_alvo):
    """Verifica se outro cadastro depende deste ID (ex.: conteúdo usado por um aluno).

    Retorno: True se estiver em uso (e então NÃO pode ser excluído), senão False.
    """
    for outra_entidade, campo in ENTIDADES[entidade]["dependentes"]:
        for registro in carregar(outra_entidade):
            if registro[campo] == id_alvo:
                return True
    return False


def excluir(entidade):
    """DELETE: pede um ID, confirma e remove da lista, salvando o CSV."""
    registros = carregar(entidade)
    id_alvo = ler_numero("ID para excluir", int, minimo=1)
    registro = buscar_por_id(registros, id_alvo)
    if registro is None:
        print("  ID não encontrado.")
    elif esta_em_uso(entidade, id_alvo):
        print("  Não é possível excluir: este cadastro está em uso por outro registro.")
    elif ler_booleano("Confirmar exclusão?"):
        registros.remove(registro)  # operação de lista: remover item
        salvar(entidade, registros)
        print("  Excluído.")
    else:
        print("  Exclusão cancelada.")


def menu_crud(entidade):
    """Menu de um CRUD (Criar, Listar/Buscar, Editar, Excluir) para a entidade escolhida.

    Usa while para repetir até o usuário voltar, e match para escolher a ação.
    """
    titulo = ENTIDADES[entidade]["titulo"]
    while True:
        print(f"\n===== CRUD de {titulo} =====")
        print("1 - Cadastrar")
        print("2 - Listar")
        print("3 - Buscar por texto")
        print("4 - Editar")
        print("5 - Excluir")
        print("0 ou v - Voltar ao menu principal")
        print("m - Menu principal  (v e m funcionam em qualquer pergunta)")
        try:
            opcao = entrada("Escolha: ")
        except VoltarMenu:
            return  # 'v' no menu do CRUD: volta para o menu principal

        # IrMenuPrincipal ('m') não é tratada aqui: sobe até o menu_principal.
        try:
            match opcao:
                case "1":
                    criar(entidade)
                case "2":
                    listar(entidade)
                case "3":
                    listar(entidade, entrada("  Texto a buscar: "))
                case "4":
                    editar(entidade)
                case "5":
                    excluir(entidade)
                case "0":
                    return  # sai da função e volta ao menu principal
                case _:
                    print("  Opção inválida.")
        except VoltarMenu:
            print("  Operação cancelada. Voltando ao menu anterior...")


# RELATÓRIO (funcionalidade 5 do Grillo: dificuldades da turma)

def classificar_confianca(nota):
    """Transforma a nota de confiança (1 a 5) em um texto, usando if/elif/else.

    Retorno: 'baixa', 'média' ou 'alta'.
    """
    if nota < 2.5:
        return "baixa"
    elif nota < 4:
        return "média"
    else:
        return "alta"


def relatorio_dificuldades():
    """Mostra, por conteúdo, quantos alunos travam nele (quantidade e percentual).

    É o diagnóstico que o professor recebe. Também mostra a confiança média
    da turma, classificada por classificar_confianca().
    """
    alunos = carregar("alunos")
    conteudos = carregar("conteudos")
    print("\n--- Relatório de dificuldades da turma ---")
    if not alunos:
        print("  Nenhum aluno cadastrado.")
        return

    contagem = {}  # dicionário: id do conteúdo -> quantidade de alunos travados
    soma_confianca = 0.0
    for aluno in alunos:
        soma_confianca += aluno["nota_confianca"]
        if aluno["dificuldade_id"] != 0:
            contagem[aluno["dificuldade_id"]] = contagem.get(aluno["dificuldade_id"], 0) + 1

    total = len(alunos)
    if not contagem:
        print("  Nenhum aluno registrou dificuldade.")
    for conteudo in conteudos:
        quantidade = contagem.get(conteudo["id"], 0)
        if quantidade > 0:
            percentual = quantidade / total * 100
            print(f"  {conteudo['titulo']}: {quantidade} aluno(s) ({percentual:.1f}%)")

    media = soma_confianca / total
    print(f"  Confiança média da turma: {media:.1f}/5 ({classificar_confianca(media)})")


# PROGRAMA PRINCIPAL

def menu_principal():
    """Menu inicial do Grillo: escolhe o CRUD ou o relatório. Roda até o usuário sair."""
    while True:
        print("\n=============== GRILLO ===============")
        print("Ou a conta bate, ou não bate!")
        print("1 - Professores")
        print("2 - Alunos")
        print("3 - Conteúdos e questões")
        print("4 - Relatório de dificuldades")
        print("0 - Sair")
        try:
            opcao = entrada("Escolha: ")
        except (VoltarMenu, IrMenuPrincipal):
            print("  Você já está no menu principal.")
            continue

        try:
            match opcao:
                case "1":
                    menu_crud("professores")
                case "2":
                    menu_crud("alunos")
                case "3":
                    menu_crud("conteudos")
                case "4":
                    relatorio_dificuldades()
                case "0":
                    print("Até logo!")
                    return
                case _:
                    print("  Opção inválida.")
        except (VoltarMenu, IrMenuPrincipal):
            print("  Voltando ao menu principal...")


def main():
    """Ponto de entrada: inicia o menu e trata Ctrl+C e erros inesperados."""
    try:
        menu_principal()
    except (KeyboardInterrupt, EOFError):
        print("\nEncerrado pelo usuário.")
    except Exception as erro:
        print(f"\nErro inesperado: {erro}")


# Só executa main() quando o arquivo é rodado diretamente (não quando importado).
if __name__ == "__main__":
    main()
