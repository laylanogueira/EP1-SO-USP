"""
Modulo test_filas.py
Testes unitarios para validar as regras do modulo filas.py (Etapa 2).
"""

import unittest
from bcp import BCP
from tabela_processos import TabelaProcessos
from filas import FilaProntos, FilaBloqueados, verificar_e_redistribuir_creditos

class TestFilas(unittest.TestCase):

    def setUp(self):
        # Criacao de BCPs para os testes
        self.p1 = BCP("TESTE-1", "01.txt", ["X=8", "COM", "SAIDA"], prioridade=1)
        self.p2 = BCP("TESTE-2", "02.txt", ["COM", "SAIDA"], prioridade=3)
        self.p3 = BCP("TESTE-3", "03.txt", ["COM", "SAIDA"], prioridade=2)
        self.p4 = BCP("TESTE-4", "04.txt", ["COM", "SAIDA"], prioridade=10)

        self.tabela = TabelaProcessos()
        for p in [self.p1, self.p2, self.p3, self.p4]:
            self.tabela.adicionar_processo(p)

    def test_01_obter_proximo_retorna_bcp_e_nao_lista(self):
        """Valida que FilaProntos.obter_proximo() retorna uma instancia de BCP, e nao a lista inteira."""
        fila = FilaProntos([self.p1, self.p2, self.p3])
        proximo = fila.obter_proximo()

        # Deve ser uma instancia de BCP
        self.assertIsInstance(proximo, BCP, "obter_proximo() deve retornar um objeto BCP, nao uma lista.")
        self.assertEqual(proximo.nome, "TESTE-2", "O proximo BCP deve ser o de maior credito (TESTE-2 com prioridade 3).")
        
        # O tamanho da fila deve permanecer inalterado (nao deve ter removido)
        self.assertEqual(len(fila), 3, "obter_proximo() nao deve remover o processo da fila.")

    def test_02_decrementar_esperas_ignora_processo_que_executou(self):
        """
        Valida que FilaBloqueados.decrementar_esperas(processo_executou)
        nao decrementa a espera do processo que acabou de solicitar E/S,
        garantindo que ele aguarde 2 execucoes de OUTROS processos.
        """
        fila_bloq = FilaBloqueados()

        # Processo P1 executa e solicita E/S -> entra na FilaBloqueados com espera_es = 2
        fila_bloq.inserir(self.p1, tempo_espera=2)
        self.assertEqual(self.p1.espera_es, 2)

        # Fim do surto do P1: decrementar_esperas é chamado passando P1 como processo_executou
        desbloqueados_surto_p1 = fila_bloq.decrementar_esperas(processo_executou=self.p1)
        self.assertEqual(len(desbloqueados_surto_p1), 0)
        self.assertEqual(self.p1.espera_es, 2, "A espera_es de P1 deve continuar em 2 no surto em que ele solicitou E/S.")

        # Execucao 1 de OUTRO processo (P2): Fim do surto de P2
        desbloqueados_surto_p2 = fila_bloq.decrementar_esperas(processo_executou=self.p2)
        self.assertEqual(len(desbloqueados_surto_p2), 0)
        self.assertEqual(self.p1.espera_es, 1, "A espera_es de P1 deve ser reduzida para 1 apos a execucao de P2.")

        # Execucao 2 de OUTRO processo (P3): Fim do surto de P3
        desbloqueados_surto_p3 = fila_bloq.decrementar_esperas(processo_executou=self.p3)
        self.assertEqual(len(desbloqueados_surto_p3), 1)
        self.assertEqual(desbloqueados_surto_p3[0].nome, "TESTE-1")
        self.assertEqual(self.p1.espera_es, 0, "A espera_es de P1 deve chegar a 0 apos a segunda execucao de outro processo.")

    def test_03_ordenacao_inicial_fila_prontos(self):
        """Valida que a FilaProntos ordena os processos do maior credito para o menor."""
        fila = FilaProntos([self.p1, self.p2, self.p3, self.p4])
        
        self.assertEqual(fila.remover_proximo().nome, "TESTE-4")  # Creditos: 10
        self.assertEqual(fila.remover_proximo().nome, "TESTE-2")  # Creditos: 3
        self.assertEqual(fila.remover_proximo().nome, "TESTE-3")  # Creditos: 2
        self.assertEqual(fila.remover_proximo().nome, "TESTE-1")  # Creditos: 1

    def test_04_comportamento_fifo_quando_prontos_zerados_mas_ha_bloqueados_com_credito(self):
        """
        Valida que se os processos na FilaProntos estao com 0 creditos, porem ha
        processos no sistema com creditos > 0 (ex: bloqueados), a fila atua em FIFO.
        """
        self.p1.creditos = 0
        self.p2.creditos = 0
        self.p3.creditos = 2  # P3 tem credito e esta Bloqueado

        fila_prontos = FilaProntos()
        # Insere P1 e depois P2 (ambos com credito 0)
        fila_prontos.inserir(self.p1, todos_processos=self.tabela.listar_processos())
        fila_prontos.inserir(self.p2, todos_processos=self.tabela.listar_processos())

        # Ordem deve ser FIFO (P1 depois P2)
        proximo1 = fila_prontos.remover_proximo()
        proximo2 = fila_prontos.remover_proximo()

        self.assertEqual(proximo1.nome, "TESTE-1")
        self.assertEqual(proximo2.nome, "TESTE-2")

    def test_05_redistribuicao_somente_quando_todos_zerados(self):
        """Valida que a redistribuicao de creditos so ocorre quando TODOS no sistema possuem 0 creditos."""
        self.p1.creditos = 0
        self.p2.creditos = 0
        self.p3.creditos = 0
        self.p4.creditos = 1  # Ainda existe 1 processo com credito

        fila_prontos = FilaProntos([self.p1, self.p2, self.p3])

        redistribuiu = verificar_e_redistribuir_creditos(self.tabela, fila_prontos)
        self.assertFalse(redistribuiu, "Nao deve redistribuir enquanto houver algum processo com credito.")

        # Agora zera o credito do ultimo processo
        self.p4.creditos = 0
        redistribuiu_agora = verificar_e_redistribuir_creditos(self.tabela, fila_prontos)
        self.assertTrue(redistribuiu_agora, "Deve redistribuir quando TODOS os processos no sistema estiverem zerados.")

        # Verifica se os creditos foram restaurados para o valor da prioridade original
        self.assertEqual(self.p1.creditos, 1)
        self.assertEqual(self.p2.creditos, 3)
        self.assertEqual(self.p3.creditos, 2)
        self.assertEqual(self.p4.creditos, 10)

if __name__ == "__main__":
    unittest.main()
