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
  "email" varchar(255) NOT NULL,
  "phone_number" varchar(20) NOT NULL,
  "password_hash" varchar(255) NOT NULL,
  "created_at" timestamp NOT NULL DEFAULT (now()),
  "status" varchar(20) NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE "addresses" (
  "id" uuid PRIMARY KEY,
  "user_id" varchar(11) NOT NULL
);

ALTER TABLE "addresses" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY IMMEDIATE;
