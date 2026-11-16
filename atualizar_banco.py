"""Atualiza um banco ANTIGO para a estrutura nova do tcc.sql.

Quando rodar: se você já tinha o banco criado antes e agora recebeu o
tcc.sql novo. (Banco novo, criado só com o tcc.sql, não precisa disto.)

Como usar (com o MySQL ligado, na pasta do projeto):
    python atualizar_banco.py

O que faz (pode rodar mais de uma vez, não apaga dado nenhum):
  1. cria turmas.id_login, que liga cada matrícula ao login do aluno;
  2. preenche id_login casando turmas.nome_aluno com aluno.nome;
  3. cria a chave estrangeira (apagar o login apaga a matrícula);
  4. cria os índices únicos de aluno.nome e turmas.ra_aluno — só se não
     houver repetidos; se houver, mostra quais são pra você corrigir.

Se as senhas ainda estiverem em texto puro, rode também:
    python migrar_senhas.py
"""
from app import conectar_banco


def tem_coluna(cursor, tabela, coluna):
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (tabela, coluna)
    )
    return cursor.fetchone()[0] > 0


def tem_constraint(cursor, tabela, nome):
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND CONSTRAINT_NAME = %s
        """,
        (tabela, nome)
    )
    return cursor.fetchone()[0] > 0


def tem_indice(cursor, tabela, nome):
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = %s
        """,
        (tabela, nome)
    )
    return cursor.fetchone()[0] > 0


def criar_unico(cursor, tabela, coluna, nome_indice):
    if tem_indice(cursor, tabela, nome_indice):
        print(f"  {tabela}.{coluna}: índice único já existe.")
        return

    cursor.execute(
        f"""
        SELECT `{coluna}`, COUNT(*) FROM `{tabela}`
        WHERE `{coluna}` IS NOT NULL
        GROUP BY `{coluna}` HAVING COUNT(*) > 1
        """
    )
    repetidos = cursor.fetchall()

    if repetidos:
        print(f"  {tabela}.{coluna}: NÃO criei o índice único, há valores repetidos:")
        for valor, qtd in repetidos:
            print(f"      '{valor}' aparece {qtd} vezes")
        print("      Corrija (apague ou renomeie os repetidos) e rode este script de novo.")
        return

    cursor.execute(f"ALTER TABLE `{tabela}` ADD UNIQUE KEY `{nome_indice}` (`{coluna}`)")
    print(f"  {tabela}.{coluna}: índice único criado.")


def main():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        print("1) Coluna turmas.id_login")
        if tem_coluna(cursor, "turmas", "id_login"):
            print("  já existe.")
        else:
            cursor.execute("ALTER TABLE `turmas` ADD COLUMN `id_login` INT NULL AFTER `id_aluno`")
            print("  criada.")

        print("2) Ligando matrículas aos logins (pelo nome)")
        cursor.execute(
            """
            UPDATE `turmas` t
            JOIN `aluno` a ON a.nome = t.nome_aluno
            SET t.id_login = a.id_aluno
            WHERE t.id_login IS NULL
            """
        )
        print(f"  {cursor.rowcount} matrícula(s) ligada(s).")
        conexao.commit()

        print("3) Chave estrangeira turmas.id_login -> aluno.id_aluno")
        if tem_constraint(cursor, "turmas", "fk_turmas_login"):
            print("  já existe.")
        else:
            cursor.execute(
                """
                ALTER TABLE `turmas`
                ADD CONSTRAINT `fk_turmas_login` FOREIGN KEY (`id_login`)
                REFERENCES `aluno` (`id_aluno`) ON DELETE CASCADE
                """
            )
            print("  criada.")

        print("4) Índices únicos")
        criar_unico(cursor, "aluno", "nome", "uq_aluno_nome")
        criar_unico(cursor, "turmas", "ra_aluno", "uq_turmas_ra")
        conexao.commit()

        print("\nSituação final")
        cursor.execute("SELECT COUNT(*) FROM `turmas` WHERE id_login IS NULL")
        sem_login = cursor.fetchone()[0]
        cursor.execute(
            """
            SELECT COUNT(*) FROM `aluno` a
            WHERE NOT EXISTS (SELECT 1 FROM `turmas` t WHERE t.id_login = a.id_aluno)
            """
        )
        sem_turma = cursor.fetchone()[0]
        print(f"  Matrículas sem login: {sem_login}  (normal nas de exemplo)")
        print(f"  Logins sem turma:     {sem_turma}")
        print("Pronto.")

    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    main()
