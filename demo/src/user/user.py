from dataclasses import dataclass, field
from connection import Connection
import psycopg
from domain_types import *



@dataclass(frozen=True)
class User():
    def check_if_user_exist(self, pesel: str) -> bool:
        SQL="""SELECT EXISTS (SELECT 1 FROM users
        WHERE pesel = %s);"""
        with Connection() as conn:
            exist = conn.execute(SQL, (pesel,)).fetchone()[0]
        return exist

    def create(self, pesel: Pesel, first_name: Name, last_name: Name, email: Email, phone_number: Phone ,password: Password, adress_type: AddressType | None,
               street: Street | None, building_number : AddressNumber, apartment_number : AddressNumber | None, postal_code : PostalCode,
               city: City, country: CountryCode):
        SQL="""WITH new_user AS (
                INSERT INTO users (id, pesel, first_name, last_name, email, phone_number, password_hash)
                VALUES (
                    gen_random_uuid(),
                    %(pesel)s,
                    %(first_name)s,
                    %(last_name)s,
                    %(email)s,
                    %(phone_number)s,              
                    %(password_hash)s
                )
                RETURNING id
                )
                INSERT INTO addresses (id, user_id, street, building_number, apartment_number, postal_code, city)
                SELECT gen_random_uuid(), id,
                    %(adress_type)s
                    %(street)s,      
                    %(building_number)s,                  
                    %(apartment_number)s                  
                    %(postal_code)s,               
                    %(city)s,
                    %(country)s             
                FROM new_user
                RETURNING user_id;"""
        
        try:
            if self.check_if_user_exist(pesel):
                print ("User with this pesel already exists!")
                return None
            with Connection() as conn:
                cur = conn.execute(SQL, {
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

            if cur.rowcount != 1:
                print("User was not created!")
            print("User created")

        except psycopg.errors.UniqueViolation as e:
            print("User was not created: value already in use:", e.diag.constraint_name)
        except psycopg.errors.CheckViolation as e:
            print("User was not created: value rejected by constraint:", e.diag.constraint_name)
        except psycopg.errors.NotNullViolation as e:
            print("User was not created: missing required value:", e.diag.column_name)
        except psycopg.errors.ForeignKeyViolation as e:
            print("User was not created: referenced record not found:", e.diag.constraint_name)
        except psycopg.errors.DataError as e:
            print("User was not created: invalid data format:", e.diag.message_primary)
        except psycopg.errors.SyntaxError as e:
            print("User was not created: SQL syntax error:", e.diag.message_primary)
        except psycopg.Error as e:
            print("User was not created: database error:", e)
        except ValueError as e:
            print("User was not created: invalid input:", e)
        except AttributeError as e:
            print("User was not created: missing or malformed field:", e)
        except ConnectionError as e:
            print("User was not created: connection error:", e)

    
