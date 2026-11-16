"""Validação da entrada de dados (validação com while + try/except)."""

from config import ENTIDADES
from dados import buscar_por_id, carregar
from navegacao import entrada


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
