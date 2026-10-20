from cash_transactions.deposit import Deposit
from transfer.transfer import Transfer
from user.user import User
from accounts.internal_account import create_inernal_bank_account, INTERNAL_BANK_ACCOUNT_NUMBER
from accounts.account import Account
from currency.currency import Currency
from domain_types import *
from decimal import Decimal

def main():
    try:
        Currency(CurrencyCode("PLN"), verbose=True).add(Name("Polski złoty"), CurrencySymbol("zł"))
        create_inernal_bank_account(verbose=True)

        client1_number = User(verbose=True).create(pesel=Pesel("02231512347"), first_name=Name("Andrzej"), last_name=Name("Nowak"),
        email=Email("andrzejtest@gmail.com"), phone_number=Phone("123456789"), password=Password("123Qwe123#ABC"),
        adress_type=AddressType.RESIDENTIAL, street=Street("Kawiory"), building_number=AddressNumber("21"),
        apartment_number=AddressNumber("5"), postal_code=PostalCode("30-255"), city=City("Kraków"),
        country=CountryCode.PL)
        
        client2_number = User(verbose=True).create(pesel=Pesel("99123100126"), first_name=Name("Filip"), last_name=Name("Kowalski"),
        email=Email("filiptest@gmail.com"), phone_number=Phone("987654321"), password=Password("Qwe123Qwe#ABC"),
        adress_type=AddressType.RESIDENTIAL, street=Street("Krowodrza"), building_number=AddressNumber("210"),
        apartment_number=AddressNumber("6"), postal_code=PostalCode("30-155"), city=City("Kraków"),
        country=CountryCode.PL)

        account1_number = Account(client1_number, verbose=True).create(CurrencyCode("PLN"))
        account2_number = Account(client2_number, verbose=True).create(CurrencyCode("PLN"))

        Deposit(account_number=account1_number, ammount=MoneyAmount(Decimal(1000.00)), verbose=True).execute()
        Transfer(account1_number, account2_number, MoneyAmount(Decimal(200.00)), verbose=True).execute()
        Transfer(account1_number, account2_number, MoneyAmount(Decimal(100.00)), verbose=True).execute()
        Transfer(account1_number, account2_number, MoneyAmount(Decimal(800.00)), verbose=True).execute() #Nie wykona się
        Transfer(account2_number, account1_number, MoneyAmount(Decimal(100.00)), verbose=True).execute()
        Transfer(account1_number, account2_number, MoneyAmount(Decimal(800.00)), verbose=True).execute()
    except ValueError as e:
        print(f"Incorect data: {e}")

if __name__=="__main__":
    main()