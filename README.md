# GreenEdu - Green Technology Awareness Platform

A complete web platform for studying **Green Technology Adoption in Educational Institutions**. Built with HTML, CSS, Python Flask, and MySQL (XAMPP).

---

## Features

### Public Site
- 🏠 **Home** — Hero with mission, features (Solar, Energy, Water, Sustainable Campus)
- ℹ️ **About** — Researcher info, project description, value cards, quote
- 📋 **Survey** — Green technology awareness questionnaire
- 🔐 **Login / Register** — Authentication for admin

### Admin Panel
- 📊 **Dashboard** — Stats, recent activity, donut chart, top tech, upcoming events, quote
- 📋 **Survey** — All submitted surveys with scores
- 📊 **Reports** — Green tech adoption stats, top institutions
- 🏫 **Institutions** — Schools, colleges, universities list
- 👨‍🎓 **Students** — Student data and awareness scores
- 🌱 **Green Tech** — Manage technology categories
- ⚙️ **Settings** — User profile, system info

---

## Tech Stack

- **Frontend:** HTML5, CSS3 (vanilla, no frameworks)
- **Backend:** Python 3.8+, Flask
- **Database:** MySQL (via XAMPP)
- **Authentication:** Flask sessions + bcrypt

---

## Project Structure

```
green-technology-45/
├── app.py                    # Flask application
├── config.py                 # Database config
├── requirements.txt          # Dependencies
├── init_db.sql               # DB schema + sample data
├── README.md
├── static/
│   └── css/
│       ├── style.css         # Public site
│       └── admin.css         # Admin panel
└── templates/
    ├── base.html              # Public layout
    ├── home.html
    ├── about.html
    ├── login.html
    ├── register.html
    ├── survey.html
    ├── 404.html
    └── admin/
        ├── admin_base.html    # Admin layout
        ├── dashboard.html
        ├── survey.html
        ├── reports.html
        ├── institutions.html
        ├── students.html
        ├── greentech.html
        └── settings.html
```

---

## Installation

### Step 1: XAMPP Setup
1. Open **XAMPP Control Panel**
2. Start **Apache** and **MySQL**
3. Open phpMyAdmin: [http://localhost/phpmyadmin](http://localhost/phpmyadmin)

### Step 2: Import Database
1. Click **Import** tab in phpMyAdmin
2. Choose the `init_db.sql` file
3. Click **Go**

This creates the `greenedu` database with all tables and sample data.

### Step 3: Python Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Git Bash on Windows)
source venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Run the App
```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

---

## First Admin Account

The `init_db.sql` creates a placeholder admin entry. To set up your first admin:

1. Visit [http://localhost:5000/register](http://localhost:5000/register)
2. Create your account (username, email, password)
3. Login at [http://localhost:5000/login](http://localhost:5000/login)
4. You'll be redirected to the admin dashboard

---

## Configuration

Edit `config.py` to change DB credentials:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''         # XAMPP default
MYSQL_DB = 'greenedu'
SECRET_KEY = 'change-this-in-production'
```

---

## Routes

### Public
| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/about` | About page |
| `/survey` | Survey form |
| `/login` | Login |
| `/register` | Register admin |
| `/logout` | Logout |

### Admin
| Route | Description |
|-------|-------------|
| `/admin` | Dashboard |
| `/admin/survey` | Survey management |
| `/admin/reports` | Reports & analytics |
| `/admin/institutions` | Institutions list |
| `/admin/students` | Students data |
| `/admin/greentech` | Green tech categories |
| `/admin/settings` | Settings |

---

## Database Tables

- `users` — Admins and researchers
- `institutions` — Schools, colleges, universities
- `students` — Student participants
- `surveys` — Survey responses with awareness scores
- `green_tech` — Technology categories with adoption %
- `activities` — Recent activity feed
- `upcoming` — Upcoming events
- `quotes` — Inspirational quotes

---

## Troubleshooting

**MySQL Connection Error**
- Make sure XAMPP MySQL is running
- Check credentials in `config.py`

**mysqlclient Install Error (Windows)**
- Install Microsoft C++ Build Tools
- Or use PyMySQL: replace `MySQLdb` with `pymysql` in `app.py`

**Cannot Login**
- Make sure you registered through `/register` first
- The default admin in `init_db.sql` has a placeholder hash

---

## License

Free for educational use.
