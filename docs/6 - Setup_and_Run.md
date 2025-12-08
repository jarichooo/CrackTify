# User Guide

This document provides a guide for the user for the program setup and app interaction.


---
## Preparation

Make sure you have installed:

- **Python 3.10+**
- **pip**
- **XAMPP** (for MySQL database)
- **Flet** (`pip install flet`)
- **FastAPI & SQLAlchemy** (`pip install fastapi uvicorn sqlalchemy pymysql python-dotenv httpx`)

---

## Installation
First, navigate towards where you want the project's **directory** to be.
```bash
cd $HOME\Documents\Example
```
After that, open the **command prompt** then **enter**:
```bash
git clone https://github.com/jarichooo/CrackTify
```

---

## Set-up
#### XAMPP
1. Open **XAMPP Control Panel**, start both **Apache** and **MySQL**, then enter **phpMyAdmin**
    
    Go to: `http://localhost/phpmyadmin`

2. Create a new database: `crackapp`
3. No need to create tables manually — FastAPI will automatically create them.

---

#### Backend .env 
4. Go to **command prompt**, Proceed inside the folder's directory, then go to server folder:
```bash
cd server
``` 
5. Copy the example file by running:
```bash
copy .env.example .env
```
Make sure your credentials match XAMPP, and your email and [app password](https://myaccount.google.com/apppasswords) are correct.

```bash
# You can copy this
# Database config
DB_HOST="localhost"
DB_USER="root"
DB_PORT="3306"
DB_PASSWORD=""
DB_NAME="crackapp"

# Email config
EMAIL_SENDER="cracktify.noreply@gmail.com"
EMAIL_PASSWORD="hhce aqsk anba lwsm"

APP_ENV=development
APP_PORT=8000
APP_HOST=0.0.0.0
SECRET_KEY=your_secret_key_here

JWT_SECRET_KEY="FgfsUDiuhopQ1xX9W0AJDOJffsO0Q2IC0Q9E"
```

---

#### Running the Backend Server
Open a terminal and go to the backend folder:

```bash
cd server
uvicorn main:app --reload --port 8000
```
Your FastAPI will run at
```bash
http://127.0.0.1:8000
```

---

#### Configure API URL in Frontend
Navigate to your Flet app directory `askcrack-project/`. Create a `.env` file, then add this in:
```bash
API_BASE_URL = "http://127.0.0.1:8000"
```

---

#### Run the Flet Frontend
Open a new terminal, then run:

```bash
cd askcrack-project
flet run # flet run --android if you want to run it on Flet mobile
```

---

## Running the Application