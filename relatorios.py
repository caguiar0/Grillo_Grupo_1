"""Análise: relatório de dificuldades da turma (funcionalidade 5 do Grillo)."""

from dados import carregar


def classificar_confianca(nota):
    """Transforma a nota de confiança (1 a 5) em um texto, usando if/elif/else.

    Retorno: 'baixa', 'média' ou 'alta'.
    ValueError se a nota estiver fora do intervalo de 0 a 5.
    """
    if nota < 0 or nota > 5:
        raise ValueError("A nota de confiança deve estar entre 0 e 5.")
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
