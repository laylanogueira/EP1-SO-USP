"""Testes de integracao do motor e da interface de linha de comando."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from escalonador import executar_escalonamento
from main import main


class TestEscalonador(unittest.TestCase):
    def criar_entrada(self, raiz, programas, prioridades, quantum):
        pasta = raiz / "programas"
        pasta.mkdir()
        for indice, (nome, instrucoes) in enumerate(programas, 1):
            (pasta / f"{indice:02d}.txt").write_text(nome + "\n" + "\n".join(instrucoes) + "\n", encoding="utf-8")
        (raiz / "prioridades.txt").write_text("\n".join(map(str, prioridades)), encoding="utf-8")
        (raiz / "quantum.txt").write_text(str(quantum), encoding="utf-8")
        return pasta

    def executar(self, raiz):
        return executar_escalonamento(raiz / "programas", raiz / "prioridades.txt", raiz / "quantum.txt", raiz / "saida.txt")

    def test_programa_simples_finaliza(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_entrada(raiz, [("P1", ["X=7", "Y=-2", "SAIDA"])], [1], 2)
            log = self.executar(raiz)
            self.assertIn("P1 terminado. X=7. Y=-2", log)
            self.assertIn("MEDIA DE INSTRUCOES: 1.5", log)
            self.assertIn("MEDIA DE TROCAS: 2", log)
            self.assertEqual((raiz / "saida.txt").read_text(encoding="utf-8"), log)

    def test_es_espera_dois_outros_surtos(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_entrada(raiz, [
                ("P1", ["E/S", "SAIDA"]),
                ("P2", ["COM", "SAIDA"]),
                ("P3", ["COM", "SAIDA"]),
            ], [3, 2, 1], 1)
            log = self.executar(raiz)
            execucoes = [linha for linha in log.splitlines() if linha.startswith("Executando ")]
            self.assertEqual(execucoes[:3], ["Executando P1", "Executando P2", "Executando P3"])
            self.assertEqual(execucoes[3], "Executando P1")

    def test_todos_bloqueados_nao_trava(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_entrada(raiz, [("P1", ["E/S", "SAIDA"])], [1], 1)
            log = self.executar(raiz)
            self.assertEqual(log.count("Executando P1"), 2)
            self.assertIn("P1 terminado", log)

    def test_arquivos_de_configuracao_dentro_de_programas(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            pasta = self.criar_entrada(raiz, [("P1", ["SAIDA"])], [1], 3)
            (raiz / "prioridades.txt").replace(pasta / "prioridades.txt")
            (raiz / "quantum.txt").replace(pasta / "quantum.txt")
            log = executar_escalonamento(pasta, caminho_log=raiz / "saida.txt")
            self.assertIn("P1 terminado", log)

    def test_main_argumentos(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.criar_entrada(raiz, [("P1", ["SAIDA"])], [1], 3)
            with patch("sys.argv", ["main.py", str(raiz / "programas"), str(raiz / "prioridades.txt"), str(raiz / "quantum.txt"), str(raiz / "log.txt")]):
                self.assertEqual(main(), 0)
            self.assertTrue((raiz / "log.txt").exists())


if __name__ == "__main__":
    unittest.main()
