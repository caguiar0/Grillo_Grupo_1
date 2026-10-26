# Documentação Didática — Grillo MVP 0.1

> **Ou a conta bate, ou não bate!**
> Tutor de matemática com IA, mediado pelo professor — Projetos 01 · CESAR School · 2026.2

Este documento explica, de forma didática, como o arquivo `grillo.py` funciona: a arquitetura, os dados, cada função e os conceitos de Python da disciplina que foram aplicados. Pode ser lido do início ao fim ou consultado por seção.

---

## 1. Visão geral

O `grillo.py` é um programa de terminal que implementa a base de dados do MVP do Grillo por meio de **três CRUDs** (Create, Read, Update, Delete) e um **relatório de dificuldades**:

| Módulo | O que gerencia | Funcionalidade do projeto |
|---|---|---|
| CRUD de **Professores** | Cadastro de quem cura o conteúdo | Base do professor |
| CRUD de **Alunos** | Cadastro de quem estuda e onde trava | Registro do aluno |
| CRUD de **Conteúdos/Questões** | Conteúdos e roteiros de perguntas do tutor | Funcionalidades 1 e 2 |
| **Relatório de dificuldades** | Quantos alunos travam em cada conteúdo | Funcionalidade 5 |

**O que o código não faz (ainda):** não chama nenhuma IA. O campo `roteiro` guarda as perguntas que o tutor usaria, mas a conversa com o modelo de IA (funcionalidade 3) fica para uma sprint futura.

### Requisitos e execução

- **Python 3.10 ou superior** (a instrução `match` não existe em versões anteriores).
- **Nenhuma biblioteca externa**: usa apenas `csv` e `os`, da biblioteca padrão.
- No VS Code: abra `grillo.py` e clique em **Run Python File**, ou no terminal:

```bash
python grillo.py
```

Na primeira execução, a pasta `dados/` é criada automaticamente ao lado do arquivo.

---

## 2. Arquitetura

O código é organizado em camadas, de baixo para cima. Cada camada só usa as de baixo:

```
┌──────────────────────────────────────────────┐
│ 5. PROGRAMA PRINCIPAL  main, menu_principal  │
├──────────────────────────────────────────────┤
│ 4. MENUS E RELATÓRIO   menu_crud, relatorio  │
├──────────────────────────────────────────────┤
│ 3. CRUD GENÉRICO       criar, listar, editar,│
│                        excluir, buscar...    │
├──────────────────────────────────────────────┤
│ 2. ENTRADA DE DADOS    entrada, ler_*,       │
│                        coletar_dados         │
├──────────────────────────────────────────────┤
│ 1. ARQUIVOS E CONFIG   ENTIDADES, carregar,  │
│                        salvar                │
└──────────────────────────────────────────────┘
          dados/*.csv  (persistência)
```

### A decisão de design mais importante: CRUD genérico

Em vez de escrever 12 funções (4 operações × 3 entidades), o código tem **4 funções** que servem às três entidades. O que muda de uma entidade para outra fica descrito em um dicionário de configuração, o `ENTIDADES`:

```python
ENTIDADES = {
    "professores": {"titulo": ..., "arquivo": ..., "campos": {...}, ...},
    "alunos":      {...},
    "conteudos":   {...},
}
```

