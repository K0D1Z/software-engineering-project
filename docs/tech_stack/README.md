# TECH STACK

## Backend - Python (FastAPI and SQLAlchemy probably???)
### Industry context
- Java Spring Boot and C# .NET are the dominant technologies in the banking sector (Spring Boot has been widely used in core banking systems for decades
given its support for transactions `@Transactional(isolation = ...)` and pessimistic locks `@Lock(LockModeType.PESSIMISTIC_WRITE)`)
- Given the project’s basic level of complexity, our proficiency in Python language and lack of experience in Java and C#,
we decided to prepare a demonstration version using Python.
### Justification
- The team possesses a decent level of proficiency in Python. Choosing this environment minimizes the risk of implementation
errors and allows to focus on domain logic (double-entry bookkeeping, ledger).
- Through integration with Pydantic and the standard `Decimal` type, the backend ensures strict validation of incoming JSON payloads at the system boundaries, eliminating the risk of floating-point rounding errors in financial operations.

## Database - PostgreSQL 16 or PostgreSQL 17
### Justification
- Native support for arbitrary-precision numeric types—specifically `numeric(18, 4)` for monetary amounts and `numeric(12, 6)` for exchange rates—eliminates currency rounding errors.
- PostgreSQL offers advanced concurrency control mechanisms (MVCC) and row-level locking (SELECT ... FOR UPDATE) for handling concurrent requests that affect an account.
- The PostgreSQL relational database is the standard for transactional and accounting systems. It guarantees the atomicity of multi-stage banking operations (e.g. the simultaneous creation of a transaction record and balanced entries in the general ledger).
- Defined foreign keys, UNIQUE and CHECK constraints ensure data consistency at the database engine level.

## Frontend - React.js + TypeScript (SPA)
### Justification
- Single Page Application (SPA) architecture ensures the separation of the presentation layer from the application's business logic. The frontend layer communicates with the backend exclusively through a defined REST API, utilizing the JSON data format.
- React library enables building reusable components (account cards, forms for validating IBAN formats, transaction history tables).
- Static typing in TypeScript ensures contracts for data structures transmitted from the backend (using interfaces that correspond to Pydantic or database models); it eliminates errors at the client–server interface.
- Taking into account the complexity of the project and its focus on architecture design, the frontend primarily serves to demonstrate how the architecture functions, which does not require a high level of complexity in the visual layer (e.g. using complex frameworks such as Angular).

## Background Tasks: TODO
### Justification