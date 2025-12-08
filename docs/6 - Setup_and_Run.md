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

