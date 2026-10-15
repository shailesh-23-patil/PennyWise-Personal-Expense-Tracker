
import logging
import os
import re
import sqlite3

from datetime import date, datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "expense_tracker.db")

app = Flask(__name__)

# Set SECRET_KEY as an environment variable before deployment.
SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    SECRET_KEY = "pennywise-development-key-change-before-deployment"
    app.logger.warning(
        "Using the development SECRET_KEY. Configure SECRET_KEY before deployment."
    )

app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("SESSION_COOKIE_SECURE", "false").lower()
    in ("1", "true", "yes")
)

logging.basicConfig(level=logging.INFO)

INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Allowance",
    "Investment",
    "Gift",
    "Other Income",
]

EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Education",
    "Health",
    "Entertainment",
    "Rent",
    "Travel",
    "Other Expense",
]


# ============================================================
# DATABASE
# ============================================================

def get_db():
    """Get a SQLite connection for the current application context."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


@app.teardown_appcontext
def close_db(error=None):
    """Close the current request's database connection."""
    db = g.pop("db", None)

    if db is not None:
        if error is not None:
            db.rollback()

        db.close()


def init_db():
    """Create the database tables if they do not already exist."""
    with sqlite3.connect(DATABASE, timeout=10) as db:
        db.execute("PRAGMA foreign_keys = ON")

        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL
                    CHECK(transaction_type IN ('income', 'expense')),
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL,
                transaction_date TEXT NOT NULL,
                description TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                month TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, month),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_transactions_user_date
            ON transactions(user_id, transaction_date);
        """)


# Initialize tables on startup, including when launched with Flask CLI.
init_db()


# ============================================================
# VALIDATION HELPERS
# ============================================================

def valid_amount(raw):
    """Return a valid positive amount, or None."""
    try:
        if raw is None or len(raw.strip()) > 20:
            return None

        value = float(raw)

        if not (0 < value < 1_000_000_000):
            return None

        # Reject NaN and infinity.
        if value != value or value in (float("inf"), float("-inf")):
            return None

        return value

    except (TypeError, ValueError, OverflowError):
        return None


def valid_email(email):
    """Perform basic server-side email format validation."""
    if not email or len(email) > 160:
        return False

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.fullmatch(pattern, email) is not None


def valid_date(value):
    """Check whether a value is a valid YYYY-MM-DD date."""
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
        return parsed.date().isoformat() == value
    except (TypeError, ValueError):
        return False


def valid_month(value):
    """Check whether a value is a valid YYYY-MM month."""
    try:
        parsed = datetime.strptime(value, "%Y-%m")
        return parsed.strftime("%Y-%m") == value
    except (TypeError, ValueError):
        return False


# ============================================================
# USER SESSION
# ============================================================

@app.before_request
def load_user():
    """Load the signed-in user for each request."""
    g.user = None

    user_id = session.get("user_id")

    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

        # Clear a stale session if its user no longer exists.
        if g.user is None:
            session.clear()


def login_required(view):
    """Require authentication before accessing a view."""
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))

        return view(**kwargs)

    return wrapped_view


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():
    if g.user:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ============================================================
# REGISTRATION
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or len(name) > 80:
            flash("Enter a name (up to 80 characters).", "danger")

        elif not valid_email(email):
            flash("Enter a valid email address.", "danger")

        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")

        elif len(password) > 1024:
            flash("Password is too long.", "danger")

        else:
            try:
                db = get_db()

                cursor = db.execute(
                    """
                    INSERT INTO users (name, email, password_hash)
                    VALUES (?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        generate_password_hash(password),
                    ),
                )

                db.commit()

                # Avoid reusing any previous session data.
                session.clear()
                session["user_id"] = cursor.lastrowid

                flash("Account created. Welcome!", "success")
                return redirect(url_for("dashboard"))

            except sqlite3.IntegrityError:
                flash(
                    "An account with that email already exists.",
                    "danger",
                )

            except sqlite3.Error:
                app.logger.exception("Registration database error.")
                flash(
                    "We couldn't create your account. Please try again.",
                    "danger",
                )

    return render_template("register.html")


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not valid_email(email) or not password:
            flash("Invalid email or password.", "danger")
            return render_template("login.html"), 401

        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if user and check_password_hash(
            user["password_hash"],
            password,
        ):
            session.clear()
            session["user_id"] = user["id"]

            flash("You are now logged in.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "success")

    return redirect(url_for("login"))


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user_id = g.user["id"]

    requested_month = request.args.get(
        "month",
        date.today().strftime("%Y-%m"),
    )

    month = (
        requested_month
        if valid_month(requested_month)
        else date.today().strftime("%Y-%m")
    )

    # Selected month's income and expenses.
    monthly = db.execute(
        """
        SELECT transaction_type, COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = ?
          AND substr(transaction_date, 1, 7) = ?
        GROUP BY transaction_type
        """,
        (user_id, month),
    ).fetchall()

    totals = {"income": 0.0, "expense": 0.0}

    for row in monthly:
        totals[row["transaction_type"]] = row["total"]

    # Lifetime totals.
    all_totals = db.execute(
        """
        SELECT transaction_type, COALESCE(SUM(amount), 0) AS total
        FROM transactions
        WHERE user_id = ?
        GROUP BY transaction_type
        """,
        (user_id,),
    ).fetchall()

    lifetime = {"income": 0.0, "expense": 0.0}

    for row in all_totals:
        lifetime[row["transaction_type"]] = row["total"]

    # Selected month's budget.
    budget_row = db.execute(
        """
        SELECT amount
        FROM budgets
        WHERE user_id = ? AND month = ?
        """,
        (user_id, month),
    ).fetchone()

    budget = budget_row["amount"] if budget_row else 0.0

    budget_used = (
        totals["expense"] / budget * 100
        if budget > 0
        else 0
    )

    # Expense category breakdown.
    category_rows = db.execute(
        """
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE user_id = ?
          AND transaction_type = 'expense'
          AND substr(transaction_date, 1, 7) = ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (user_id, month),
    ).fetchall()

    # Most recent transactions.
    recent = db.execute(
        """
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY transaction_date DESC, id DESC
        LIMIT 6
        """,
        (user_id,),
    ).fetchall()

    # Latest six months containing transactions.
    chart_rows = db.execute(
        """
        SELECT
            substr(transaction_date, 1, 7) AS month,
            SUM(
                CASE
                    WHEN transaction_type = 'income' THEN amount
                    ELSE 0
                END
            ) AS income,
            SUM(
                CASE
                    WHEN transaction_type = 'expense' THEN amount
                    ELSE 0
                END
            ) AS expense
        FROM transactions
        WHERE user_id = ?
        GROUP BY substr(transaction_date, 1, 7)
        ORDER BY month DESC
        LIMIT 6
        """,
        (user_id,),
    ).fetchall()

    chart_rows = list(reversed(chart_rows))

    return render_template(
        "dashboard.html",
        month=month,
        totals=totals,
        savings=totals["income"] - totals["expense"],
        lifetime=lifetime,
        budget=budget,
        budget_used=budget_used,
        category_rows=category_rows,
        recent=recent,
        chart_rows=chart_rows,
    )


# ============================================================
# TRANSACTION HISTORY AND FILTERS
# ============================================================

@app.route("/transactions")
@login_required
def transactions():
    db = get_db()
    user_id = g.user["id"]

    tx_type = request.args.get("type", "").strip()
    category = request.args.get("category", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    search = request.args.get("search", "").strip()[:100]

    conditions = ["user_id = ?"]
    params = [user_id]

    if tx_type in ("income", "expense"):
        conditions.append("transaction_type = ?")
        params.append(tx_type)
    else:
        tx_type = ""

    allowed_categories = set(
        INCOME_CATEGORIES + EXPENSE_CATEGORIES
    )

    if category and category in allowed_categories:
        conditions.append("category = ?")
        params.append(category)
    else:
        category = ""

    if start_date:
        if valid_date(start_date):
            conditions.append("transaction_date >= ?")
            params.append(start_date)
        else:
            start_date = ""

    if end_date:
        if valid_date(end_date):
            conditions.append("transaction_date <= ?")
            params.append(end_date)
        else:
            end_date = ""

    if start_date and end_date and start_date > end_date:
        start_date = ""
        end_date = ""

        flash(
            "The date range was invalid. Please select valid dates.",
            "warning",
        )

        # Remove date filters from this request.
        conditions = ["user_id = ?"]
        params = [user_id]

        if tx_type:
            conditions.append("transaction_type = ?")
            params.append(tx_type)

        if category:
            conditions.append("category = ?")
            params.append(category)

        if search:
            conditions.append(
                "(description LIKE ? OR category LIKE ?)"
            )
            params.extend([f"%{search}%", f"%{search}%"])

    elif start_date and end_date:
        # Both dates are valid and in the correct order.
        conditions.append("transaction_date >= ?")
        params.append(start_date)
        conditions.append("transaction_date <= ?")
        params.append(end_date)

    elif start_date:
        conditions.append("transaction_date >= ?")
        params.append(start_date)

    elif end_date:
        conditions.append("transaction_date <= ?")
        params.append(end_date)

    if search:
        conditions.append(
            "(description LIKE ? OR category LIKE ?)"
        )
        params.extend([f"%{search}%", f"%{search}%"])

    query = (
        "SELECT * FROM transactions WHERE "
        + " AND ".join(conditions)
        + " ORDER BY transaction_date DESC, id DESC"
    )

    rows = db.execute(query, params).fetchall()

    return render_template(
        "transactions.html",
        transactions=rows,
        tx_type=tx_type,
        category=category,
        start_date=start_date,
        end_date=end_date,
        search=search,
        all_categories=sorted(
            set(INCOME_CATEGORIES + EXPENSE_CATEGORIES)
        ),
    )


# ============================================================
# ADD TRANSACTION
# ============================================================

@app.route("/transactions/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        tx_type = request.form.get("transaction_type", "").strip()
        amount = valid_amount(request.form.get("amount"))
        category = request.form.get("category", "").strip()
        tx_date = request.form.get("transaction_date", "").strip()
        description = request.form.get("description", "").strip()

        if len(description) > 250:
            description = description[:250]

        allowed_categories = (
            INCOME_CATEGORIES
            if tx_type == "income"
            else EXPENSE_CATEGORIES
            if tx_type == "expense"
            else []
        )

        if (
            not allowed_categories
            or amount is None
            or category not in allowed_categories
            or not valid_date(tx_date)
        ):
            flash(
                "Please check the transaction type, amount, category and date.",
                "danger",
            )

        else:
            try:
                db = get_db()

                db.execute(
                    """
                    INSERT INTO transactions (
                        user_id,
                        transaction_type,
                        amount,
                        category,
                        transaction_date,
                        description
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        g.user["id"],
                        tx_type,
                        amount,
                        category,
                        tx_date,
                        description,
                    ),
                )

                db.commit()

                flash("Transaction added successfully.", "success")
                return redirect(url_for("transactions"))

            except sqlite3.Error:
                app.logger.exception("Could not add transaction.")
                flash(
                    "We couldn't save your transaction. Please try again.",
                    "danger",
                )

    return render_template(
        "add_transaction.html",
        income_categories=INCOME_CATEGORIES,
        expense_categories=EXPENSE_CATEGORIES,
        today=date.today().isoformat(),
    )


# ============================================================
# DELETE TRANSACTION
# ============================================================

@app.route(
    "/transactions/<int:transaction_id>/delete",
    methods=["POST"],
)
@login_required
def delete_transaction(transaction_id):
    db = get_db()

    # A user can delete only their own transactions.
    db.execute(
        """
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?
        """,
        (transaction_id, g.user["id"]),
    )

    db.commit()

    flash(
        "Transaction deleted if it belonged to your account.",
        "success",
    )

    # Avoid redirecting to an external URL.
    referrer = request.referrer or ""

    if referrer.startswith(request.host_url):
        return redirect(referrer)

    return redirect(url_for("transactions"))


# ============================================================
# SAVE OR UPDATE MONTHLY BUDGET
# ============================================================

@app.route("/budget", methods=["POST"])
@login_required
def save_budget():
    month = request.form.get("month", "").strip()
    amount = valid_amount(request.form.get("amount"))

    month_valid = valid_month(month)

    if not month_valid or amount is None:
        flash(
            "Enter a valid month and a budget amount greater than zero.",
            "danger",
        )

    else:
        try:
            db = get_db()

            db.execute(
                """
                INSERT INTO budgets (user_id, month, amount)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, month)
                DO UPDATE SET amount = excluded.amount
                """,
                (g.user["id"], month, amount),
            )

            db.commit()

            flash("Monthly budget saved.", "success")

        except sqlite3.Error:
            app.logger.exception("Could not save monthly budget.")
            flash(
                "We couldn't save your budget. Please try again.",
                "danger",
            )

    destination_month = (
        month
        if month_valid
        else date.today().strftime("%Y-%m")
    )

    return redirect(
        url_for("dashboard", month=destination_month)
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    debug_enabled = (
        os.environ.get("FLASK_DEBUG", "false").lower()
        in ("1", "true", "yes")
    )

    app.run(debug=debug_enabled)