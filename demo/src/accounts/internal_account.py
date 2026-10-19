from connection.connection import Connection
from contextlib import AbstractContextManager
from domain_types import AccountNumber

INTERNAL_BANK_ACCOUNT_NUMBER: AccountNumber = AccountNumber("00000000000000000000000099")

def check_if_internal_account_exist(conn: AbstractContextManager) -> bool:
    exist = conn.execute(f"""SELECT EXISTS (SELECT 1 FROM accounts 
    WHERE account_type = 'INTERNAL');""").fetchone()[0]
    return exist

def create_inernal_bank_account() -> None:
    SQL="""INSERT INTO accounts (id, user_id, currency_code, account_number, account_type)
    VALUES (gen_random_uuid(), NULL, 'PLN', %(internal_account_number)s, 'INTERNAL')
    RETURNING id;"""
    try:
        with Connection() as conn:
            if check_if_internal_account_exist(conn):
                print ("Internal account exist")
                return None
            cur = conn.execute(SQL, {"internal_account_number": INTERNAL_BANK_ACCOUNT_NUMBER.value()})
        if cur.rowcount!=1:
            print("Inernal account was not created")
            return
        print("Internal account created")

    except Exception as e:
        print("Error: internal account was not created!", e)

        