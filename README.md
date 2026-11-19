# GRILLO

**Ou a conta bate, ou não bate!**

Tutor de estudos de matemática da educação básica com IA, mediado pelo professor (Projetos 01, CESAR School, 2026.2).

Este código é o **MVP 0.1** do Grillo: um programa de terminal em Python que cadastra professores, alunos e conteúdos, registra em qual conteúdo cada aluno trava e gera o relatório de dificuldades da turma. Os dados ficam em arquivos CSV, sem servidor, e o programa funciona offline.

---

## Como executar

Requisito: **Python 3.10 ou superior** (o código usa `match`). Não há bibliotecas externas: só `csv` e `os`, que já vêm com o Python.

```bash
cd GRILLO
python main.py
```

A pasta `dados/` fica ao lado do código, então o programa funciona de qualquer diretório de onde for iniciado.

---

## Organização do projeto

```
GRILLO/
├── main.py          Inicialização
├── config.py        Configurações
├── navegacao.py     Navegação
├── dados.py         CSV
├── validacao.py     Validação
├── cadastros.py     CRUD
├── relatorios.py    Análise
└── dados/
    ├── professores.csv
    ├── alunos.csv
    └── conteudos.csv
```

| Arquivo | Responsabilidade | Principais itens |
|---|---|---|
| `main.py` | Ponto de entrada. Inicia o menu e trata `Ctrl+C` e erros inesperados sem derrubar o programa com uma mensagem técnica. | `main()` |
| `config.py` | Concentra as configurações: o caminho da pasta `dados/` e a descrição das três entidades. | `PASTA`, `ENTIDADES` |
| `navegacao.py` | Entrada do usuário, comandos de voltar e os menus do programa. | `VoltarMenu`, `IrMenuPrincipal`, `entrada()`, `menu_principal()`, `menu_crud()` |
| `dados.py` | Leitura e gravação dos CSV. Converte arquivo em lista de dicionários e o contrário. Também calcula o próximo ID e busca por ID. | `carregar()`, `salvar()`, `converter_valor()`, `proximo_id()`, `buscar_por_id()` |
| `validacao.py` | Pede cada dado ao usuário e só aceita valores válidos, repetindo a pergunta enquanto houver erro. | `ler_texto()`, `ler_numero()`, `ler_booleano()`, `ler_referencia()`, `coletar_dados()` |
| `cadastros.py` | As quatro operações do CRUD, usadas pelas três entidades. | `criar()`, `listar()`, `editar()`, `excluir()`, `esta_em_uso()`, `mostrar_registro()` |
| `relatorios.py` | Análise dos dados: relatório de dificuldades da turma e classificação da confiança. | `relatorio_dificuldades()`, `classificar_confianca()` |
| `dados/` | Um arquivo CSV por entidade, já com o cabeçalho. | `professores.csv`, `alunos.csv`, `conteudos.csv` |

### Como os módulos se conectam

```
main.py
  └── navegacao.py ──────────► cadastros.py ──► validacao.py ──► dados.py ──► config.py
        │                           │                │
        │                           └────────────────┴──► dados.py
        └──────────────────────► relatorios.py ──► dados.py
```

- `config.py` não depende de ninguém: é a base.
- `dados.py` só conhece `config.py`.
- `validacao.py` usa `dados.py` (para conferir IDs) e `entrada()` de `navegacao.py`.
- `cadastros.py` usa `dados.py` e `validacao.py`.
- `navegacao.py` chama `cadastros.py` e `relatorios.py`. Essas importações ficam **dentro das funções de menu** para evitar um import circular, já que `validacao.py` também importa `entrada()` de `navegacao.py`.

### Estrutura dos dados

Cada registro é um **dicionário**, e cada entidade é uma **lista de dicionários**, com tipos `str`, `int`, `float` e `bool`. Cada lista é gravada em um arquivo CSV.

