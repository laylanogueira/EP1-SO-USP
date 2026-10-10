"""Execucao de uma instrucao da maquina ficticia."""
from bcp import BCP


def executar_instrucao(bcp: BCP) -> str:
    """Executa uma instrucao e avanca o PC somente quando ela e valida.

    Retorna ATRIBUICAO, COM, E/S ou SAIDA. O escalonador e responsavel
    pelas mudancas de estado, bloqueio e termino do processo.
    """
    if not 0 <= bcp.pc < len(bcp.texto):
        raise IndexError(f"PC ({bcp.pc}) fora do texto de {bcp.nome}.")

    instrucao = bcp.texto[bcp.pc].strip()
    if instrucao == "COM":
        tipo = "COM"
    elif instrucao == "E/S":
        tipo = "E/S"
    elif instrucao == "SAIDA":
        tipo = "SAIDA"
    elif instrucao.startswith(("X=", "Y=")):
        registrador, valor_texto = instrucao.split("=", 1)
        try:
            valor = int(valor_texto)
        except ValueError as exc:
            raise ValueError(f"Atribuicao invalida: {instrucao!r} em {bcp.nome}") from exc
        setattr(bcp, registrador, valor)
        tipo = "ATRIBUICAO"
    else:
        raise ValueError(f"Instrucao invalida {instrucao!r} em {bcp.nome} (PC={bcp.pc}).")

    bcp.pc += 1
    return tipo
