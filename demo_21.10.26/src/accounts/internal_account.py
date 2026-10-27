from connection.connection import Connection
from contextlib import AbstractContextManager
from domain_types import AccountNumber

INTERNAL_BANK_ACCOUNT_NUMBER: AccountNumber = AccountNumber("00000000000000000000000099")

def check_if_internal_account_exist(conn: AbstractContextManager) -> bool:
    exist = conn.execute(f"""SELECT EXISTS (SELECT 1 FROM accounts 
    WHERE account_type = 'INTERNAL');""").fetchone()[0]
    return exist

def create_inernal_bank_account(verbose: bool = False) -> None:
    def _log(*args):
        if verbose:
            print(*args)

    SQL="""INSERT INTO accounts (id, user_id, currency_code, account_number, account_type)
    VALUES (gen_random_uuid(), NULL, 'PLN', %(internal_account_number)s, 'INTERNAL')
    RETURNING id;"""
    try:
        with Connection() as conn:
            if check_if_internal_account_exist(conn):
                _log("Internal account exist")
                return None
            cur = conn.execute(SQL, {"internal_account_number": INTERNAL_BANK_ACCOUNT_NUMBER.value()})
        if cur.rowcount!=1:
            _log("Inernal account was not created")
            return
        _log("Internal account created")

    except Exception as e:
        _log("Error: internal account was not created!", e)

        