| Arquivo | Campos | Observações |
|---|---|---|
| `professores.csv` | `id`, `nome`, `email`, `disciplina`, `ativo` | `ativo` é verdadeiro/falso. |
| `alunos.csv` | `id`, `nome`, `serie`, `turma`, `nota_confianca`, `dificuldade_id` | `serie` de 1 a 3. `nota_confianca` de 1 a 5. `dificuldade_id` aponta para um conteúdo (`0` = nenhum). |
| `conteudos.csv` | `id`, `titulo`, `tipo_dificuldade`, `roteiro`, `resposta_final`, `professor_id` | `roteiro` guarda as perguntas do tutor separadas por `;`. `professor_id` aponta para um professor. |

**Relacionamentos:**
- `alunos.dificuldade_id` → `conteudos.id`
- `conteudos.professor_id` → `professores.id`

---

## Funcionalidades

### Menu principal

```
1 - Professores
2 - Alunos
3 - Conteúdos e questões
4 - Relatório de dificuldades
0 - Sair
```

### CRUD (professores, alunos e conteúdos)

Os três cadastros usam o mesmo código, guiado pela descrição em `ENTIDADES`. Cada um oferece:

1. **Cadastrar:** pede os campos, gera um ID novo (maior ID existente + 1) e salva no CSV.
2. **Listar:** mostra todos os registros.
3. **Buscar por texto:** filtra os registros pelo texto digitado, sem diferenciar maiúsculas de minúsculas, em todos os campos.
4. **Editar:** pede o ID e cada campo. Apertar Enter mantém o valor atual.
5. **Excluir:** pede o ID e uma confirmação antes de apagar.

### Relatório de dificuldades

É o diagnóstico que o professor recebe: para cada conteúdo, mostra **quantos alunos travam nele, em quantidade e em percentual da turma**. Mostra também a **confiança média da turma** (de 1 a 5), classificada como:

| Média | Classificação |
|---|---|
| abaixo de 2,5 | baixa |
| de 2,5 até menos de 4 | média |
| 4 ou mais | alta |

Exemplo de saída:

```
--- Relatório de dificuldades da turma ---
  Regra de sinais: 1 aluno(s) (100.0%)
  Confiança média da turma: 2.5/5 (média)
```

### Navegação

Em qualquer pergunta do programa:

- **`v`**: volta para a seção anterior.
- **`m`**: volta direto ao menu principal.
- **`0`**: sai do menu atual (nos menus de CRUD, volta ao menu principal; no menu principal, encerra o programa).

---

## Regras de validação e integridade

- **Campos de texto** não podem ficar vazios. Na edição, Enter mantém o valor atual.
- **Números** precisam ser válidos e respeitar os limites (`serie` de 1 a 3, `nota_confianca` de 1 a 5). A vírgula decimal é aceita (`2,5`).
- **Campos sim/não** aceitam `s`, `sim`, `n`, `nao` ou `não`.
- **Integridade referencial:** um conteúdo só pode apontar para um professor que existe, e um aluno só pode apontar para um conteúdo que existe (ou `0`, para nenhum).
- **Exclusão protegida:** não é possível excluir um professor que tem conteúdos, nem um conteúdo que algum aluno registrou como dificuldade.
- **Arquivos tolerantes a falhas:** se um CSV não existir, o programa começa com a lista vazia. Linhas corrompidas são ignoradas com um aviso, e erros de disco ao salvar são mostrados sem encerrar o programa.

---

## Princípios do Grillo refletidos no código

- **Dados mínimos por registro:** só são guardados os campos necessários.
- **O professor avalia:** o sistema registra onde o aluno trava e a confiança declarada, mas não dá veredito sobre a compreensão.
- **Funciona offline:** CSV local, sem servidor, o que atende escolas com pouca conectividade.

## Observação sobre `__pycache__`

Depois da primeira execução, o Python cria uma pasta `__pycache__/` com versões compiladas dos módulos. Ela é gerada automaticamente e pode ser apagada a qualquer momento, sem afetar o programa.
