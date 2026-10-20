import secrets
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from accounts.account import Account
from accounts.internal_account import create_inernal_bank_account
from cash_transactions.deposit import Deposit
from connection.connection import Connection
from currency.currency import Currency
from domain_types import *
from transfer.transfer import Transfer
from user.user import User

_print_lock = threading.Lock()
_t0 = 0.0


def log(who: str, msg: str):
    with _print_lock:
        print(f"[{time.monotonic() - _t0:5.2f}s] {who:<4} {msg}")


def reset_clock():
    global _t0
    _t0 = time.monotonic()


def balance(account: AccountNumber) -> Decimal:
    with Connection() as conn:
        return conn.execute("SELECT balance FROM accounts WHERE account_number = %s",
                            (account.value(),)).fetchone()[0]


def random_pesel() -> Pesel:
    weights = (1, 3, 7, 9, 1, 3, 7, 9, 1, 3)
    digits = [int(d) for d in "990101" + str(secrets.randbelow(10 ** 4)).zfill(4)]
    check = (10 - sum(d * w for d, w in zip(digits, weights)) % 10) % 10
    return Pesel("".join(map(str, digits)) + str(check))


def setup_client() -> ClientNumber:
    tag = secrets.token_hex(4)
    return User().create(pesel=random_pesel(), first_name=Name("Jan"), last_name=Name("Testowy"),
        email=Email(f"concurrency-{tag}@example.com"), phone_number=Phone("111222333"),
        password=Password("123Qwe123#ABC"), adress_type=AddressType.RESIDENTIAL, street=Street("Kawiory"),
        building_number=AddressNumber("1"), apartment_number=AddressNumber("1"),
        postal_code=PostalCode("30-055"), city=City("Kraków"), country=CountryCode.PL)


def new_account(client: ClientNumber, initial: Decimal) -> AccountNumber:
    account = Account(client).create(CurrencyCode("PLN"))
    Deposit(account_number=account, ammount=MoneyAmount(initial)).execute()
    return account


def header(title: str):
    print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)


def scenario_lock_wait(client: ClientNumber):
    header("SCENARIO 1: two transfers of 800 PLN from a 1000 PLN account")
    src = new_account(client, Decimal("1000.00"))
    dst = new_account(client, Decimal("0.01"))
    print(f"Balance before: {balance(src)}")

    def t1():
        log("T1", "start: transfer 800, will hold row lock for 3 s before COMMIT")
        ok = Transfer(src, dst, MoneyAmount(Decimal("800.00")), hold_before_commit=3).execute()
        log("T1", "COMMIT - success" if ok else "rejected")
        return ok

    def t2():
        time.sleep(0.5)
        log("T2", "start: transfer 800 (T1 is still uncommitted) -> waiting for row lock...")
        ok = Transfer(src, dst, MoneyAmount(Decimal("800.00"))).execute()
        log("T2", "success" if ok else "rejected: insufficient funds (CHECK balance >= 0)")
        return ok

    reset_clock()
    with ThreadPoolExecutor() as pool:
        results = [f.result() for f in [pool.submit(t1), pool.submit(t2)]]

    final = balance(src)
    print(f"Balance after: {final}   successful transfers: {sum(results)}/2")
    assert final == Decimal("200.00") and results == [True, False]


def scenario_race(client: ClientNumber, threads: int = 10, amount: Decimal = Decimal("300.00")):
    initial = Decimal("1000.00")
    header(f"SCENARIO 2: {threads} threads x {amount} PLN at once from a {initial} PLN account")
    src = new_account(client, initial)
    dst = new_account(client, Decimal("0.01"))
    barrier = threading.Barrier(threads)

    def worker(i: int) -> bool:
        barrier.wait()
        log(f"T{i}", "start")
        ok = Transfer(src, dst, MoneyAmount(amount), hold_before_commit=0.3).execute()
        
        log(f"T{i}", "success" if ok else "rejected: insufficient funds")
        return ok

    reset_clock()
    with ThreadPoolExecutor(max_workers=threads) as pool:
        results = list(pool.map(worker, range(1, threads + 1)))

    final = balance(src)
    expected_ok = int(initial // amount)
    print(f"Balance after: {final}   successful: {sum(results)}/{threads} (expected {expected_ok})")
    assert final >= 0
    assert sum(results) == expected_ok
    assert final == initial - expected_ok * amount


def scenario_cross(client: ClientNumber, pairs: int = 10):
    header(f"SCENARIO 3: {pairs} x (A->B) and {pairs} x (B->A) simultaneously")
    a = new_account(client, Decimal("500.00"))
    b = new_account(client, Decimal("500.00"))
    total_before = balance(a) + balance(b)
    barrier = threading.Barrier(2 * pairs)

    def worker(i: int) -> bool:
        src, dst, name = (a, b, "A->B") if i % 2 == 0 else (b, a, "B->A")
        barrier.wait()
        ok = Transfer(src, dst, MoneyAmount(Decimal("10.00")), hold_before_commit=0.1).execute()
        log(f"T{i}", f"{name} " + ("success" if ok else "FAILED"))
        return ok

    reset_clock()
    with ThreadPoolExecutor(max_workers=2 * pairs) as pool:
        results = list(pool.map(worker, range(2 * pairs)))

    total_after = balance(a) + balance(b)
    print(f"A = {balance(a)}, B = {balance(b)}, A+B before = {total_before}, after = {total_after}")
    print(f"successful: {sum(results)}/{2 * pairs}, no deadlocks")
    assert all(results)
    assert total_before == total_after


def main():
    Currency(CurrencyCode("PLN")).add(Name("Polski złoty"), CurrencySymbol("zł"))
    create_inernal_bank_account()
    client = setup_client()

    scenario_lock_wait(client)
    scenario_race(client)
    scenario_cross(client)
    print("\nAll invariants held.")


if __name__ == "__main__":
    main()
