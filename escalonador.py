"""Motor de simulacao do escalonador por creditos."""
from pathlib import Path
from carregador import carregar_sistema
from filas import FilaProntos, FilaBloqueados, verificar_e_redistribuir_creditos
from interpretador import executar_instrucao
from logger import Logger


def executar_escalonamento(
    diretorio_programas: str | Path = "programas",
    caminho_prioridades: str | Path = "prioridades.txt",
    caminho_quantum: str | Path = "quantum.txt",
    caminho_log: str | Path | None = None,
) -> str:
    tabela, iniciais, quantum = carregar_sistema(
        diretorio_programas=str(diretorio_programas),
        caminho_prioridades=str(caminho_prioridades),
        caminho_quantum=str(caminho_quantum),
    )
    logger = Logger(quantum, caminho_log)
    total_processos = len(iniciais)
    prontos = FilaProntos(iniciais)
    bloqueados = FilaBloqueados()
    for processo in iniciais:
        logger.registrar_carregamento(processo.nome)

    while len(tabela) > 0:
        # Sem prontos, simula a passagem de tempo de E/S, sem executar instrucoes.
        while prontos.esta_vazia() and not bloqueados.esta_vazia():
            for liberado in bloqueados.decrementar_esperas():
                bloqueados.remover(liberado)
                prontos.inserir(liberado, todos_processos=tabela.listar_processos())

        if prontos.esta_vazia():
            raise RuntimeError("Existem processos ativos, mas nenhum esta pronto ou bloqueado.")

        verificar_e_redistribuir_creditos(tabela, prontos)
        processo = prontos.remover_proximo()
        processo.estado = "EXECUTANDO"
        logger.registrar_execucao(processo.nome)
        if processo.creditos > 0:
            processo.creditos -= 1

        quantidade = 0
        motivo = "QUANTUM"
        for _ in range(quantum):
            tipo = executar_instrucao(processo)
            quantidade += 1
            if tipo in ("E/S", "SAIDA"):
                motivo = tipo
                break

        logger.registrar_surto(quantidade)
        if motivo == "SAIDA":
            logger.registrar_termino(processo.nome, processo.X, processo.Y)
            processo.estado = "TERMINADO"
            tabela.remover_processo(processo.nome)
        elif motivo == "E/S":
            logger.registrar_es(processo.nome)
            logger.registrar_interrupcao(processo.nome, quantidade)
            bloqueados.inserir(processo, tempo_espera=2)
        else:
            logger.registrar_interrupcao(processo.nome, quantidade)
            prontos.inserir(processo, todos_processos=tabela.listar_processos())

        # Nunca reduz a espera do processo que solicitou E/S neste mesmo surto.
        for liberado in bloqueados.decrementar_esperas(processo_executou=processo):
            bloqueados.remover(liberado)
            prontos.inserir(liberado, todos_processos=tabela.listar_processos())

    return logger.finalizar_log(total_processos)
