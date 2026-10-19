import psycopg
import psycopg
from connection.connection import Connection
from dataclasses import dataclass, field
from domain_types import AccountNumber, ClientNumber, CurrencyCode
import secrets

ACCOUNT_NUMBER_LENGTH = 26
MAX_NUMBER_ATTEMPTS = 10

@dataclass(slots=True)
class Account():
    client_number: ClientNumber
    account_number: AccountNumber | None = field(default=None)

    def _choose_account_number(self, conn) -> AccountNumber:
        """Draw random account numbers until one is not used in the database."""
        for _ in range(MAX_NUMBER_ATTEMPTS):
            candidate = str(secrets.randbelow(10 ** ACCOUNT_NUMBER_LENGTH)).zfill(ACCOUNT_NUMBER_LENGTH)
            taken = conn.execute(
                "SELECT EXISTS (SELECT 1 FROM accounts WHERE account_number = %(number)s);",
                {"number": candidate},
            ).fetchone()[0]
            if not taken:
                return AccountNumber(candidate)
        raise RuntimeError("Could not find a free account number")

    def create(self, currency: CurrencyCode) -> AccountNumber:
        SQL="""INSERT INTO accounts (id, user_id, currency_code, account_number, account_type)
            SELECT gen_random_uuid(), u.id, %(currency)s, %(account_number)s, 'CUSTOMER'
            FROM users u
            WHERE u.client_number = %(client_number)s
            RETURNING account_number;"""
        try:
            with Connection() as conn:
                self.account_number = self._choose_account_number(conn)
                cur = conn.execute(SQL, {
                    "currency": currency.value(),
                    "client_number": self.client_number.value(),
                    "account_number": self.account_number.value()
                })
                row = cur.fetchone()
            if row is None:
                print("Account was not created: client not found")
                return None
            print("Account created:", self.account_number.value())
            return self.account_number
        except psycopg.errors.ForeignKeyViolation as e:
            print("Account was not created: referenced record not found:", e.diag.constraint_name)
        except psycopg.errors.UniqueViolation as e:
            print("Account was not created: value already in use:", e.diag.constraint_name)
        except psycopg.errors.CheckViolation as e:
            print("Account was not created: value rejected by constraint:", e.diag.constraint_name)
        except psycopg.errors.NotNullViolation as e:
            print("Account was not created: missing required value:", e.diag.column_name)
        except psycopg.errors.DataError as e:
            print("Account was not created: invalid data format:", e.diag.message_primary)
        except psycopg.Error as e:
            print("Account was not created: database error:", e)
        except ConnectionError as e:
            print("Account was not created: connection error:", e)

    #close(self, ) TODO
