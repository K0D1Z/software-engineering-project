from transfer.transfer import Transfer
from dataclasses import dataclass
from domain_types import AccountNumber, MoneyAmount
from accounts.internal_account import INTERNAL_BANK_ACCOUNT_NUMBER

@dataclass(frozen=True)
class Deposit():
    account_number: AccountNumber
    ammount: MoneyAmount

    def execute(self):
        Transfer(INTERNAL_BANK_ACCOUNT_NUMBER, self.account_number, self.ammount).execute()