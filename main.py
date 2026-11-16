"""Inicialização do Grillo: execute este arquivo (python main.py)."""

from navegacao import menu_principal


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
