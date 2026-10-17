from connection.connection import Connection
from contextlib import AbstractContextManager

def check_if_internal_account_exist(conn: AbstractContextManager) -> bool:
    exist = conn.execute(f"""SELECT EXISTS (SELECT 1 FROM accounts 
    WHERE account_type = 'INTERNAL');""").fetchone()[0]
    return exist
    

def create_inernal_bank_account() -> None:
    try:
        with Connection() as conn:
            if check_if_internal_account_exist(conn):
                print ("Internal account exist")
                return None
            conn.execute("""INSERT INTO currencies (code, name, symbol)
            VALUES ('PLN', 'Polski złoty', 'zł')
            ON CONFLICT (code) DO NOTHING;""")
            cur = conn.execute("""INSERT INTO accounts (id, user_id, currency_code, account_number, account_type)
            VALUES (gen_random_uuid(), NULL, 'PLN', '00000000000000000000000099', 'INTERNAL')
            RETURNING id;""")
        print("Internal account created")
    except Exception as e:
        print("Error: internal account was not created!", e)

        