CREATE TABLE "currencies" (
  "code" varchar(3) PRIMARY KEY,
  "name" varchar(100) NOT NULL,
  "symbol" varchar(5) NOT NULL,
  CONSTRAINT chk_currency_code CHECK ("code" ~ '^[A-Z]{3}$')
);

CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "client_number" varchar(8) UNIQUE NOT NULL,
  "pesel" varchar(11) UNIQUE NOT NULL,
  "first_name" varchar(100) NOT NULL,
  "last_name" varchar(100) NOT NULL,
  "email" varchar(255) UNIQUE NOT NULL,
  "phone_number" varchar(20) NOT NULL,
  "password_hash" varchar(255) NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "status" varchar(20) NOT NULL DEFAULT 'ACTIVE',
  CONSTRAINT chk_user_status CHECK ("status" IN ('ACTIVE','DELETED', 'PENDING', 'BLOCKED')),
  CONSTRAINT chk_pesel CHECK ("pesel" ~ '^[0-9]{11}$')
);

CREATE TABLE "addresses" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "address_type" varchar(20) NOT NULL DEFAULT 'RESIDENTIAL',
  "street" varchar(150) NOT NULL,
  "building_number" varchar(15) NOT NULL,
  "apartment_number" varchar(15),
  "postal_code" varchar(10),
  "city" varchar(100) NOT NULL,
  "country" varchar(2) NOT NULL DEFAULT 'PL',
  "created_at" timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT chk_postal_code_pl CHECK ("country" <> 'PL' OR "postal_code" ~ '^[0-9]{2}-[0-9]{3}$'),
  CONSTRAINT chk_address_type CHECK ("address_type" IN ('RESIDENTIAL', 'CORRESPONDENCE'))
);

CREATE TABLE "accounts" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid,
  "balance" numeric(18,4) NOT NULL DEFAULT 0,  
  "currency_code" varchar(3) NOT NULL,
  "account_number" varchar(34) UNIQUE NOT NULL,
  "account_type" varchar(20) NOT NULL DEFAULT 'CUSTOMER',
  "status" varchar(20) NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT uq_accounts_id_currency UNIQUE ("id", "currency_code"),
  CONSTRAINT chk_account_type CHECK ("account_type" IN ('CUSTOMER' ,'INTERNAL')),
  CONSTRAINT chk_account_status CHECK ("status" IN ('ACTIVE','CLOSED', 'FROZEN')),
  CONSTRAINT chk_account_owner CHECK (
    ("account_type" = 'INTERNAL' AND "user_id" IS NULL) OR
    ("account_type" <> 'INTERNAL' AND "user_id" IS NOT NULL)
  ),
  CONSTRAINT chk_balance CHECK ("account_type" = 'INTERNAL' OR "balance" >= 0)
);

CREATE TABLE "transactions" (
  "id" uuid PRIMARY KEY,
  "reference_number" varchar(64) UNIQUE NOT NULL,
  "description" text NOT NULL,
  "status" varchar(20) NOT NULL DEFAULT 'POSTED',
  "executed_at" timestamp NOT NULL DEFAULT (now()),
  "reverses_transaction_id" uuid,
  "scheduled_transaction_id" uuid,
  CONSTRAINT chk_no_self_reverse CHECK ("reverses_transaction_id" <> "id"),
  CONSTRAINT uq_tx_reversed_once UNIQUE ("reverses_transaction_id"),
  CONSTRAINT chk_tx_status CHECK ("status" IN ('PENDING','POSTED','REVERSED', 'REJECTED'))
);

CREATE TABLE "ledger" (
  "id" uuid PRIMARY KEY,
  "transaction_id" uuid NOT NULL,
  "account_id" uuid NOT NULL,
  "entry_type" varchar(6) NOT NULL,
  "amount" numeric(18,4) NOT NULL,
  "currency_code" varchar(3) NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT chk_entry_type CHECK ("entry_type" IN ('DEBIT','CREDIT')),
  CONSTRAINT chk_amount_positive CHECK ("amount" > 0)
);

CREATE TABLE "exchange_rates" (
  "id" bigserial PRIMARY KEY,
  "base_currency" varchar(3) NOT NULL,
  "target_currency" varchar(3) NOT NULL,
  "rate" numeric(12,6) NOT NULL,
  "rate_timestamp" timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT chk_rate_positive CHECK ("rate" > 0),
  CONSTRAINT chk_rate_currencies CHECK ("base_currency" <> "target_currency")  
);

