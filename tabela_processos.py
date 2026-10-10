"""Tabela de processos ativos, indexada pelo nome do programa."""
from bcp import BCP


class TabelaProcessos:
    def __init__(self):
        self.processos: dict[str, BCP] = {}

    def adicionar_processo(self, bcp: BCP) -> None:
        if bcp.nome in self.processos:
            raise ValueError(f"Nome de programa duplicado: {bcp.nome}")
        self.processos[bcp.nome] = bcp

    def remover_processo(self, nome: str) -> BCP | None:
        return self.processos.pop(nome, None)

    def obter_processo(self, nome: str) -> BCP | None:
        return self.processos.get(nome)

    def listar_processos(self) -> list[BCP]:
        return list(self.processos.values())

    def __len__(self) -> int:
        return len(self.processos)

    def __repr__(self) -> str:
        return f"<TabelaProcessos com {len(self.processos)} processos: {list(self.processos)}>"
