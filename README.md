# 💰 PennyWise — Personal Expense Tracker

<p align="center">
  <strong>Take control of your money, one transaction at a time.</strong>
</p>

PennyWise is a web-based **Personal Expense Tracker** built with Python Flask and SQLite. It helps users record their income and expenses, manage monthly budgets, track spending history, and understand their financial habits through an interactive dashboard.

Whether you're a student managing pocket money or someone who wants to organize personal finances, PennyWise makes tracking money simple and convenient.

## ✨ Features

- 🔐 **User Authentication** — Register an account and log in securely.
- 💵 **Income Tracking** — Record and monitor your income.
- 💸 **Expense Management** — Add and manage daily expenses.
- 🏷️ **Transaction Categories** — Organize transactions by category.
- 📊 **Interactive Dashboard** — View important financial information and charts.
- 🎯 **Monthly Budget Management** — Set monthly budgets and monitor spending.
- 📅 **Transaction History** — Review previous transactions and filter records by date.
- 💰 **Savings Overview** — Understand the relationship between income, expenses, and savings.
- 🗄️ **SQLite Database** — Store user accounts, transactions, and budgets locally.
- 📱 **Responsive Interface** — Use a clean interface designed for convenient navigation.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| SQLite | Database management |
| HTML5 | Page structure |
| CSS3 | Styling and responsive design |
| JavaScript | Interactive elements and charts |
| Jinja2 | Dynamic HTML templates |

## 📁 Project Structure

```text
PennyWise-Personal-Expense-Tracker/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── .gitignore              # Files excluded from Git
│
├── expense_tracker.db      # Local database (created at runtime)
│
├── templates/              # HTML templates
│   ├── base.html           # Shared page layout
│   ├── dashboard.html      # Financial dashboard
│   ├── add_transaction.html
│   ├── transactions.html   # Transaction history
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   └── 404.html            # Error page
│
└── static/
    ├── css/
    │   └── style.css       # Application styles
    │
    └── js/
        └── script.js       # Client-side interactions
```

> **Note:** The SQLite database file is generated locally when the application initializes. It is excluded from Git so your local financial records are not uploaded to GitHub.

## 🚀 How to Install and Run the Project

Follow these steps even if you are running the project for the first time.

### Prerequisites

Install the following before starting:

- [Python](https://www.python.org/downloads/) — preferably Python 3.10 or newer.
- [Git](https://git-scm.com/downloads/) — required to clone the repository.
- A code editor such as [Visual Studio Code](https://code.visualstudio.com/).

### Step 1: Clone the repository

Open PowerShell or your terminal and run:

```bash
git clone https://github.com/shailesh-23-patil/PennyWise-Personal-Expense-Tracker.git
```

### Step 2: Open the project folder

```bash
cd PennyWise-Personal-Expense-Tracker
```

### Step 3: Create a virtual environment

A virtual environment keeps the project's Python packages separate from other projects.

```bash
python -m venv .venv
```

### Step 4: Activate the virtual environment

For Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, you should see `(.venv)` at the beginning of your terminal prompt.

If PowerShell blocks script execution, you can activate the environment from Command Prompt instead:

```cmd
.venv\Scripts\activate.bat
```

### Step 5: Install the required packages

```bash
python -m pip install -r requirements.txt
```

This installs Flask and the dependencies listed in `requirements.txt`.

### Step 6: Run the application

```bash
python app.py
```

Wait for Flask to start. Your terminal should display a local development address.

### Step 7: Open PennyWise in your browser

Visit:

**http://127.0.0.1:5000**

Register a new account, log in, and start managing your income, expenses, and budgets.

To stop the application, return to the terminal and press `Ctrl + C`.

## 📖 How to Use PennyWise

1. **Create an account:** Register with your details.
2. **Log in:** Access your personal expense tracker.
3. **Explore the dashboard:** Review your income, expenses, savings, and budget information.
4. **Add a transaction:** Record income or an expense with the relevant details and category.
5. **Set a budget:** Define a monthly spending limit.
6. **Review your history:** Browse past transactions and use the available date filters.
7. **Understand your spending:** Use the dashboard's visualizations to review your financial activity.

## 🗄️ Database Information

PennyWise uses SQLite, a lightweight database that runs locally without requiring a separate database server.

The application uses these tables:

- **`users`** — Stores registered user information, including password hashes.
- **`transactions`** — Stores income and expense records associated with users.
- **`budgets`** — Stores users' budget information.

The database file is created locally by the application. Your local database is not included in the GitHub repository.

## 🔒 Security and Privacy

- Passwords are stored as hashes rather than plain-text passwords.
- The local SQLite database is excluded from Git using `.gitignore`.
- Keep secret keys and credentials out of public repositories.
- Before deploying the application publicly, configure a strong secret key and review protections such as CSRF protection, input validation, and production deployment settings.

**Important:** This project is intended for learning and personal use. Review and strengthen its security before using it to store sensitive financial information in a public deployment.

## 🎓 Project Information

- **Project Name:** PennyWise — Personal Expense Tracker
- **Project Type:** Web Application
- **Project Category:** Python / Web Development
- **Backend:** Python Flask
- **Database:** SQLite

This project demonstrates practical concepts such as web development, user authentication, database operations, CRUD functionality, session management, and financial data visualization.

## 🔮 Future Enhancements

Potential improvements for future versions include:

- 📤 Export transactions to CSV or PDF.
- 🔔 Budget limit notifications.
- 📈 Advanced spending analytics and monthly comparisons.
- ☁️ Secure cloud deployment.
- 📱 Further improvements to mobile usability.

## 👨‍💻 Author

**Shailesh Patil**

GitHub: [@shailesh-23-patil](https://github.com/shailesh-23-patil)

## ⭐ Support

If you find this project useful for learning Python, Flask, or database development, consider giving the repository a ⭐ on GitHub.

---

<p align="center">
  <strong>Made with Python, Flask, and a goal to make money management easier. 💚</strong>
</p>
