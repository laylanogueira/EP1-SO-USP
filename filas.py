"""
Modulo filas.py
Gerencia a Fila de Prontos e a Fila de Bloqueados para o Escalonador de Processos.
"""

from bcp import BCP
from tabela_processos import TabelaProcessos

class FilaProntos:
    """
    Gerencia a fila de processos no estado PRONTO.
    
    Regras de ordenacao:
    1. Por padrao, e ordenada de forma decrescente pelo numero de creditos restantes.
    2. Em caso de empate de creditos, mantem a ordem de chegada (estabilidade).
    3. Quando todos os processos da Fila de Prontos estao com 0 creditos, mas ainda
       existem processos Bloqueados com creditos restantes, a Fila de Prontos
       funciona temporariamente como FIFO (ordem de chegada) sem redistribuir creditos.
    """

    def __init__(self, lista_inicial: list[BCP] | None = None):
        self.fila: list[BCP] = []
        if lista_inicial:
            for bcp in lista_inicial:
                self.inserir(bcp)

    def inserir(self, bcp: BCP, todos_processos: list[BCP] | None = None):
        """
        Insere um BCP na Fila de Prontos, ajusta seu estado para PRONTO
        e mantem a fila ordenada adequadamente.
        """
        bcp.estado = "PRONTO"
        if bcp not in self.fila:
            self.fila.append(bcp)
        self.ordenar(todos_processos)

    def remover_proximo(self) -> BCP | None:
        """Remove e retorna o proximo BCP a ser executado (cabeca da fila)."""
        if not self.fila:
            return None
        return self.fila.pop(0)

    def obter_proximo(self) -> BCP | None:
        """Retorna o proximo BCP a ser executado sem remove-lo da fila."""
        if not self.fila:
            return None
        return self.fila[0]

    def ordenar(self, todos_processos: list[BCP] | None = None):
        """
        Reordena a Fila de Prontos conforme as regras de credito do enunciado.
        
        Se todos os processos da Fila de Prontos tiverem 0 creditos, porem existir
        algum processo no sistema (ex: bloqueado) com creditos > 0, a fila atua como FIFO,
        preservando a ordem atual de insercao.
        """
        if not self.fila:
            return

        # Verifica se todos na fila de prontos estao com 0 creditos
        prontos_zerados = all(p.creditos == 0 for p in self.fila)

        # Verifica se existe algum processo no sistema inteiro com creditos > 0
        ha_credito_no_sistema = False
        if todos_processos:
            ha_credito_no_sistema = any(p.creditos > 0 for p in todos_processos)

        # Se prontos estao zerados mas ha bloqueados com credito, mantem ordem FIFO
        if prontos_zerados and ha_credito_no_sistema:
            return

        # Ordenacao padrao: maior numero de creditos primeiro (sort estavel preserva empate)
        self.fila.sort(key=lambda p: p.creditos, reverse=True)

    def todos_zerados(self) -> bool:
        """Verifica se todos os processos na Fila de Prontos estao com 0 creditos."""
        return all(p.creditos == 0 for p in self.fila)

    def esta_vazia(self) -> bool:
        """Retorna True se a Fila de Prontos estiver vazia."""
        return len(self.fila) == 0

    def __len__(self) -> int:
        return len(self.fila)

    def __repr__(self) -> str:
        return f"<FilaProntos ({len(self.fila)}): {[f'{p.nome}(cred={p.creditos})' for p in self.fila]}>"

class FilaBloqueados:
    """
    Gerencia a fila de processos no estado BLOQUEADO (ordem FIFO).
    
    Regras de E/S:
    1. Cada processo bloqueado entra no final da fila com espera_es = 2.
    2. O tempo de espera representa a necessidade de aguardar 2 execucoes de OUTROS processos.
    3. A decrementacao de espera_es ocorre ao final da execucao de um surto/quantum de outro processo.
       O processo que acabou de executar e solicitar E/S (processo_executou) NAO tem sua espera descontada no mesmo surto.
    """

    def __init__(self):
        self.fila: list[BCP] = []

    def inserir(self, bcp: BCP, tempo_espera: int = 2):
        """
        Insere o processo no final da Fila de Bloqueados,
        define seu estado como BLOQUEADO e ajusta o contador de espera_es.
        """
        bcp.estado = "BLOQUEADO"
        bcp.espera_es = tempo_espera
        if bcp not in self.fila:
            self.fila.append(bcp)

    def decrementar_esperas(self, processo_executou: BCP | None = None) -> list[BCP]:
        """
        Decrementa em 1 unidade o tempo de espera_es dos processos bloqueados.
        Se processo_executou for informado, ele NAO tem sua espera descontada neste surto,
        garantindo que um processo recem-bloqueado aguarde 2 execucoes completas de OUTROS processos.

        Retorna uma lista com os BCPs cujo tempo de espera chegou a 0 (prontos para desbloquear).
        """
        prontos_para_desbloquear: list[BCP] = []
        for bcp in self.fila:
            if bcp is not processo_executou:
                bcp.espera_es -= 1
                if bcp.espera_es <= 0:
                    prontos_para_desbloquear.append(bcp)
        return prontos_para_desbloquear

    def remover(self, bcp: BCP):
        """Remove um BCP especifico da Fila de Bloqueados."""
        if bcp in self.fila:
            self.fila.remove(bcp)

    def esta_vazia(self) -> bool:
        """Retorna True se a Fila de Bloqueados estiver vazia."""
        return len(self.fila) == 0

    def __len__(self) -> int:
        return len(self.fila)

    def __repr__(self) -> str:
        return f"<FilaBloqueados ({len(self.fila)}): {[f'{p.nome}(esp={p.espera_es})' for p in self.fila]}>"

def verificar_e_redistribuir_creditos(tabela: TabelaProcessos, fila_prontos: FilaProntos) -> bool:
    """
    Verifica se TODOS os processos ativos na Tabela de Processos (Prontos e Bloqueados)
    estao com 0 creditos. Se sim, redistribui os creditos de todos os BCPs para o valor
    de suas prioridades originais e reordena a Fila de Prontos.

    Retorna True se a redistribuicao foi realizada, False caso contrario.
    """
    processos = tabela.listar_processos()
    if not processos:
        return False

    # A redistribuicao SO ocorre quando TODOS os processos no sistema possuem 0 creditos
    if all(p.creditos == 0 for p in processos):
        for p in processos:
            p.creditos = p.prioridade
        fila_prontos.ordenar(todos_processos=processos)
        return True

    return False
