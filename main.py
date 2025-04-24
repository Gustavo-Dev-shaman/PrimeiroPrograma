"""
Sistema de Gerenciamento de Estoque
----------------------------------
Este é um sistema de gerenciamento de estoque desenvolvido em Python usando PyQt6 para a interface gráfica
e MySQL para armazenamento de dados.

Autor: [Seu Nome]
Data: [Data]
Versão: 1.0
"""

import sys
from datetime import datetime
import pymysql
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QTableWidgetItem
from interface import Ui_MainWindow
from dotenv import load_dotenv
import os
import re


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Classe principal que gerencia a interface gráfica e as operações do sistema.
    Herda de QMainWindow para criar a janela principal e Ui_MainWindow para a interface.
    """

    def __init__(self):
        """Inicializa a janela principal e configura os elementos básicos."""
        super().__init__()
        self.setupUi(self)

        # Conecta os botões às suas respectivas funções
        self.inputProduto.clicked.connect(self.adicionar_produto)
        self.removeProduto.clicked.connect(self.excluir_produto_por_id)

        # Configura a tabela inicial
        self.configurar_tabela()
        self.atualizar_tabela()

    def conectar(self):
        """
        Estabelece conexão com o banco de dados MySQL.
        Utiliza variáveis de ambiente para as credenciais de conexão.

        Returns:
            pymysql.Connection: Objeto de conexão com o banco de dados

        Raises:
            Exception: Se houver erro na conexão com o banco
        """
        load_dotenv()  # Carrega variáveis de ambiente do arquivo .env
        try:
            return pymysql.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME'),
                charset='utf8mb4',
                connect_timeout=5,
                read_timeout=5,
                write_timeout=5
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro de Conexão", "Não foi possível conectar ao banco de dados")
            raise

    def configurar_tabela(self):
        """Configura o layout inicial da tabela de produtos."""
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Nome", "Preço", "Validade"])
        header = self.tableWidget.horizontalHeader()
        for i in range(4):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

    def validar_nome_produto(self, nome):
        """
        Valida o nome do produto segundo regras específicas.

        Args:
            nome (str): Nome do produto a ser validado

        Returns:
            str: Nome validado

        Raises:
            ValueError: Se o nome não atender aos critérios
        """
        if not nome:
            raise ValueError("O nome não pode estar vazio")
        if len(nome) > 100:
            raise ValueError("Nome do produto muito longo")
        if not re.match(r"^[a-zA-Z0-9\s\-_.,]+$", nome):
            raise ValueError("Nome contém caracteres inválidos")
        return nome

    def adicionar_produto(self):
        """
        Adiciona um novo produto ao banco de dados.
        Realiza validações nos dados antes da inserção.
        """
        try:
            # Obtém e valida os dados do formulário
            nome = self.validar_nome_produto(self.lineEdit.text().strip())
            preco_text = self.lineEdit_2.text().strip()
            validade = self.lineEdit_3.text().strip()

            # Valida o preço
            try:
                preco = float(preco_text)
                if not 0 < preco < 1000000:
                    raise ValueError("Preço fora do intervalo permitido")
            except ValueError:
                raise ValueError("Digite um preço válido")

            # Valida a data de validade
            try:
                data = datetime.strptime(validade, '%d/%m/%Y')
                if data < datetime.now():
                    raise ValueError("A data de validade não pode ser no passado")
                validade_formatada = data.strftime('%Y-%m-%d')
            except ValueError:
                raise ValueError("Data inválida. Use o formato DD/MM/YYYY")

            # Insere no banco de dados
            with self.conectar() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO produtos (nome, preco, validade) 
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(sql, (nome, preco, validade_formatada))
                conn.commit()

            QMessageBox.information(self, "Sucesso", "Produto adicionado com sucesso!")
            self.limpar_campos()
            self.atualizar_tabela()

        except ValueError as e:
            QMessageBox.warning(self, "Erro de Validação", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erro", "Erro ao adicionar produto")
            print(f"Erro detalhado: {str(e)}")  # Log do erro

    def excluir_produto_por_id(self):
        """Remove um produto do banco de dados com base no ID fornecido."""
        try:
            id_text = self.removeProduto_2.text().strip()

            if not id_text:
                QMessageBox.warning(self, "Aviso", "Digite o ID do produto")
                return

            try:
                id_produto = int(id_text)
                if id_produto <= 0:
                    raise ValueError()
            except ValueError:
                QMessageBox.warning(self, "Erro", "ID inválido")
                return

            # Processo de exclusão com confirmação
            with self.conectar() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("START TRANSACTION")
                    cursor.execute("SELECT nome FROM produtos WHERE id = %s FOR UPDATE", (id_produto,))
                    produto = cursor.fetchone()

                    if not produto:
                        cursor.execute("ROLLBACK")
                        QMessageBox.warning(self, "Erro", "Produto não encontrado")
                        return

                    resposta = QMessageBox.question(
                        self, 'Confirmar Exclusão',
                        f'Deseja excluir o produto "{produto[0]}"?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )

                    if resposta == QMessageBox.StandardButton.Yes:
                        cursor.execute("DELETE FROM produtos WHERE id = %s", (id_produto,))
                        conn.commit()
                        QMessageBox.information(self, "Sucesso", "Produto excluído!")
                        self.atualizar_tabela()
                        self.removeProduto_2.clear()
                    else:
                        cursor.execute("ROLLBACK")

        except Exception as e:
            QMessageBox.critical(self, "Erro", "Erro ao excluir produto")
            print(f"Erro detalhado: {str(e)}")  # Log do erro

    def atualizar_tabela(self):
        """Atualiza a exibição da tabela com os dados mais recentes do banco."""
        try:
            with self.conectar() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM produtos")
                    produtos = cursor.fetchall()

                    self.tableWidget.setRowCount(len(produtos))
                    for i, produto in enumerate(produtos):
                        self.tableWidget.setItem(i, 0, QTableWidgetItem(str(produto[0])))
                        self.tableWidget.setItem(i, 1, QTableWidgetItem(produto[1]))
                        self.tableWidget.setItem(i, 2, QTableWidgetItem(f"R$ {produto[2]:.2f}"))
                        self.tableWidget.setItem(i, 3, QTableWidgetItem(str(produto[3])))

        except Exception as e:
            QMessageBox.critical(self, "Erro", "Erro ao atualizar tabela")
            print(f"Erro detalhado: {str(e)}")  # Log do erro

    def limpar_campos(self):
        """Limpa todos os campos de entrada do formulário."""
        self.lineEdit.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        self.lineEdit_4.clear()
        self.removeProduto_2.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())