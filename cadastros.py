"""CRUD usado pelas 3 entidades: professores, alunos e conteúdos."""

from config import ENTIDADES
from dados import buscar_por_id, carregar, proximo_id, salvar
from validacao import coletar_dados, ler_booleano, ler_numero


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
