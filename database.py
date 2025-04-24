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


def excluir_produto(id):
    with conectar() as conn:
        with conn.cursor() as cursor:
            sql = "DELETE FROM produtos WHERE id = %s"
            cursor.execute(sql, (id,))
        conn.commit()
        return cursor.rowcount > 0  # Retorna True se algum produto foi excluído


if __name__ == "__main__":
    conn = None
    try:
        while True:
            print("\n=== Sistema de Estoque ===")
            print("1. Inserir Produto")
            print("2. Listar Produtos")
            print("3. Excluir Produto")
            print("0. Sair")

            opcao = input("\nEscolha uma opção: ")

            if opcao == "1":
                nome = input("Nome do produto: ")
                preco = float(input("Preço: "))
                validade = input("Validade (DD/MM/AAAA)")
                try:
                    inserir_produto(nome, preco, validade)
                    print("✅ Produto inserido com sucesso!")
                except Exception as e:
                    print(f"❌ Erro ao inserir produto: {str(e)}")

            elif opcao == "2":
                try:
                    produtos = listar_produtos()
                    if produtos:
                        print("\nProdutos cadastrados:")
                        for p in produtos:
                            print(f"ID: {p[0]}, Nome: {p[1]}, Preço: R${p[2]:.2f}, Validade: {p[3]}")
                    else:
                        print("Não há produtos cadastrados.")
                except Exception as e:
                    print(f"❌ Erro ao listar produtos: {str(e)}")

            elif opcao == "3":
                try:
                    produtos = listar_produtos()
                    if produtos:
                        print("\nProdutos disponíveis para exclusão:")
                        for p in produtos:
                            print(f"ID: {p[0]}, Nome: {p[1]}, Preço: R${p[2]:.2f}, Validade: {p[3]}")

                        id_excluir = int(input("\nDigite o ID do produto que deseja excluir: "))
                        if excluir_produto(id_excluir):
                            print("✅ Produto excluído com sucesso!")
                        else:
                            print("❌ Produto não encontrado.")
                    else:
                        print("Não há produtos cadastrados para excluir.")
                except ValueError:
                    print("❌ Por favor, digite um ID válido (número inteiro).")
                except Exception as e:
                    print(f"❌ Erro ao excluir produto: {str(e)}")

            elif opcao == "0":
                print("Saindo do sistema...")
                break

            else:
                print("❌ Opção inválida. Por favor, tente novamente.")

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
