import pymysql

def conectar():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Gustavo210874.",
        database="estoque_db",
        charset='utf8mb4'
    )

def inserir_produto(nome, preco, validade):
    with conectar() as conn:
        with conn.cursor() as cursor:
            sql = "INSERT INTO produtos (nome, preco, validade) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nome, preco, validade))
        conn.commit()

def listar_produtos():
    with conectar() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM produtos")
            return cursor.fetchall()

if __name__ == "__main__":
    conn = None
    try:
        # Teste de conexão
        print("Testando conexão com o banco de dados...")
        conn = conectar()
        print("✅ Conexão bem sucedida!")

        # Verifica se a tabela existe
        with conn.cursor() as cursor:
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS produtos (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        nome VARCHAR(255) NOT NULL,
                        preco DECIMAL(10,2) NOT NULL,
                        validade DATE NOT NULL
                    )
                """)
                conn.commit()
                print("✅ Tabela 'produtos' verificada/criada com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao verificar/criar tabela: {str(e)}")

        # Testa inserção
        def atualizar_produto(id, nome, preco, validade):
            with conectar() as conn:
                with conn.cursor() as cursor:
                    sql = """
                        UPDATE produtos 
                        SET nome = %s, preco = %s, validade = %s 
                        WHERE id = %s
                    """
                    cursor.execute(sql, (nome, preco, validade, id))
                conn.commit()


        def deletar_produto(id):
            with conectar() as conn:
                with conn.cursor() as cursor:
                    sql = "DELETE FROM produtos WHERE id = %s"
                    cursor.execute(sql, (id,))
                conn.commit()


        def buscar_produto(id):
            with conectar() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM produtos WHERE id = %s", (id,))
                    return cursor.fetchone()


        # Testa listagem
        try:
            produtos = listar_produtos()
            print("\nProdutos cadastrados:")
            for p in produtos:
                print(f"ID: {p[0]}, Nome: {p[1]}, Preço: R${p[2]:.2f}, Validade: {p[3]}")
            print("✅ Listagem realizada com sucesso!")
        except Exception as e:
            print(f"❌ Erro ao listar produtos: {str(e)}")

    except pymysql.Error as err:
        print(f"❌ Erro de conexão com MySQL: {err}")
        print("\nVerifique:")
        print("1. Se o servidor MySQL está rodando")
        print("2. Se as credenciais estão corretas")
        print("3. Se o banco de dados 'estoque_db' existe")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
    finally:
        if conn:
            conn.close()
