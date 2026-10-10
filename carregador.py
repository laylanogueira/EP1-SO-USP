"""Carrega os programas, prioridades e quantum para a Etapa 1."""
from pathlib import Path
from bcp import BCP
from tabela_processos import TabelaProcessos


def ler_quantum(caminho_quantum: str = "quantum.txt") -> int:
    caminho = Path(caminho_quantum)
    quantum = int(caminho.read_text(encoding="utf-8").strip())
    if quantum <= 0:
        raise ValueError("O quantum deve ser um inteiro positivo.")
    return quantum


def ler_prioridades(caminho_prioridades: str = "prioridades.txt") -> list[int]:
    linhas = Path(caminho_prioridades).read_text(encoding="utf-8").splitlines()
    prioridades = [int(linha.strip()) for linha in linhas if linha.strip()]
    if any(p < 0 for p in prioridades):
        raise ValueError("As prioridades não podem ser negativas.")
    return prioridades


def carregar_sistema(
    diretorio_programas: str = "programas",
    caminho_prioridades: str = "prioridades.txt",
    caminho_quantum: str = "quantum.txt",
) -> tuple[TabelaProcessos, list[BCP], int]:
    diretorio = Path(diretorio_programas)
    # Aceita tanto os arquivos na raiz quanto dentro de programas/.
    # Caminhos explicitos continuam sendo respeitados.
    if str(caminho_prioridades) == "prioridades.txt" and not Path(caminho_prioridades).is_file():
        caminho_prioridades = diretorio / "prioridades.txt"
    if str(caminho_quantum) == "quantum.txt" and not Path(caminho_quantum).is_file():
        caminho_quantum = diretorio / "quantum.txt"
    quantum = ler_quantum(caminho_quantum)
    prioridades = ler_prioridades(caminho_prioridades)
    if not diretorio.is_dir():
        raise FileNotFoundError(f"Diretório de programas não encontrado: {diretorio}")

    ignorados = {"prioridades.txt", "quantum.txt", Path(caminho_prioridades).name, Path(caminho_quantum).name}
    arquivos = sorted(p for p in diretorio.glob("*.txt") if p.name not in ignorados)
    if not arquivos:
        raise FileNotFoundError(f"Nenhum programa .txt encontrado em: {diretorio}")
    if len(arquivos) != len(prioridades):
        raise ValueError(
            f"Divergência detectada: {len(arquivos)} programas e "
            f"{len(prioridades)} prioridades."
        )

    tabela = TabelaProcessos()
    bcps = []
    for arquivo, prioridade in zip(arquivos, prioridades):
        linhas = [linha.strip() for linha in arquivo.read_text(encoding="utf-8").splitlines()
                  if linha.strip()]
        if len(linhas) < 2:
            raise ValueError(f"Programa sem nome ou instruções: {arquivo.name}")
        nome_programa = linhas[0]
        instrucoes = linhas[1:]
        if len(instrucoes) > 21:
            raise ValueError(f"Programa {arquivo.name} excede 21 instruções.")
        if instrucoes[-1] != "SAIDA":
            raise ValueError(f"Programa {arquivo.name} não termina com SAIDA.")
        bcp = BCP(nome=nome_programa, nome_arquivo=arquivo.name,
                  texto=instrucoes, prioridade=prioridade)
        tabela.adicionar_processo(bcp)
        bcps.append(bcp)

    fila_prontos = sorted(bcps, key=lambda processo: processo.creditos, reverse=True)
    return tabela, fila_prontos, quantum
