"""Navegação: voltar / menu principal em qualquer etapa, e os menus do programa."""

from config import ENTIDADES


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


def menu_crud(entidade):
    """Menu de um CRUD (Criar, Listar/Buscar, Editar, Excluir) para a entidade escolhida.

    Usa while para repetir até o usuário voltar, e match para escolher a ação.
    """
    # Importado aqui dentro para evitar import circular:
    # cadastros -> validacao -> navegacao (entrada) -> cadastros.
    from cadastros import criar, editar, excluir, listar

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


def menu_principal():
    """Menu inicial do Grillo: escolhe o CRUD ou o relatório. Roda até o usuário sair."""
    from relatorios import relatorio_dificuldades

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
