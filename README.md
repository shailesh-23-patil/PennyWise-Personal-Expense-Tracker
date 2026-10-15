# PennyWise — Personal Expense Tracker

A BCA minor project built with Python, Flask, SQLite, HTML, CSS, JavaScript and Chart.js.

## Features

- User registration and login with hashed passwords
- User-specific data isolation
- Add income and expense transactions
- Predefined income and expense categories
- Monthly budget creation and progress indicator
- Dashboard with monthly income, expenses, savings and all-time savings
- Interactive monthly comparison and spending category charts
- Transaction history with type, category, text and date filters
- Delete transactions
- Responsive layout for desktop and mobile

## Requirements

- Python 3.10 or newer
- A browser
- Internet access for the Google Fonts and Chart.js CDN assets (the app itself runs locally)

## Windows setup (PowerShell)

1. Extract the ZIP and open the `Personal-Expense-Tracker` folder in VS Code.
2. Open a terminal in that folder.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

4. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, either allow scripts for the current terminal with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again, or use Command Prompt and run `.venv\Scripts\activate.bat`.

5. Install Flask:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. Start the app:

   ```powershell
   python app.py
   ```

7. Open `http://127.0.0.1:5000` in your browser.
8. Choose **Create an account**, register, and start entering transactions.

The SQLite database `expense_tracker.db` is created automatically in the project folder on the first run.

## Project structure

```text
Personal-Expense-Tracker/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── add_transaction.html
│   ├── transactions.html
│   └── 404.html
└── static/
    ├── css/style.css
    └── js/script.js
```

## Important notes

- This is a learning/demo project, not a production financial service.
- Before deployment, set a long random `SECRET_KEY` environment variable. Do not use the development key in a public deployment.
- Use HTTPS and add CSRF protection before deploying publicly. Keep dependencies updated.
- Chart.js and Google Fonts load from external CDNs, so charts and custom fonts require internet access.

## Suggested test plan

1. Register a new user and log in.
2. Add income of ₹25,000 under Salary.
3. Add expenses in Food and Transport categories.
4. Check that dashboard savings equal income minus expenses for the selected month.
5. Set a monthly budget and verify the progress indicator.
6. Filter transactions by type, category, text and date range.
7. Delete a transaction and verify the totals update.
8. Log out and log back in; verify the records remain saved.
9. Register a second account and verify it cannot see the first account's records.

## Viva explanation

- **Flask:** routes HTTP requests and renders HTML templates.
- **SQLite:** stores users, transactions and budgets in a local database file.
- **Password hashing:** passwords are stored as hashes using Werkzeug, not as plain text.
- **Parameterized SQL:** user-provided values are passed separately to SQL statements.
- **JavaScript:** changes transaction categories dynamically and checks date filter ranges.
- **Chart.js:** renders the monthly bar chart and expense doughnut chart.
- **Savings formula:** selected-month income minus selected-month expenses.
