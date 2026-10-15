# PawConnect – Pet Adoption Management System 🐾

> **B.Tech Computer Science & Engineering – DBMS Mini Project**  
> *"Connecting Paws with Loving Homes."*

PawConnect is a full-featured, responsive pet adoption web application designed to connect verified animal shelters, rescuers, and animal lovers. Built using **Python Flask**, **MySQL**, and **Vanilla CSS/JavaScript**, this project follows clean relational database standards, role-based access control, parameterized SQL queries, and transactional data integrity.

---

## 🎨 Theme & Design Aesthetics
- **Warm Cream Background:** Soft, approachable aesthetic (`#FAF6F0` / `#FDFBF7`)
- **Soft Orange Buttons:** High-contrast, friendly call-to-actions (`#E07A5F`)
- **Brown Headings:** Warm typography in deep espresso brown (`#3D2B1F`)
- **Sage Green Accents:** Trustworthy indicators for health & verified badges (`#81B29A` / `#588157`)
- **Modern Typography:** Styled with Google Fonts *Outfit* and *Plus Jakarta Sans*
- **Fully Responsive:** Adapts seamlessly across desktop, tablet, and mobile devices

---

## 🛠️ Technology Stack
- **Frontend:** HTML5, Modern Vanilla CSS, JavaScript (ES6+)
- **Backend:** Python 3.x, Flask
- **Database:** MySQL 8.0+
- **Connectivity:** `mysql-connector-python` with parameterized prepared queries
- **Security:** `werkzeug.security` (Scrypt password hashing) & environment isolation via `python-dotenv`

---

## 📂 Project Structure

```text
PawConnect/
│
├── .env                     # Local environment configuration (DB credentials & secret key)
├── .env.example             # Template file for environment variables
├── .gitignore               # Excludes .env, __pycache__, and temporary files
├── requirements.txt         # Python package dependencies
├── database.sql             # Relational schema (DDL) + rich sample records (DML)
├── init_db.py               # Automated one-click database setup & seeding script
├── app.py                   # Main Flask application and business logic
├── db.py                    # MySQL connector layer with parameterized queries
│
├── static/
│   ├── css/
│   │   └── style.css        # Warm cream & orange design system
│   └── js/
│       └── main.js          # Interactive live search, menu toggle, and image fallback
│
└── templates/
    ├── base.html            # Master layout with responsive navbar & footer
    ├── index.html           # Home page with hero, statistics & featured pets
    ├── pets.html            # Browse & filter available pets
    ├── pet_detail.html      # Pet profile, medical history & shelter contacts
    ├── login.html           # Sign in with quick-fill demo buttons
    ├── register.html        # Dual registration (Adopter & Shelter)
    ├── apply.html           # Adoption application form
    ├── adopter_dashboard.html # Adopter application status tracker
    ├── shelter_dashboard.html # Shelter pet directory & request review
    ├── add_pet.html         # Add a new pet listing
    ├── edit_pet.html        # Update pet details and availability
    └── admin_dashboard.html # Platform moderation & shelter verification
```

---

## 🗄️ Database Architecture (MySQL)

PawConnect's schema enforces **3rd Normal Form (3NF)** with strict foreign key constraints:

1. **`users`**: Base table for system authentication.
   - Fields: `id`, `full_name`, `email`, `password_hash`, `phone`, `address`, `role` (`'adopter'`, `'shelter'`, `'admin'`), `created_at`.
2. **`shelters`**: Details of animal shelters and rescue centers.
   - Foreign Key: `user_id` references `users(id)` ON DELETE CASCADE.
   - Fields: `shelter_name`, `license_number`, `city`, `state`, `address`, `phone`, `email`, `website`, `is_verified`.
3. **`admins`**: Platform administrators.
   - Foreign Key: `user_id` references `users(id)` ON DELETE CASCADE.
   - Fields: `admin_code`, `department`.
