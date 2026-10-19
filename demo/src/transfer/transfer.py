from connection.connection import Connection
import psycopg
from dataclasses import dataclass
from domain_types import AccountNumber, MoneyAmount
from uuid import uuid4

@dataclass(slots=True)
class Transfer():
    acount_number_source: AccountNumber
    acount_number_target: AccountNumber
    amount: MoneyAmount

    def execute(self):
        #TODO check is active
        SQL: str = """
        WITH tx AS (
        INSERT INTO transactions (id, reference_number, description)
        VALUES (gen_random_uuid(), %(ref)s, 'Transfer')
        RETURNING id
        )
        INSERT INTO ledger (id, transaction_id, account_id, entry_type, amount, currency_code)
        SELECT gen_random_uuid(), tx.id, a.id, v.entry_type, %(amount)s::numeric, a.currency_code
        FROM tx
        JOIN (VALUES (%(src)s::text, 'DEBIT'), (%(dst)s::text, 'CREDIT')) AS v(account_number, entry_type) ON true
        JOIN accounts a ON a.account_number = v.account_number
        ORDER BY a.id
        """
        
        try:
            with Connection() as conn:
                cur = conn.execute(SQL, {"ref": f"TRF-{uuid4()}", "amount": self.amount.value(), 
                                        "src": self.acount_number_source.value(), 
                                        "dst": self.acount_number_target.value()})            
                if cur.rowcount != 2:
                    raise ValueError("Source or target account not found")
            print("Transfer finished successfully!")
        except psycopg.errors.CheckViolation:
            print("Insufficient funds")
        except psycopg.errors.UniqueViolation:
            print("Reference number already exists")
        except psycopg.errors.RaiseException as e:
            print("Rejected by the database:", e.diag.message_primary)
        except psycopg.Error as e:
            print("Database error:", e)
        except ValueError as e:
            print("Invalid transfer:", e)
        except ConnectionError as e:
            print("Connection error:", e)