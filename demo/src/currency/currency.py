import psycopg
from dataclasses import dataclass, field
from domain_types import CurrencyCode, Name, CurrencySymbol
from connection.connection import Connection

@dataclass(frozen=True)
class Currency():
    code: CurrencyCode
    verbose: bool = False

    def _log(self, *args):
        if self.verbose:
            print(*args)

    def add(self, name: Name, symbol: CurrencySymbol):
        SQL="""INSERT INTO currencies (code, name, symbol)
            VALUES (%(code)s, %(name)s, %(symbol)s)
            ON CONFLICT (code) DO NOTHING
            RETURNING code;"""
        try:
            with Connection() as conn:
                cur = conn.execute(SQL, {"code": self.code.value(), "name": name.value(), "symbol": symbol.value()})
                row = cur.fetchone()
                if row is None:
                    self._log("Currency was not created (already exists?)")
                    return
            self._log("Currency was created")
        except psycopg.errors.CheckViolation as e:
            self._log("Currency was not created: value rejected by constraint:", e.diag.constraint_name)
        except psycopg.errors.NotNullViolation as e:
            self._log("Currency was not created: missing required value:", e.diag.column_name)
        except psycopg.errors.DataError as e:
            self._log("Currency was not created: invalid data format:", e.diag.message_primary)
        except psycopg.Error as e:
            self._log("Currency was not created: database error:", e)
        except ConnectionError as e:
            self._log("Currency was not created: connection error:", e)
        except Exception as e:
            self._log("Unkown error:", e)


    #def set_exchange_rate(self) TODO