4. **`pets`**: Animals registered for adoption.
   - Foreign Key: `shelter_id` references `shelters(id)` ON DELETE CASCADE.
   - Fields: `name`, `species` (`'Dog'`, `'Cat'`, `'Rabbit'`, `'Bird'`, `'Other'`), `breed`, `age_years`, `age_months`, `gender`, `size`, `color`, `description`, `medical_notes`, `vaccinated`, `spayed_neutered`, `good_with_kids`, `good_with_pets`, `image_url`, `status` (`'Available'`, `'Pending'`, `'Adopted'`), `is_approved`.
5. **`adoption_requests`**: Applications submitted by adopters for a specific pet.
   - Foreign Keys: `pet_id` references `pets(id)` ON DELETE CASCADE, `user_id` references `users(id)` ON DELETE CASCADE.
   - Fields: `housing_type`, `has_yard`, `previous_experience`, `reason_for_adoption`, `contact_phone`, `status` (`'Pending'`, `'Approved'`, `'Rejected'`, `'Cancelled'`), `shelter_remarks`.

---

## ⚡ How to Run Locally on Windows

### Step 1: Clone or Navigate to the Project
Open **PowerShell** or **Command Prompt** and navigate to the project directory:
```powershell
cd "c:\Users\pooji\OneDrive\Desktop\PawConnect"
```

### Step 2: Install Required Python Packages
```powershell
pip install -r requirements.txt
```
*(Packages: `flask`, `mysql-connector-python`, `python-dotenv`, `werkzeug`)*

### Step 3: Configure MySQL Credentials in `.env`
Open the `.env` file in PawConnect and make sure your MySQL password matches your local MySQL server:
```ini
FLASK_SECRET_KEY=pawconnect_secret_key_2026_super_secure_random_btech_dbms
FLASK_DEBUG=True

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=pawconnect_db
```

### Step 4: Initialize the Database & Seed Sample Records
Run the included automated setup script:
```powershell
python init_db.py
```
> **Alternative Manual Method (MySQL Workbench / CLI):**  
> If you prefer MySQL Workbench, open `database.sql` in Workbench and click **Execute (⚡)** to create `pawconnect_db` and insert all demo data.

### Step 5: Start the Flask Web Server
```powershell
python app.py
```

### Step 6: Open the Website in Your Browser
Visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Sample Demonstration Accounts

For demonstration and viva evaluation, sample accounts with realistic data are provided in `database.sql`:

| Role | Email | Description |
| :--- | :--- | :--- |
| **Admin** | `admin@pawconnect.org` | Can verify shelters & moderate pet listings |
| **Shelter** | `hopeforpaws@shelter.org` | Can list pets, edit details, and review applications |
| **Adopter** | `pooja@example.com` | Can browse pets, submit requests & track status |

> **Note on Passwords:** Sample accounts in `database.sql` have unique, randomized placeholder hashes for safety on public repositories. To log in locally, register a new account through the web interface or update the sample user password hash via `werkzeug.security.generate_password_hash`.

---

## 🌟 Key DBMS Implementation Features

1. **No Hardcoded Listings:**
   All pet listings, shelter profiles, cities, and adoption records are loaded dynamically from MySQL tables.
2. **Admin Verification & Moderation:**
   Only pet listings from verified shelters that have been approved (`is_approved = 1` and `is_verified = 1`) appear on the public pages.
3. **Prevention of Duplicate Adoptions:**
   When a shelter approves an application:
   - The selected request is updated to `Approved`.
   - The pet's status automatically transitions to `Adopted`.
   - Competing pending applications for the same pet are automatically updated to `Rejected` with an explanatory note.
   - The pet can no longer receive further adoption approvals.
4. **100% Parameterized Prepared Statements:**
   All queries across `db.py` and `app.py` utilize `%s` placeholders to guarantee immunity against SQL Injection attacks.
5. **Role-Based Access Control (RBAC):**
   Routes are secured using custom Python decorators (`@login_required`, `@role_required`).
