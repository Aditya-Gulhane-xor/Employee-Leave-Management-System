# Employee Leave Management System (Django + MySQL)

This is a  Employee Leave Management System built using Django with MySQL as the database. 
The project allows employees to apply for leave, managers to approve or reject leave requests, and admins to manage users and leave records. 


# Features
Employee registration & login
Apply for leave
Approve / reject leave requests
Track leave history and status
Admin panel for managing employees and leaves
Clean and modular Django structure

# Tech Stack
Backend: Django
Database: MySQL
Language: Python
Frontend: Django Templates / HTML

# Installation & Setup
1. Clone the Repository
git clone <your-repo-url>
cd <project-folder>

2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows

3. Install Requirements
pip install -r requirements.txt

4. Configure Database (MySQL)

Update your settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

5. Run Migrations
python manage.py migrate

6. Start Server
python manage.py runserver
