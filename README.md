# SecureBank – Banking Transaction Management System

A web-based banking transaction management application built using Django REST Framework and PostgreSQL. SecureBank allows authenticated users to manage their bank accounts and perform simulated banking transactions through a web interface backed by REST APIs.

## Project Overview

SecureBank demonstrates the development of a banking-style application with user authentication, account management, transaction processing, and transaction history. It uses JWT authentication to protect API endpoints and database transactions to help maintain consistent account balances during financial operations.

This project is designed as a practical demonstration of Python, Django REST Framework, REST API development, relational database integration, and backend testing.

## Features

### Authentication and Authorization
- JWT-based authentication using access and refresh tokens.
- Protected API endpoints for authenticated users.
- Account-level access restrictions so users can access only their own accounts and transaction history.

### Bank Account Management
- Retrieve the authenticated user's bank accounts.
- View account details and account balances.
- Support account status checks, including active and inactive accounts.

### Banking Transactions
- **Deposit:** Add funds to an eligible account.
- **Withdrawal:** Withdraw funds when sufficient balance is available.
- **Fund Transfer:** Transfer funds between eligible accounts.
- **Transaction History:** View transactions associated with an account.
- **Mini Statement:** Review transaction records through the frontend.
- **Transaction Search and Filtering:** Find relevant transaction records using the available dashboard controls.

### Transaction Integrity
- Database transactions using Django's `transaction.atomic()`.
- Row-level locking using `select_for_update()` for transaction operations.
- Validation of account ownership, account status, and available balance.
- Separate `DEBITED` and `CREDITED` transaction records for the sender and receiver during a successful transfer.

### Frontend
- Responsive web interface built with HTML, CSS, Bootstrap, and JavaScript.
- Login page and banking dashboard.
- Account balance and transaction displays.
- Deposit, withdrawal, and transfer forms.
- Transaction history with pagination and print support.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Django |
| REST API Framework | Django REST Framework |
| Authentication | JWT using Simple JWT |
| Database | PostgreSQL |
| Database Adapter | psycopg |
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| API Testing | Django automated tests; Postman can be used for manual API testing |
| Development Tools | Visual Studio Code, pgAdmin |

## Project Structure

The project is organized around a Django backend, a banking application, and frontend files. Your exact filenames and folders may differ depending on your final project structure.

```text
banking_project/
├── manage.py
├── banking_project/
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── banking/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── ...
├── templates/          # If used in your project
├── static/             # If used in your project
├── requirements.txt    # If created
└── README.md
```

## Prerequisites

Before running the project, install:

- Python compatible with your project's dependencies.
- PostgreSQL.
- pip.
- Git (optional, for version control and GitHub).
- Visual Studio Code or another code editor.

## Installation and Setup

### 1. Clone the repository

After uploading the project to GitHub, clone it using:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd banking_project
```

Replace the placeholder with your actual GitHub repository URL.

If you already have the project locally, open its root directory in your terminal instead.

### 2. Create and activate a virtual environment

Create the environment:

```bash
python -m venv venv
```

On Windows Command Prompt:

```bash
venv\Scripts\activate
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

If the project contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

If you have not created this file yet, activate your virtual environment and install the dependencies used by your project. The core backend packages include:

```bash
pip install django djangorestframework djangorestframework-simplejwt "psycopg[binary]"
```

For a reproducible setup, generate a requirements file after confirming your project works:

```bash
pip freeze > requirements.txt
```

### 4. Configure PostgreSQL

Create a PostgreSQL database for the application. For example:

```sql
CREATE DATABASE banking_db;
```

Configure the Django database settings to use PostgreSQL. Provide the database name, username, password, host, and port through environment variables or your local development configuration.

Do not commit database passwords or other secrets to GitHub.

### 5. Apply database migrations

Run:

```bash
python manage.py makemigrations
python manage.py migrate
```

If migrations are already included in the repository and up to date, running `python manage.py migrate` is normally sufficient.

### 6. Create an administrator account

Run:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your Django administrator account.

### 7. Start the development server

Run:

```bash
python manage.py runserver
```

Open the local address in your browser:

http://127.0.0.1:8000/

Use the configured application routes to access the frontend and API endpoints.

## API Endpoints

The following endpoints describe the current API functionality. Confirm the exact URL prefixes in your Django URL configuration before publishing the repository.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/token/` | Obtain JWT access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh an access token |
| POST | `/api/deposit/` | Deposit funds into an account |
| POST | `/api/withdraw/` | Withdraw funds from an account |
| POST | `/api/transfer/` | Transfer funds between accounts |
| GET | `/api/accounts/` | List the authenticated user's accounts |
| GET | `/api/accounts/<account_number>/` | Retrieve account details |
| GET | `/api/accounts/<account_number>/balance/` | Retrieve an account balance |
| GET | `/api/accounts/<account_number>/transactions/` | Retrieve paginated transaction history |

Protected endpoints require a valid JWT access token. Send it in the request header:

```http
Authorization: Bearer <access_token>
```

The actual request body fields and response formats are defined by the project's serializers and views.

## Running Automated Tests

The project includes automated Django tests for banking functionality, account access, and transaction behavior.

Run the banking app's test suite:

```bash
python manage.py test banking
```

**Latest recorded test result:** 41 tests passed, with no failures.

This result reflects the test run completed during development. Run the command again after making changes to verify the current code.

## Security and Data Integrity

SecureBank includes several backend safeguards:

- JWT authentication for protected API operations.
- Ownership checks to restrict account access.
- Validation of account status and transaction conditions.
- Balance checks before withdrawals and transfers.
- Atomic database operations to help prevent partially completed transactions.
- Row-level locking during supported transaction operations.

This is a learning and demonstration project. It is not a production banking system and has not been presented as independently security-audited or compliant with banking regulations. Use test data only.

## Future Enhancements

Potential future improvements include:

- Automated API documentation with Swagger or OpenAPI.
- Improved audit logging and monitoring.
- More comprehensive API integration tests.
- Docker-based development setup.
- CI automation for running tests.
- Deployment to a secure hosting environment.
- Additional input validation, rate limiting, and security hardening.

## Learning Outcomes

This project demonstrates practical experience with:

- Python and Django application development.
- REST API design using Django REST Framework.
- JWT authentication and authorization.
- PostgreSQL database integration and Django ORM.
- Database relationships and migrations.
- Transaction integrity using atomic operations and row-level locking.
- Automated testing with Django's testing framework.
- Frontend-to-backend integration.

## Author

**Developer:** [Your Name]

**Project:** SecureBank – Banking Transaction Management System

**Technology Focus:** Python, Django REST Framework, PostgreSQL, REST APIs, JWT Authentication

---

*SecureBank is a demonstration project created for learning and showcasing web application development skills. It does not process real money or connect to actual banking systems.*