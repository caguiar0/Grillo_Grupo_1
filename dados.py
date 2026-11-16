"""Acesso aos dados: leitura e gravação dos CSV (CSV <-> lista de dicionários)."""

import csv
import os

from config import ENTIDADES, PASTA


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
