"""Registro de eventos e estatisticas do escalonador."""
from pathlib import Path


class Logger:
    def __init__(self, quantum: int, caminho_saida: str | Path | None = None):
        if quantum <= 0:
            raise ValueError("O quantum deve ser positivo")
        self.quantum = quantum
        self.caminho_log = Path(caminho_saida) if caminho_saida is not None else Path(f"log{quantum:02d}.txt")
        self.linhas: list[str] = []
        self.total_interrupcoes = 0
        self.total_instrucoes = 0
        self.total_surtos = 0
        self.total_processos = 0

    def registrar_carregamento(self, nome_processo: str):
        self.linhas.append(f"Carregando {nome_processo}")

    def registrar_execucao(self, nome_processo: str):
        self.linhas.append(f"Executando {nome_processo}")

    def registrar_surto(self, instrucoes_executadas: int):
        """Contabiliza UM surto de CPU, independentemente de como terminou.

        Chamar exatamente uma vez por despacho, incluindo E/S e SAIDA.
        """
        if instrucoes_executadas <= 0:
            raise ValueError("Um surto deve executar ao menos uma instrucao")
        self.total_surtos += 1
        self.total_instrucoes += instrucoes_executadas

    def registrar_interrupcao(self, nome_processo: str, instrucoes_executadas: int):
        """Registra a preempcao; chamar registrar_surto separadamente."""
        self.total_interrupcoes += 1
        palavra = "instrucao" if instrucoes_executadas == 1 else "instrucoes"
        self.linhas.append(f"Interrompendo {nome_processo} apos {instrucoes_executadas} {palavra}")

    def registrar_es(self, nome_processo: str):
        self.linhas.append(f"E/S iniciada em {nome_processo}")

    def registrar_termino(self, nome_processo: str, x: int, y: int):
        self.linhas.append(f"{nome_processo} terminado. X={x}. Y={y}")

    def finalizar_log(self, total_processos: int) -> str:
        """Conta cada despacho, inclusive o ultimo surto encerrado por SAIDA."""
        if total_processos < 0:
            raise ValueError("total_processos nao pode ser negativo")
        self.total_processos = total_processos
        media_trocas = self.total_surtos / total_processos if total_processos else 0.0
        media_instrucoes = self.total_instrucoes / self.total_surtos if self.total_surtos else 0.0
        def fmt(valor: float) -> str:
            return f"{valor:.4f}".rstrip("0").rstrip(".")
        linhas = self.linhas + [
            f"MEDIA DE TROCAS: {fmt(media_trocas)}",
            f"MEDIA DE INSTRUCOES: {fmt(media_instrucoes)}",
            f"QUANTUM: {self.quantum}",
        ]
        conteudo = "\n".join(linhas) + "\n"
        self.caminho_log.parent.mkdir(parents=True, exist_ok=True)
        self.caminho_log.write_text(conteudo, encoding="utf-8")
        return conteudo
