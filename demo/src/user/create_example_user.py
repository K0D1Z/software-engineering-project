from connection.connection import Connection
from contextlib import AbstractContextManager

def check_if_user_exist(conn: AbstractContextManager, pesel: str) -> bool:
    exist = conn.execute("""SELECT EXISTS (SELECT 1 FROM users
    WHERE pesel = %s);""", (pesel,)).fetchone()[0]
    return exist
    

def create_user(pesel: str, firs_name: str, last_name:str, email:str) -> None:
    SQL="""WITH new_user AS (
        INSERT INTO users (id, pesel, first_name, last_name, email, phone_number, password_hash)
        VALUES (
            gen_random_uuid(),
            %(pesel)s,
            %(first_name)s,
            %(last_name)s,
            %(email)s,
            '000000000',              
            'PLACEHOLDER_HASH'
        )
        RETURNING id
        )
        INSERT INTO addresses (id, user_id, street, building_number, apartment_number, postal_code, city)
        SELECT gen_random_uuid(), id,
            'ul. Przykładowa',      
            '1',                  
            NULL,                  
            '00-000',               
            'Test'             
        FROM new_user
        RETURNING user_id;"""

    
    try:
        with Connection() as conn:
            if check_if_user_exist(conn, pesel):
                print ("User with this pesel already exists!")
                return None
            cur = conn.execute(SQL, {
            "first_name": firs_name,
            "last_name": last_name,
            "pesel": pesel,
            "email": email,
            })
        print("Example user created")
    except Exception as e:
        print("Error: user was not created!", e)
