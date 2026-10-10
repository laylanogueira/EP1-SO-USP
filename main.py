"""Entrada do simulador: python main.py [programas] [prioridades] [quantum] [log]."""
import sys
from escalonador import executar_escalonamento


def main():
    argumentos = sys.argv[1:]
    if len(argumentos) > 4:
        print("Uso: python main.py [diretorio_programas] [prioridades.txt] [quantum.txt] [log.txt]", file=sys.stderr)
        return 2
    caminhos = ["programas", "prioridades.txt", "quantum.txt", None]
    caminhos[:len(argumentos)] = argumentos
    try:
        conteudo = executar_escalonamento(*caminhos)
    except (OSError, ValueError, RuntimeError, IndexError) as erro:
        print(f"Erro ao executar o escalonador: {erro}", file=sys.stderr)
        return 1
    print("Execucao concluida. Resumo do log:")
    for linha in conteudo.strip().splitlines()[-3:]:
        print(linha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
