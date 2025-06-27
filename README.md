# 🏥 Hospital Auth & Patient Manager

A Flask-based web application designed for hospitals to manage user authentication and patient record workflows. Integrated with Oracle DB via ODBC, the app offers secure login, account creation, password changes, and patient CRUD operations.


## 🚀 Features

- 🔐 User authentication with main & alternate password support
- ➕ User creation and password change functionality
- 🩺 Patient form with:
  - Save, Update, Delete, Commit
  - Field validations and DOB formatting
- 📦 Dual-table logic (`patients` and `main_table`)
- 📈 Navigation between patient records
- 🖼️ Background images switch dynamically based on context (`bg2.webp`, `bg3.webp`)

## 🗂️ Technologies Used

- Python (Flask)
- Oracle DB (via pyodbc)
- Bootstrap 5 for UI
- HTML/CSS/Jinja2 Templates
- Flatpickr for date selection

## ⚙️ Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/your-username/hospital-auth-patient-manager.git
cd hospital-auth-patient-manager
```
###2. Create a virtual environment and activate it
```
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```
###3. Install dependencies
```
pip install -r requirements.txt
```

###4. Set up Oracle ODBC DSN
Make sure your ODBC Data Source Name (DSN) is configured as oracledb.


###5. Run the app
```
python app.py
```
App runs on: http://localhost:5000

##🔐 Default Login Flow
On login, users are authenticated using either:

- Main password
- Alternate password (e.g., for emergency access)
- Redirects to the patient dashboard

##✍️ Author
Rajasri
B.Tech - Information Technology
[LinkedIn](https://www.linkedin.com/in/rajasri-sampath-kumar-892046296/) | [GitHub](https://github.com/Rajasri-1406)


📜 License
This project is for educational/demo use. Customize and extend as needed for production systems.

---

## ✅ `requirements.txt` (create manually if not done):
```
Flask
pyodbc
```
