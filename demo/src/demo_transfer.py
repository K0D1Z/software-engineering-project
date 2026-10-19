from transfer.transfer import Transfer
from user.user import create_user
from accounts.create_internal import create_inernal_bank_account
from accounts.account import create_customer_account
from decimal import Decimal

def main():
    create_inernal_bank_account()
    create_user("01234567890", "Jan", "Kowalski", "abc@test.com")
    create_user("11234567890", "Adam", "Nowak", "def@test.com")
    create_customer_account(pesel="01234567890", number="00000000000000000000000001")
    create_customer_account(pesel="11234567890", number="00000000000000000000000002")
    Transfer(acount_number_source="00000000000000000000000099", 
             acount_number_target="00000000000000000000000001",
             amount=Decimal(1000.00)).execute()
    Transfer(acount_number_source="00000000000000000000000001",
                 acount_number_target="00000000000000000000000002",
                 amount=Decimal(200.00)).execute()
    Transfer(acount_number_source="00000000000000000000000001",
                     acount_number_target="00000000000000000000000002",
                     amount=Decimal(100.00)).execute()
    Transfer(acount_number_source="00000000000000000000000001",
                     acount_number_target="00000000000000000000000002",
                     amount=Decimal(800.00)).execute()


if __name__=="__main__":
    main()