from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from domain_types import *



@dataclass(field=True)
class User():
    conn: AbstractContextManager
    client_number: int = field(init=False)

    def __post_init__(self): #TODO dodaj tworzenie numeru
        if not (isinstance(self.client_number, int) and len(self.client_number)==10):
            raise ValueError("Incorrect client number")

    def check_if_user_exist(self, pesel: str) -> bool:
        SQL="""SELECT EXISTS (SELECT 1 FROM users
        WHERE pesel = %s);"""

        exist = self.conn.execute(SQL, (pesel,)).fetchone()[0]
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
            cur = self.conn.execute(SQL, {
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
            print("Example user created")

        except Exception as e: #TODO rozwiń
            print("Error: user was not created!", e)

    
