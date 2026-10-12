CREATE TABLE "currencies" (
  "code" varchar(3) PRIMARY KEY,
  "name" varchar(50) NOT NULL,
  "symbol" varchar(5) NOT NULL
);

CREATE TABLE "users" (
  "id" uuid PRIMARY KEY,
  "pesel" varchar(11) UNIQUE NOT NULL,
  "first_name" varchar(100) NOT NULL,
  "last_name" varchar(100) NOT NULL,
  "email" varchar(255) UNIQUE NOT NULL,
  "phone_number" varchar(20) NOT NULL,
  "password_hash" varchar(255) NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "status" varchar(20) NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE "addresses" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "address_type" varchar(20) NOT NULL DEFAULT 'RESIDENTIAL',
  "street" varchar(150) NOT NULL,
  "building_number" varchar(15) NOT NULL,
  "apartment_number" varchar(15),
  "postal_code" varchar(10) NOT NULL,
  "city" varchar(100) NOT NULL,
  "country" varchar(2) NOT NULL DEFAULT 'PL',
  "created_at" timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE "accounts" (
  "id" uuid PRIMARY KEY,
  "user_id" uuid NOT NULL,
  "currency_code" varchar(3) NOT NULL,
  "account_number" varchar(34) UNIQUE NOT NULL,
  "account_type" varchar(20) NOT NULL,
  "status" varchar(20) NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE "transactions" (
  "id" uuid PRIMARY KEY,
  "reference_number" varchar(64) UNIQUE NOT NULL,
  "description" text NOT NULL,
  "status" varchar(20) NOT NULL DEFAULT 'POSTED',
  "executed_at" timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE "ledger" (
  "id" uuid PRIMARY KEY,
  "transaction_id" uuid NOT NULL,
  "account_id" uuid NOT NULL,
  "entry_type" varchar(6) NOT NULL,
  "amount" numeric(18,4) NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE "exchange_rates" (
  "id" bigserial PRIMARY KEY,
  "base_currency" varchar(3) NOT NULL,
  "target_currency" varchar(3) NOT NULL,
  "rate" numeric(12,6) NOT NULL,
  "rate_timestamp" timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE "scheduled_transactions" (
  "id" uuid PRIMARY KEY,
  "source_account_id" uuid NOT NULL,
  "target_account_id" uuid NOT NULL,
  "currency" varchar(3) NOT NULL,
  "amount" numeric(18,4) NOT NULL,
  "status" varchar(20) NOT NULL DEFAULT 'ACTIVE',
  "created_at" timestamp NOT NULL DEFAULT (now())
);

ALTER TABLE "addresses" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "accounts" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "accounts" ADD FOREIGN KEY ("currency_code") REFERENCES "currencies" ("code") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "ledger" ADD FOREIGN KEY ("transaction_id") REFERENCES "transactions" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "ledger" ADD FOREIGN KEY ("account_id") REFERENCES "accounts" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "exchange_rates" ADD FOREIGN KEY ("base_currency") REFERENCES "currencies" ("code") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "exchange_rates" ADD FOREIGN KEY ("target_currency") REFERENCES "currencies" ("code") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "scheduled_transactions" ADD FOREIGN KEY ("source_account_id") REFERENCES "accounts" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "scheduled_transactions" ADD FOREIGN KEY ("target_account_id") REFERENCES "accounts" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "scheduled_transactions" ADD FOREIGN KEY ("currency") REFERENCES "currencies" ("code") DEFERRABLE INITIALLY IMMEDIATE;