Para criar um quarto CRUD (por exemplo, "turmas"), basta adicionar uma entrada nesse dicionário e uma opção no menu. Nenhuma função de CRUD precisa ser reescrita. Esse é o princípio **DRY** (*Don't Repeat Yourself*).

Cada entidade tem estas chaves de configuração:

| Chave | Tipo | Função |
|---|---|---|
| `titulo` | `str` | Nome exibido nos menus |
| `arquivo` | `str` | Nome do CSV em `dados/` |
| `campos` | `dict` | Nome do campo → tipo (`int`, `str`, `float`, `bool`) |
| `rotulos` | `dict` | Campo → texto da pergunta feita ao usuário |
| `limites` | `dict` | Campo → `(mínimo, máximo)` aceitos |
| `refs` | `dict` | Campo → `(entidade_alvo, aceita_zero)`; é a chave estrangeira |
| `dependentes` | `list` | Quem usa esta entidade; impede exclusões que quebrariam referências |

---

## 3. Modelo de dados

### 3.1 Estrutura em memória

- Cada **registro** é um **dicionário**: `{"id": 1, "nome": "Ana", ...}`
- Cada **coleção** é uma **lista de dicionários**: `[{...}, {...}]`
- Tipos usados: `str`, `int`, `float` e `bool`

### 3.2 Entidades

**Professor** (`professores.csv`)

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | int | Identificador, gerado automaticamente |
| `nome` | str | Nome do professor |
| `email` | str | E-mail |
| `disciplina` | str | Disciplina que leciona |
| `ativo` | bool | Se está ativo no sistema |

**Aluno** (`alunos.csv`)

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | int | Identificador |
| `nome` | str | Nome do aluno |
| `serie` | int | Série do ensino médio (1 a 3) |
| `turma` | str | Turma (ex.: A) |
| `nota_confianca` | float | Autoavaliação de confiança em matemática (1 a 5) |
| `dificuldade_id` | int | ID do conteúdo em que mais trava (`0` = nenhum) |

**Conteúdo/Questão** (`conteudos.csv`)

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | int | Identificador |
| `titulo` | str | Ex.: "Regra de sinais" |
| `tipo_dificuldade` | str | Categoria da dificuldade |
| `roteiro` | str | Perguntas do tutor, separadas por `;` |
| `resposta_final` | str | Resposta final, visível só ao professor |
| `professor_id` | int | Professor responsável (chave estrangeira) |

### 3.3 Relacionamentos

```
Professor 1 ──────< Conteúdo >────── 0..N Aluno
          (professor_id)        (dificuldade_id)
```

- Um professor pode ter vários conteúdos.
- Um aluno aponta para **um** conteúdo em que trava (ou `0`, nenhum).
- A **integridade referencial** é garantida em duas pontas: não se cadastra um conteúdo com professor inexistente, e não se exclui um professor ou conteúdo que esteja em uso.

### 3.4 Persistência em CSV

Cada lista é gravada em um arquivo CSV. Exemplo de `professores.csv`:

```csv
id,nome,email,disciplina,ativo
1,Ana,ana@escola.com,Matemática,True
```

Por que CSV no MVP? Não exige servidor, funciona offline e atende escolas com pouca conectividade. O caminho de evolução natural é CSV → SQLite → PostgreSQL.

---

## 4. Referência das funções

### 4.1 Navegação

#### `class VoltarMenu(Exception)` e `class IrMenuPrincipal(Exception)`
Exceções **criadas pelo programa**, sem corpo (só `docstring`). Não representam erros. Funcionam como **sinais**: quando lançadas, "sobem" pela pilha de chamadas até encontrar um `try/except` que saiba o que fazer.

#### `entrada(mensagem)`
Substitui o `input()` em todo o programa.

- **Parâmetro:** `mensagem` (texto da pergunta)
- **Retorno:** texto digitado, sem espaços nas pontas
- **Comportamento:** se o usuário digitar `v`, lança `VoltarMenu`; se digitar `m`, lança `IrMenuPrincipal`

Como todas as perguntas passam por essa função, a navegação funciona **em qualquer etapa** sem repetir código nas demais funções.

### 4.2 Arquivos

#### `converter_valor(texto, tipo)`
Todo valor lido de um CSV é texto. Esta função o converte para o tipo correto.

- `bool`: `texto == "True"` (o CSV guarda `True` ou `False` como texto)
- `int` e `float`: usa `int(texto)` e `float(texto)`; podem lançar `ValueError`
- `str`: devolve o texto como está

#### `carregar(entidade)`
Lê o CSV e devolve uma **lista de dicionários**.

- Usa `with open(...)`, que fecha o arquivo automaticamente, e `csv.DictReader`, que entrega cada linha como dicionário
- `FileNotFoundError` → arquivo ainda não existe, retorna lista vazia (primeira execução)
- `ValueError`, `KeyError`, `TypeError` → linha corrompida: avisa e **ignora a linha**, sem derrubar o programa

#### `salvar(entidade, registros)`
Grava a lista inteira no CSV (**sobrescreve** o arquivo).

- `os.makedirs(PASTA, exist_ok=True)` cria a pasta se necessário
- `csv.DictWriter` escreve o cabeçalho e as linhas; o módulo `csv` já cuida de vírgulas e aspas dentro dos textos
- `OSError` (disco cheio, sem permissão) é tratado com mensagem, sem encerrar o programa

### 4.3 Entrada de dados

Todas seguem o mesmo padrão: **`while True` + validação + `return` só quando o valor é válido**. O usuário fica preso na pergunta até responder corretamente (ou digitar `v`/`m`).

#### `ler_texto(mensagem, atual=None)`
Exige texto não vazio. Em modo edição (`atual` informado), apertar Enter mantém o valor atual.

#### `ler_numero(mensagem, tipo, minimo=None, maximo=None, atual=None)`
Lê `int` ou `float`.

- Aceita vírgula decimal (`4,5` vira `4.5`)
- `try/except ValueError` captura letras e símbolos
- Compara com `minimo` e `maximo` quando informados
- Recebe o **tipo como parâmetro** (`int` ou `float`) e o usa como função: `tipo(texto)`

#### `ler_booleano(mensagem, atual=None)`
Aceita `s`/`sim` (→ `True`) e `n`/`nao`/`não` (→ `False`).

#### `ler_referencia(mensagem, entidade_alvo, aceita_zero, atual=None)`
Pede um ID e confere se ele existe na entidade apontada. Com `aceita_zero=True`, o `0` significa "nenhum" (usado em `dificuldade_id`).

#### `coletar_dados(entidade, atual=None)`
A função central de entrada. Percorre com `for` os campos da entidade e escolhe como perguntar cada um, conforme o tipo e a configuração:

```
campo é "id"?            → pula (gerado automaticamente)
campo está em refs?      → ler_referencia
tipo é bool?             → ler_booleano
tipo é int ou float?     → ler_numero (com limites)
senão                    → ler_texto
```

Serve para **criar** (`atual=None`) e para **editar** (`atual=registro`). Devolve um dicionário novo com os dados digitados.

### 4.4 CRUD genérico

| Função | Operação | Resumo |
|---|---|---|
| `criar(entidade)` | **C**reate | Carrega a lista, gera ID, coleta dados, `append` e salva |
| `listar(entidade, filtro="")` | **R**ead | Percorre a lista e imprime; com `filtro`, mostra só os que contêm o texto |
| `editar(entidade)` | **U**pdate | Busca por ID e atualiza com `registro.update(...)` |
| `excluir(entidade)` | **D**elete | Confere uso, pede confirmação e usa `registros.remove(...)` |

#### Funções de apoio

- **`proximo_id(registros)`**: percorre a lista guardando o maior ID; retorna `maior + 1`. Em lista vazia, retorna `1`. *Observação:* se o último registro for excluído, seu ID será reaproveitado.
- **`buscar_por_id(registros, id_procurado)`**: percorre a lista e retorna o dicionário encontrado, ou `None`. É a **busca linear** clássica.
- **`mostrar_registro(entidade, registro)`**: monta uma linha `campo: valor | campo: valor`, exibindo `bool` como "sim/não".
- **`esta_em_uso(entidade, id_alvo)`**: consulta `dependentes` e verifica se algum registro de outra entidade aponta para este ID. Retorna `True` ou `False`.

#### Detalhe da busca em `listar`
A busca junta todos os valores do registro em um único texto em minúsculas e verifica se o filtro está contido nele:

```python
texto = " ".join(str(v) for v in registro.values()).lower()
if filtro.lower() in texto: ...
```

Com `filtro=""`, a condição é sempre verdadeira, então todos os registros aparecem. Isso permite usar a mesma função para listar e buscar.

### 4.5 Menus e relatório

#### `menu_crud(entidade)`
Menu com cinco ações. Dois blocos `try/except` separados têm papéis diferentes:

1. O primeiro envolve **só a leitura da opção**: `VoltarMenu` ali significa "sair do CRUD" (`return`).
2. O segundo envolve o **`match` da ação**: `VoltarMenu` ali significa "cancelar a operação e voltar ao menu do CRUD".

`IrMenuPrincipal` **não é capturada** nesta função de propósito: ela sobe até o `menu_principal`.

#### `classificar_confianca(nota)`
Exemplo direto de `if/elif/else`:

| Nota | Resultado |
|---|---|
| menor que 2,5 | `"baixa"` |
| de 2,5 até menor que 4 | `"média"` |
| 4 ou mais | `"alta"` |

#### `relatorio_dificuldades()`
Transforma registros em informação para o professor:

1. Carrega alunos e conteúdos
2. Com `for`, conta quantos alunos travam em cada conteúdo, usando um **dicionário contador** (`contagem[id] = contagem.get(id, 0) + 1`) e somando as notas de confiança
3. Para cada conteúdo com ao menos 1 aluno, mostra **quantidade** e **percentual** (`quantidade / total * 100`)
4. Mostra a confiança média da turma e sua classificação

Exemplo de saída:

```
--- Relatório de dificuldades da turma ---
  Regra de sinais: 3 aluno(s) (60.0%)
  Frações: 1 aluno(s) (20.0%)
  Confiança média da turma: 3.2/5 (média)
```

### 4.6 Programa principal

#### `menu_principal()`
Menu raiz. Se o usuário digita `v` ou `m` aqui, apenas é avisado de que já está no menu principal. Os blocos `try/except` capturam os dois sinais de navegação vindos dos menus internos.

#### `main()`
Ponto de entrada. Chama `menu_principal()` dentro de um `try` que trata `Ctrl+C` (`KeyboardInterrupt`), fim de entrada (`EOFError`) e qualquer erro inesperado (`Exception`), encerrando com mensagem amigável.

#### `if __name__ == "__main__":`
Garante que `main()` só execute quando o arquivo é rodado diretamente, e não quando importado por outro arquivo (útil para testes).

---

## 5. Fluxo de navegação

```
                    MENU PRINCIPAL
         ┌──────────┬─────┴─────┬──────────────┐
    Professores   Alunos    Conteúdos      Relatório
         └──────────┴─────┬─────┘
                       MENU CRUD
     Cadastrar · Listar · Buscar · Editar · Excluir
                          │
              perguntas campo a campo
```

| Onde o usuário está | Digita `v` | Digita `m` |
|---|---|---|
| Pergunta de um cadastro/edição/busca | Cancela e volta ao menu do CRUD | Vai ao menu principal |
| Menu de um CRUD | Volta ao menu principal | Vai ao menu principal |
| Menu principal | Aviso, permanece | Aviso, permanece |

### Como o mecanismo funciona (exceções como controle de fluxo)

```
entrada() lança VoltarMenu
    └─ ler_texto / ler_numero ... (não tratam; deixam passar)
        └─ coletar_dados → criar
            └─ menu_crud: except VoltarMenu → "Operação cancelada"
```

Quando uma exceção é lançada, o Python **desfaz a pilha de chamadas** até achar um `except` compatível. Por isso as funções intermediárias não precisam saber nada sobre navegação.

---

## 6. Mapa dos conteúdos da disciplina

| Conteúdo | Onde aparece no código |
|---|---|
| **Condicionais** `if/elif/else` | `classificar_confianca`, `converter_valor`, `coletar_dados`, `ler_numero` |
| **Condicional `match`** | `menu_crud` e `menu_principal` |
| **Laço `for`** | `carregar`, `coletar_dados`, `listar`, `buscar_por_id`, `relatorio_dificuldades` |
| **Laço `while`** | `ler_texto`, `ler_numero`, `ler_booleano`, `ler_referencia`, menus |
| **Listas** (criar, percorrer, operar) | `carregar` (cria), `criar` (`append`), `excluir` (`remove`), `len()` no relatório |
| **Funções**: definição e uso | Todo o código |
| **Parâmetros** (posicionais, padrão) | `listar(entidade, filtro="")`, `ler_texto(mensagem, atual=None)` |
| **Retorno** | `buscar_por_id`, `proximo_id`, `carregar`, `classificar_confianca` |
| **Escopo** | Global: `PASTA`, `ENTIDADES`. Local: `registros`, `contagem`, `soma_confianca` |
| **Arquivos** | `carregar`, `salvar` (módulo `csv`, `with open`) |
| **Exceções** | `try/except` em `carregar`, `salvar`, `ler_numero`, menus, `main`; exceções próprias |
| **Versionamento** | Comandos Git ao final do `grillo.py` |
| **Coleções** (dicionários) | `ENTIDADES`, cada registro, `contagem` no relatório |

---

## 7. Conceitos técnicos em destaque

### 7.1 Escopo
Variáveis criadas **fora** de funções (`PASTA`, `ENTIDADES`) são **globais**: qualquer função as lê. Variáveis criadas **dentro** de uma função (`registros`, `contagem`) são **locais**: existem só durante a execução dela. Veja que `carregar` cria sua própria lista `registros`, sem relação com a lista homônima de `criar`.

### 7.2 Funções como dados
`ler_numero(..., tipo, ...)` recebe `int` ou `float` como argumento e o chama: `tipo(texto)`. Em `ENTIDADES`, os tipos também estão guardados como valores do dicionário. Em Python, tipos e funções são objetos comuns que podem ser passados e armazenados.

### 7.3 Tratamento de exceções: quando usar
| Situação | Exceção tratada | Resposta do programa |
|---|---|---|
| Arquivo inexistente | `FileNotFoundError` | Começa com lista vazia |
| Linha de CSV malformada | `ValueError`, `KeyError`, `TypeError` | Ignora a linha e avisa |
| Falha ao gravar | `OSError` | Mensagem, sem travar |
| Usuário digita letra num número | `ValueError` | Pede de novo |
| `Ctrl+C` | `KeyboardInterrupt` | Encerra com mensagem |

A regra aplicada: **capture a exceção específica, no ponto onde dá para responder de forma útil**.

### 7.4 Compreensões (*comprehensions*)
Duas linhas usam essa sintaxe compacta:

```python
registro = {campo: converter_valor(linha[campo], tipo)
            for campo, tipo in config["campos"].items()}
```
Constrói um dicionário percorrendo os campos configurados.

```python
" ".join(str(v) for v in registro.values())
```
Junta todos os valores do registro em um único texto.

### 7.5 Validação defensiva
O programa nunca confia na entrada do usuário: números são convertidos dentro de `try`, limites são conferidos, IDs referenciados são verificados e exclusões pedem confirmação.

---

## 8. Exemplo de uso (passo a passo)

1. Abra o programa e escolha **1 – Professores → 1 – Cadastrar**. Cadastre "Ana".
2. Volte (`v`) e escolha **3 – Conteúdos → 1 – Cadastrar**: título "Regra de sinais", professor ID `1`.
3. Volte ao menu principal (`m`) e escolha **2 – Alunos → 1 – Cadastrar**: informe `dificuldade_id = 1`.
4. No menu principal, escolha **4 – Relatório** e veja o percentual de alunos travados em "Regra de sinais".
5. Tente excluir o professor `1`: o programa recusa, pois há um conteúdo vinculado a ele.

---

## 9. Limitações conhecidas

- **Sem IA:** o tutor socrático (funcionalidade 3) ainda não está integrado.
- **Leitura repetida do disco:** `carregar` lê o CSV a cada operação. Simples e seguro para o MVP, mas ineficiente em grandes volumes.
- **Sem acesso simultâneo:** dois usuários gravando ao mesmo tempo podem sobrescrever dados.
- **Sem autenticação:** qualquer pessoa com acesso ao terminal usa qualquer CRUD.
- **Reaproveitamento de ID:** excluir o último registro libera seu ID.
- **Comandos reservados:** `v` e `m` não podem ser usados como resposta de texto.
- **Roteiro como texto único:** as perguntas ficam em um campo separado por `;`, sem estrutura própria.

---

## 10. Evolução sugerida

| Etapa | Melhoria |
|---|---|
| Curto prazo | Separar em módulos (`dados.py`, `menus.py`, `relatorios.py`); relatório com **Pandas** |
| Médio prazo | Interface **Streamlit**; entidade de **atendimento** e de **verificação da resposta da IA** |
| Longo prazo | Integração com IA; **SQLite/PostgreSQL**; login por papéis; adequação à **LGPD** |

---

## 11. Exercícios propostos

1. **(if/elif/else)** Altere `classificar_confianca` para cinco faixas (muito baixa, baixa, média, alta, muito alta).
2. **(for + listas)** Crie `listar_alunos_por_turma(turma)` que retorne uma lista só com os alunos da turma informada.
3. **(dicionários)** No relatório, ordene os conteúdos do que mais trava para o que menos trava.
4. **(exceções)** Crie uma exceção `ErroValidacao` e use-a para validar o formato do e-mail do professor.
5. **(arquivos)** Faça uma função `exportar_relatorio()` que grave o relatório em `relatorio.txt`.
6. **(funções)** Crie `proximo_id` que **nunca** reaproveite IDs excluídos.
7. **(integração)** Faça `listar` de conteúdos mostrar o **nome** do professor em vez do `professor_id`.
8. **(Git)** Crie um repositório, faça um commit por exercício resolvido e escreva mensagens claras.

---

## 12. Glossário

| Termo | Significado |
|---|---|
| **CRUD** | Create, Read, Update, Delete: as quatro operações básicas sobre dados |
| **Registro** | Um item de dados; aqui, um dicionário |
| **Chave estrangeira** | Campo que guarda o ID de outra entidade (`professor_id`) |
| **Integridade referencial** | Garantia de que toda referência aponta para algo que existe |
| **CSV** | *Comma-Separated Values*: arquivo de texto em formato de tabela |
| **Escopo** | Região do código onde um nome de variável é visível |
| **Exceção** | Evento que interrompe o fluxo normal quando algo inesperado acontece |
| **DRY** | Princípio de não repetir código |
| **`match`** | Estrutura de decisão por padrões (Python 3.10+) |
| **Busca linear** | Procurar um item percorrendo a lista do início ao fim |
