from connection.connection import Connection
from contextlib import AbstractContextManager



def create_customer_account(pesel: str, number: str) -> None:
    SQL="""
        INSERT INTO accounts (id, user_id, currency_code, account_number, account_type)
        SELECT gen_random_uuid(), u.id, %(currency)s, %(account_number)s, 'CUSTOMER'
        FROM users u
        WHERE u.pesel = %(pesel)s 
        AND u.status = 'ACTIVE'
        RETURNING id, account_number, currency_code, balance, status;
        """
    try:
        with Connection() as conn:
            cur = conn.execute(SQL, {
            "pesel": pesel,
            "currency": "PLN",
            "account_number": number,
        })
        print("Internal account created")
    except Exception as e:
        print("Error: internal account was not created!", e)

        