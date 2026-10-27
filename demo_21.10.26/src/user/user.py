from dataclasses import dataclass, field
from connection.connection import Connection
import psycopg
import secrets
from domain_types import *


CLIENT_NUMBER_LENGTH = 8
MAX_NUMBER_ATTEMPTS = 10

@dataclass(slots=True)
class User():
    client_number: ClientNumber = field(init=False)
    verbose: bool = False

    def _log(self, *args):
        if self.verbose:
            print(*args)

    def _check_if_user_exist(self, pesel: str, conn) -> bool:
        SQL="""SELECT EXISTS (SELECT 1 FROM users
        WHERE pesel = %s);"""
        exist = conn.execute(SQL, (pesel,)).fetchone()[0]
        return exist

    def _choose_client_number(self, conn) -> ClientNumber:
        """Draw random client numbers until one is not used in the database."""
        for _ in range(MAX_NUMBER_ATTEMPTS):
            candidate = str(secrets.randbelow(10 ** CLIENT_NUMBER_LENGTH)).zfill(CLIENT_NUMBER_LENGTH)
            taken = conn.execute(
                "SELECT EXISTS (SELECT 1 FROM users WHERE client_number = %(number)s);",
                {"number": candidate},
            ).fetchone()[0]
            if not taken:
                return ClientNumber(candidate)
        raise RuntimeError("Could not find a free client number")

    def create(self, pesel: Pesel, first_name: Name, last_name: Name, email: Email, phone_number: Phone ,password: Password, adress_type: AddressType | None,
               street: Street | None, building_number : AddressNumber, apartment_number : AddressNumber | None, postal_code : PostalCode,
               city: City, country: CountryCode) -> ClientNumber:
        SQL="""WITH new_user AS (
                INSERT INTO users (id, client_number, pesel, first_name, last_name, email, phone_number, password_hash)
                VALUES (
                    gen_random_uuid(),
                    %(client_number)s,
                    %(pesel)s,
                    %(first_name)s,
                    %(last_name)s,
                    %(email)s,
                    %(phone_number)s,              
                    %(password_hash)s
                )
                RETURNING id
                )
                INSERT INTO addresses (id, user_id, address_type, street, building_number, apartment_number, postal_code, city, country)
                SELECT gen_random_uuid(), id,
                    %(adress_type)s,
                    %(street)s,      
                    %(building_number)s,                  
                    %(apartment_number)s,               
                    %(postal_code)s,               
                    %(city)s,
                    %(country)s             
                FROM new_user
                RETURNING user_id;"""
        
        try:
            with Connection() as conn:
                if self._check_if_user_exist(pesel.value(), conn):
                    self._log("User with this pesel already exists!")
                    return None
                self.client_number=self._choose_client_number(conn)
                cur = conn.execute(SQL, {
                "client_number": self.client_number.value(),
                "first_name": first_name.value(),
                "last_name": last_name.value(),
                "pesel": pesel.value(),
                "email": email.value(),
                "phone_number": phone_number.value(),
                "password_hash": password.hash(),
                "adress_type": adress_type,
                "street": street.value(),
                "building_number": building_number.value(),
                "apartment_number": apartment_number.value(),
                "postal_code": postal_code.value(),
                "city": city.value(),
                "country": country,
                })
            row = cur.fetchone()
            if row is None:
                self._log("User was not created!")
                return
            self._log(f"User created: client_number {self.client_number.value()}")
            return self.client_number

        except psycopg.errors.UniqueViolation as e:
            self._log("User was not created: value already in use:", e.diag.constraint_name)
        except psycopg.errors.CheckViolation as e:
            self._log("User was not created: value rejected by constraint:", e.diag.constraint_name)
        except psycopg.errors.NotNullViolation as e:
            self._log("User was not created: missing required value:", e.diag.column_name)
        except psycopg.errors.ForeignKeyViolation as e:
            self._log("User was not created: referenced record not found:", e.diag.constraint_name)
        except psycopg.errors.DataError as e:
            self._log("User was not created: invalid data format:", e.diag.message_primary)
        except psycopg.errors.SyntaxError as e:
            self._log("User was not created: SQL syntax error:", e.diag.message_primary)
        except psycopg.Error as e:
            self._log("User was not created: database error:", e)
        except ValueError as e:
            self._log("User was not created: invalid input:", e)
        except AttributeError as e:
            self._log("User was not created: missing or malformed field:", e)
        except ConnectionError as e:
            self._log("User was not created: connection error:", e)
        except Exception as e:
            self._log("Unkown error:", e)

    #TODO getter numeru konta    
