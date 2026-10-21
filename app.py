
import os
import pandas as pd
import psycopg2
import sqlparse
import streamlit as st

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

st.set_page_config(
    page_title="SQL Quiz Portal",
    page_icon="📊",
    layout="wide"
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
QUIZ_DATABASE_URL = os.getenv("QUIZ_DATABASE_URL")
WRITER_DATABASE_URL = os.getenv("WRITER_DATABASE_URL")

# One Supabase Auth client per Streamlit session.
# Do not use a globally cached authentication client.
if "auth_client" not in st.session_state:
    st.session_state.auth_client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None


def get_verified_user():
    """Verify authentication on the Supabase server."""
    token = st.session_state.access_token

    if not token:
        return None

    try:
        response = st.session_state.auth_client.auth.get_user(token)
        return response.user
    except Exception:
        return None


def get_connection():
    """Connect using the restricted PostgreSQL role."""
    return psycopg2.connect(
        QUIZ_DATABASE_URL,
        connect_timeout=10,
        options="-c statement_timeout=5000"
    )


def get_writer_connection():
    """Connect using quiz_writer for saving answers."""
    if not WRITER_DATABASE_URL:
        raise ValueError("WRITER_DATABASE_URL is missing")

    return psycopg2.connect(
        WRITER_DATABASE_URL,
        connect_timeout=10
    )


def fetch_questions():
    """Fetch questions from live PostgreSQL."""
    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SET TRANSACTION READ ONLY")

                cur.execute("""
                    SELECT
                        question_id,
                        question_text,
                        points,
                        hint_sql,
                        expected_result
                    FROM quiz_data.quiz_questions
                    ORDER BY question_id
                """)

                return cur.fetchall()
    finally:
        conn.close()


def run_student_sql(sql):
    """Execute one read-only query with bounded results."""

    statements = sqlparse.parse(sql)

    if len(statements) != 1:
        raise ValueError("Enter exactly one SQL statement.")

    statement = statements[0]

    if statement.get_type() != "SELECT":
        raise ValueError("Only SELECT queries are allowed.")

    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                # Defense in depth: prevent data modifications.
                cur.execute("SET TRANSACTION READ ONLY")

                # Execute the student's query.
                cur.execute(sql)

                if cur.description is None:
                    raise ValueError("Query did not return rows.")

                columns = [
                    column[0]
                    for column in cur.description
                ]

                # Display up to 100 rows.
                rows = cur.fetchmany(101)

                truncated = len(rows) > 100
                rows = rows[:100]

                result = pd.DataFrame(
                    rows,
                    columns=columns
                )

                return result, truncated

    finally:
        conn.close()


def save_answer(user_id, question_id, sql_answer):
    """Save or update one student's SQL answer."""

    conn = get_writer_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO quiz_data.student_answers
                        (user_id, question_id, sql_answer)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id, question_id)
                    DO UPDATE SET
                        sql_answer = EXCLUDED.sql_answer,
                        updated_at = NOW()
                """, (
                    str(user_id),
                    question_id,
                    sql_answer
                ))
    finally:
        conn.close()


def load_answer(user_id, question_id):
    """Load a student's previously saved answer."""

    conn = get_writer_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT sql_answer
                    FROM quiz_data.student_answers
                    WHERE user_id = %s
                      AND question_id = %s
                """, (
                    str(user_id),
                    question_id
                ))

                row = cur.fetchone()
                return row[0] if row else ""
    finally:
        conn.close()


st.title("SQL Quiz Portal")
st.caption("IDS 706 — Data Engineering")

user = get_verified_user()

# -------------------
# SIGN-IN PAGE
# -------------------
if user is None:

    st.subheader("Sign In")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button("Sign In")

    if submitted:
        try:
            response = (
                st.session_state.auth_client.auth
                .sign_in_with_password({
                    "email": email,
                    "password": password
                })
            )

            if response.session:
                st.session_state.access_token = (
                    response.session.access_token
                )
                st.session_state.refresh_token = (
                    response.session.refresh_token
                )

                st.rerun()
            else:
                st.error("Login failed.")

        except Exception:
            st.error("Invalid credentials or login error.")

    st.stop()


# -------------------
# AUTHENTICATED PAGE
# -------------------
st.success(f"Signed in as {user.email}")

if st.button("Sign Out"):
    try:
        st.session_state.auth_client.auth.sign_out()
    except Exception:
        pass

    st.session_state.access_token = None
    st.session_state.refresh_token = None

    st.rerun()


st.header("Online Store SQL Quiz")
st.write("5 Questions | 20 Total Points")

try:
    questions = fetch_questions()
except Exception:
    st.error("Could not load quiz questions.")
    st.stop()

if not questions:
    st.warning("No quiz questions found.")
    st.stop()


question_map = {
    q[0]: q for q in questions
}

question_id = st.selectbox(
    "Choose a question",
    list(question_map.keys()),
    format_func=lambda x: f"Question {x}"
)

question = question_map[question_id]

qid, question_text, points, hint_sql, expected = question

st.subheader(f"Question {qid} — {points} points")
st.write(question_text)

with st.expander("Show Hint / Expected Result"):
    st.code(hint_sql, language="sql")
    st.write("Expected Result:", expected)


# -------------------
# SQL EDITOR
# -------------------
st.subheader("SQL Editor")

# Load saved answer when opening a question
editor_key = f"sql_{user.id}_{qid}"

if editor_key not in st.session_state:
    try:
        st.session_state[editor_key] = load_answer(
            user.id,
            qid
        )
    except Exception:
        st.error("Could not load saved answer.")
        st.stop()

sql = st.text_area(
    "Write your SQL query",
    height=180,
    key=editor_key,
    placeholder=(
        "SELECT product_name, price\n"
        "FROM quiz_data.products;"
    )
)

if st.button("Run SQL", type="primary"):

    # Re-check authentication before executing.
    verified_user = get_verified_user()

    if verified_user is None:
        st.error("Please sign in before running SQL.")
        st.stop()

    if not sql.strip():
        st.warning("Please enter a SQL query.")

    else:
        try:
            result, truncated = run_student_sql(sql)

            st.success("Query executed successfully!")
            st.dataframe(
                result,
                use_container_width=True,
                hide_index=True
            )

            st.write(f"Rows displayed: {len(result)}")

            if truncated:
                st.info("Only the first 100 rows are shown.")

        except Exception as error:
            st.error(f"Query error: {error}")


# -------------------
# SAVE ANSWER
# -------------------
if st.button("Save Answer"):

    verified_user = get_verified_user()

    if verified_user is None:
        st.error("Please sign in before saving.")
        st.stop()

    if not sql.strip():
        st.warning("Write SQL before saving.")

    elif len(sql) > 10000:
        st.error("SQL answer is too long.")

    else:
        try:
            save_answer(
                verified_user.id,
                qid,
                sql
            )

            st.success("Answer saved successfully!")

        except Exception:
            st.error("Could not save your answer.")
