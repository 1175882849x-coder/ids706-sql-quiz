# IDS 706 — Online Store SQL Quiz

A web-based SQL quiz application built for IDS 706 Data Engineering. Students can sign in, answer SQL questions, execute queries against a live PostgreSQL database, view query results, and save their answers.

## Live Application

**Quiz Website:** https://ids706-sql-quiz-rrekxc266gcslayj28qnpw.streamlit.app/

**GitHub Repository:** https://github.com/1175882849x-coder/ids706-sql-quiz

Replace the quiz website URL above with the actual Streamlit Community Cloud deployment URL.

## Features

- Email/password authentication using Supabase Auth
- Five SQL questions worth 20 points
- Live PostgreSQL queries with results displayed in tables
- Reference SQL and expected results for each question
- Save and reload student SQL answers
- Restricted database roles for query execution and answer storage
- GitHub Actions for automated database connection testing

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| Database | Supabase PostgreSQL |
| Authentication | Supabase Auth |
| Database Driver | psycopg2 |
| Automation | GitHub Actions |
| Deployment | Streamlit Community Cloud |

## Database Design

The application uses PostgreSQL hosted on Supabase.

The main tables are:

- `quiz_data.customers` — customer information
- `quiz_data.products` — product information and prices
- `quiz_data.orders` — customer orders and quantities
- `quiz_data.quiz_questions` — questions, reference SQL, and expected results
- `quiz_data.student_answers` — saved answers linked to authenticated user IDs

The dataset contains 5 customers, 6 products, and 8 orders.

The application connects using the Supabase Session Pooler with SSL required.

## Quiz Questions

| Question | Topic | Points |
|---|---|---|
| Q1 | SELECT, WHERE, ORDER BY | 4 |
| Q2 | ORDER BY, LIMIT | 4 |
| Q3 | GROUP BY, COUNT | 4 |
| Q4 | JOIN | 4 |
| Q5 | JOIN, SUM | 4 |
| **Total** | | **20** |

## How to Use

1. Open the live quiz website.
2. Sign in using an authorized Supabase Auth account.
3. Select one of the five SQL questions.
4. Read the question and optionally open the hint.
5. Enter a SQL query in the editor.
6. Click **Run SQL** to execute the query against the live PostgreSQL database.
7. Review the result table.
8. Click **Save Answer** to save the SQL response.
9. Revisit a question to load a previously saved answer.
10. Click **Sign Out** when finished.

Signed-out users cannot execute queries or save answers.

**Test account:** A test account can be created or enabled by the project administrator in Supabase Authentication. Passwords are not published in this repository.

## Local Setup

Clone the repository:

```bash
git clone https://github.com/1175882849x-coder/ids706-sql-quiz.git
cd ids706-sql-quiz
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a local `.env` file with the following environment variables:

```dotenv
SUPABASE_URL="YOUR_PROJECT_URL"
SUPABASE_KEY="YOUR_PUBLISHABLE_KEY"
QUIZ_DATABASE_URL="YOUR_READ_ONLY_POSTGRESQL_URI"
WRITER_DATABASE_URL="YOUR_WRITER_POSTGRESQL_URI"
DATABASE_URL="YOUR_ADMIN_POSTGRESQL_URI"
```

The admin connection is used for local database setup and testing, not for running the student-facing application.

Database connection strings use the Supabase Session Pooler with `sslmode=require`.

Run the application:

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Authentication and Database Access

Supabase Auth handles email/password authentication.

The Streamlit backend checks the authenticated user's session before allowing SQL execution or answer saving.

The application uses separate database roles:

- `quiz_reader`: executes read-only SQL queries.
- `quiz_writer`: manages saved student answers.
- `postgres`: reserved for database administration and setup.

Student SQL execution is restricted using a read-only database role, read-only transactions, and a statement timeout.

Database credentials are held in environment variables and are excluded from Git.

## GitHub Actions

The workflow is stored at:

`.github/workflows/database-test.yml`

It runs automatically when code is pushed to the `main` branch and can also be started manually.

The workflow:

1. Checks out the repository.
2. Sets up Python.
3. Installs dependencies.
4. Reads `QUIZ_DATABASE_URL` from GitHub Actions Secrets.
5. Runs `test_reader.py` to verify the database connection and retrieve quiz questions.

Database passwords are not embedded in the workflow file.

## Deployment

The app is deployed using Streamlit Community Cloud directly from the GitHub repository.

Configuration values are stored in Streamlit Cloud Secrets rather than committed to the repository.

## Notes

The application is designed as a small educational SQL practice system. The grading focus is the SQL result set rather than an exact match to the reference query.