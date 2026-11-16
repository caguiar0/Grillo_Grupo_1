"""Configurações do Grillo: pasta dos dados e descrição das entidades."""

import os

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
