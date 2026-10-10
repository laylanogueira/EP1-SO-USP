"""Testes reproduzíveis da Etapa 1, sem depender de caminhos do NotebookLM."""
import tempfile
import unittest
from pathlib import Path
from bcp import BCP
from tabela_processos import TabelaProcessos
from carregador import carregar_sistema, ler_prioridades, ler_quantum


class TestEtapa1(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.raiz = Path(self.temp.name)
        self.programas = self.raiz / "programas"
        self.programas.mkdir()
        (self.raiz / "quantum.txt").write_text("3\n", encoding="utf-8")
        (self.raiz / "prioridades.txt").write_text("1\n3\n10\n", encoding="utf-8")
        (self.programas / "01.txt").write_text("TESTE-1\nX=8\nCOM\nSAIDA\n", encoding="utf-8")
        (self.programas / "02.txt").write_text("TESTE-2\nY=4\nSAIDA\n", encoding="utf-8")
        (self.programas / "03.txt").write_text("TESTE-3\nE/S\nSAIDA\n", encoding="utf-8")

    def carregar(self):
        return carregar_sistema(str(self.programas), str(self.raiz / "prioridades.txt"),
                               str(self.raiz / "quantum.txt"))

    def test_01_leitura_quantum(self):
        self.assertEqual(ler_quantum(str(self.raiz / "quantum.txt")), 3)

    def test_02_leitura_prioridades(self):
        prioridades = ler_prioridades(str(self.raiz / "prioridades.txt"))
        self.assertEqual(prioridades[0], 1)
        self.assertEqual(prioridades[1], 3)
        self.assertEqual(prioridades[2], 10)

    def test_03_bcp_e_tabela(self):
        tabela, fila, quantum = self.carregar()
        self.assertEqual((len(tabela), len(fila), quantum), (3, 3, 3))
        for bcp in tabela.listar_processos():
            self.assertEqual((bcp.pc, bcp.estado, bcp.X, bcp.Y, bcp.espera_es),
                             (0, "PRONTO", 0, 0, 0))
            self.assertEqual(bcp.creditos, bcp.prioridade)

    def test_04_nome_e_instrucoes(self):
        tabela, _, _ = self.carregar()
        proc_01 = tabela.obter_processo("TESTE-1")
        self.assertIsNotNone(proc_01)
        self.assertEqual(proc_01.nome_arquivo, "01.txt")
        self.assertEqual(proc_01.texto[0], "X=8")
        self.assertEqual(proc_01.texto[-1], "SAIDA")
        self.assertEqual(len(proc_01.texto), 3)

    def test_05_ordenacao(self):
        _, fila_prontos, _ = self.carregar()
        self.assertEqual(fila_prontos[0].nome, "TESTE-3")
        self.assertEqual(fila_prontos[0].creditos, 10)
        self.assertEqual(fila_prontos[1].nome, "TESTE-2")
        self.assertEqual(fila_prontos[1].creditos, 3)
        self.assertEqual(fila_prontos[-1].nome, "TESTE-1")

    def test_06_prioridades_divergentes(self):
        (self.raiz / "prioridades.txt").write_text("1\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Divergência detectada"):
            self.carregar()

    def test_07_remocao(self):
        tabela, _, _ = self.carregar()
        removido = tabela.remover_processo("TESTE-1")
        self.assertEqual(removido.nome, "TESTE-1")
        self.assertIsNone(tabela.obter_processo("TESTE-1"))
        self.assertEqual(len(tabela), 2)

    def test_08_quantum_invalido(self):
        (self.raiz / "quantum.txt").write_text("0", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.carregar()

    def test_09_nome_duplicado(self):
        (self.programas / "02.txt").write_text("TESTE-1\nCOM\nSAIDA\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicado"):
            self.carregar()


if __name__ == "__main__":
    unittest.main(verbosity=2)
