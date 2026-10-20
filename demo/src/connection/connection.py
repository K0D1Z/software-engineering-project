import os
import sys
import psycopg
from dotenv import load_dotenv
from dataclasses import dataclass, field

@dataclass(slots=True)
class Connection():
    verbose: bool = True
    url: str = field(init=False)
    inner: psycopg.Connection | None = field(init=False, default=None)

    def __post_init__(self):
        load_dotenv()                                  
        self.url = os.environ["DATABASE_URL"]

    def __enter__(self):
        inner=psycopg.connect(self.url)
        conn=inner.__enter__()
        try: 
            _ = conn.execute("SELECT version()")
        except BaseException:
            inner.__exit__(*sys.exc_info())
            raise ConnectionError("Connection not established!")
        self.inner=inner
        if self.verbose:
            print("Connection established!")
        return conn
            

    def __exit__(self, exc_type, exc, tb):
        try: 
            return self.inner.__exit__(exc_type, exc, tb)
        finally:
            if self.verbose:
                print("Connection closed!")
            self.inner=None


