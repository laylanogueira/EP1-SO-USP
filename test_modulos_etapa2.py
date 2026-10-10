import tempfile
import unittest
from pathlib import Path
from bcp import BCP
from interpretador import executar_instrucao
from logger import Logger


class TestInterpretador(unittest.TestCase):
    def criar(self, texto):
        return BCP("TESTE", "01.txt", texto, 1)

    def test_atribuicoes_com_negativos(self):
        p = self.criar(["X=-8", "Y=10", "COM", "SAIDA"])
        self.assertEqual([executar_instrucao(p) for _ in range(4)],
                         ["ATRIBUICAO", "ATRIBUICAO", "COM", "SAIDA"])
        self.assertEqual((p.X, p.Y, p.pc), (-8, 10, 4))

    def test_es_avanca_pc_sem_bloquear(self):
        p = self.criar(["E/S", "SAIDA"])
        self.assertEqual(executar_instrucao(p), "E/S")
        self.assertEqual((p.pc, p.estado), (1, "PRONTO"))

    def test_pc_fora(self):
        p = self.criar(["COM"])
        p.pc = -1
        with self.assertRaises(IndexError): executar_instrucao(p)
        p.pc = 1
        with self.assertRaises(IndexError): executar_instrucao(p)

    def test_instrucao_invalida_nao_avanca(self):
        p = self.criar(["X=abc"])
        with self.assertRaises(ValueError): executar_instrucao(p)
        self.assertEqual(p.pc, 0)


class TestLogger(unittest.TestCase):
    def test_conta_es_saida_e_quantum(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Logger(3, Path(tmp) / "log03.txt")
            log.registrar_carregamento("P1")
            log.registrar_execucao("P1")
            log.registrar_surto(2)
            log.registrar_es("P1")
            log.registrar_execucao("P2")
            log.registrar_surto(3)
            log.registrar_interrupcao("P2", 3)
            log.registrar_execucao("P3")
            log.registrar_surto(1)
            log.registrar_termino("P3", 0, 0)
            conteudo = log.finalizar_log(3)
            self.assertIn("MEDIA DE INSTRUCOES: 2\n", conteudo)
            self.assertIn("MEDIA DE TROCAS: 0.3333\n", conteudo)
            self.assertEqual(conteudo, log.caminho_log.read_text(encoding="utf8"))

    def test_log_vazio(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Logger(1, Path(tmp)/"log01.txt")
            self.assertIn("MEDIA DE INSTRUCOES: 0", log.finalizar_log(0))


if __name__ == "__main__": unittest.main()