CREATE TABLE "scheduled_transactions" (
  "id" uuid PRIMARY KEY,
  "source_account_id" uuid NOT NULL,
  "target_account_id" uuid NOT NULL,
  "currency" varchar(3) NOT NULL,
  "amount" numeric(18,4) NOT NULL,
  "description" text NOT NULL,
  "status" varchar(20) NOT NULL DEFAULT 'ACTIVE',
  "cron_expression" varchar(50) NOT NULL,
  "next_run_at" timestamp NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  CONSTRAINT chk_sched_amount CHECK ("amount" > 0),
  CONSTRAINT chk_sched_accounts CHECK ("source_account_id" <> "target_account_id"),
  CONSTRAINT chk_sched_status CHECK ("status" IN ('ACTIVE','CANCELLED'))
);

ALTER TABLE "addresses" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "accounts" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "accounts" ADD FOREIGN KEY ("currency_code") REFERENCES "currencies" ("code") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "ledger" ADD FOREIGN KEY ("transaction_id") REFERENCES "transactions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "ledger" ADD FOREIGN KEY ("account_id", "currency_code") REFERENCES "accounts" ("id", "currency_code") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "exchange_rates" ADD FOREIGN KEY ("base_currency") REFERENCES "currencies" ("code") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "exchange_rates" ADD FOREIGN KEY ("target_currency") REFERENCES "currencies" ("code") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "transactions" ADD FOREIGN KEY ("reverses_transaction_id") REFERENCES "transactions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "scheduled_transactions" ADD FOREIGN KEY ("source_account_id") REFERENCES "accounts" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "scheduled_transactions" ADD FOREIGN KEY ("target_account_id") REFERENCES "accounts" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "scheduled_transactions" ADD FOREIGN KEY ("currency") REFERENCES "currencies" ("code") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "transactions" ADD FOREIGN KEY ("scheduled_transaction_id") REFERENCES "scheduled_transactions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

CREATE INDEX idx_ledger_account ON ledger (account_id, created_at);
CREATE INDEX idx_ledger_transaction ON ledger (transaction_id);
CREATE INDEX idx_accounts_user ON accounts (user_id);
CREATE INDEX idx_addresses_user ON addresses (user_id);
CREATE INDEX idx_rates_lookup ON exchange_rates (base_currency, target_currency, rate_timestamp DESC);

CREATE OR REPLACE FUNCTION check_transaction_balanced() RETURNS trigger AS $$
DECLARE
  bad record;
BEGIN
  SELECT currency_code,
         SUM(CASE entry_type WHEN 'DEBIT' THEN amount ELSE -amount END) AS diff
    INTO bad
    FROM ledger
   WHERE transaction_id = NEW.transaction_id
   GROUP BY currency_code
  HAVING SUM(CASE entry_type WHEN 'DEBIT' THEN amount ELSE -amount END) <> 0
   LIMIT 1;

  IF FOUND THEN
    RAISE EXCEPTION 'Transaction % not balanced in % (diff = %)',
                    NEW.transaction_id, bad.currency_code, bad.diff;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER trg_ledger_balanced
  AFTER INSERT ON ledger
  DEFERRABLE INITIALLY DEFERRED
  FOR EACH ROW EXECUTE FUNCTION check_transaction_balanced();


CREATE FUNCTION ledger_immutable() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'ledger is append-only; use a reversing transaction';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ledger_no_change
  BEFORE UPDATE OR DELETE ON ledger
  FOR EACH ROW EXECUTE FUNCTION ledger_immutable();


CREATE FUNCTION ledger_apply_to_balance() RETURNS trigger AS $$
BEGIN
  UPDATE accounts
     SET balance = balance + CASE NEW.entry_type
                               WHEN 'CREDIT' THEN NEW.amount
                               ELSE -NEW.amount END
   WHERE id = NEW.account_id;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_ledger_apply_balance
  AFTER INSERT ON ledger
  FOR EACH ROW EXECUTE FUNCTION ledger_apply_to_balance();

CREATE FUNCTION accounts_balance_guard() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'INSERT' AND NEW.balance <> 0 THEN
    RAISE EXCEPTION 'new account must start with balance 0';
  END IF;
  IF TG_OP = 'UPDATE'
     AND NEW.balance IS DISTINCT FROM OLD.balance
     AND pg_trigger_depth() < 2 THEN
    RAISE EXCEPTION 'balance can only be changed through the ledger';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_accounts_balance_guard
  BEFORE INSERT OR UPDATE ON accounts
  FOR EACH ROW EXECUTE FUNCTION accounts_balance_guard();
