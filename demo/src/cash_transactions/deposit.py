from transfer.transfer import Transfer
from dataclasses import dataclass
from domain_types import AccountNumber, MoneyAmount
from accounts.internal_account import INTERNAL_BANK_ACCOUNT_NUMBER

@dataclass(frozen=True)
class Deposit():
    account_number: AccountNumber
    ammount: MoneyAmount
    verbose: bool = False

    def execute(self) -> bool:
        return Transfer(INTERNAL_BANK_ACCOUNT_NUMBER, self.account_number, self.ammount, verbose=self.verbose).execute()