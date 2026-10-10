"""Bloco de Controle de Processo (BCP) da máquina fictícia."""


class BCP:
    def __init__(self, nome: str, nome_arquivo: str, texto: list[str], prioridade: int):
        self.nome = nome
        self.nome_arquivo = nome_arquivo
        self.pc = 0
        self.estado = "PRONTO"
        self.prioridade = prioridade
        self.creditos = prioridade
        self.X = 0
        self.Y = 0
        self.texto = texto
        self.espera_es = 0

    def __repr__(self) -> str:
        return (f"<BCP {self.nome} ({self.nome_arquivo}) - Estado: {self.estado}, "
                f"PC: {self.pc}, Creditos: {self.creditos}, Prioridade: {self.prioridade}, "
                f"X: {self.X}, Y: {self.Y}>")
