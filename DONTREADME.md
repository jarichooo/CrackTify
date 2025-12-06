# Cracktify — Local Development Setup (Frontend + Backend + XAMPP Database)

This guide explains how to run:

- the **backend server (FastAPI)**
- the **MySQL database (XAMPP)**
- the **frontend app (Flet)**  
locally on your machine.

---

# Prerequisites

Make sure you have installed:

- **Python 3.10+**
- **pip**
- **XAMPP** (for MySQL database)
- **Flet** (`pip install flet`)
- **FastAPI & SQLAlchemy** (`pip install fastapi uvicorn sqlalchemy pymysql python-dotenv httpx`)

---

# Step 1: Start MySQL using XAMPP

1. Open **XAMPP Control Panel**
2. Start **MySQL** and **Apache**
3. Open **phpMyAdmin**  
   Go to: `http://localhost/phpmyadmin`
4. Create a new database: `crackapp`

5. No tables needed — FastAPI will auto-create them.

---

# Step 2: Configure Backend `.env`
Copy the example file by running:
```bash
cd server
copy .env.example .env
```

Make sure your MySQL credentials match XAMPP, and your email and [app password](https://myaccount.google.com/apppasswords) are correct.

---

# Step 3: Run the Backend Server

Open a terminal and go to the backend folder:

```bash
cd server
uvicorn main:app --reload --port 8000
```
Your FastAPI will run at
```bash
http://127.0.0.1:8000
```

## Step 4: Configure API URL in Frontend
Navigate to your Flet app directory `askcrack-project/`. Create a `.env` file, then add
```bash
API_BASE_URL = "http://127.0.0.1:8000"
```

## Step 5: Run the Flet Frontend
Open a new terminal, then run:

```bash
cd askcrack-project
flet run # flet run --android if you want to run it on Flet mobile
```