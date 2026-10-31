# Fresh Database Setup Guide: `self_healing_test_db`

This guide provides step-by-step instructions to set up, initialize, and run the **Self-Healing Relational Database Integrity System** with a completely fresh MySQL database (`self_healing_test_db`) using **XAMPP / phpMyAdmin** on Windows.

---

## 1. Start MySQL through XAMPP

1. Open the **XAMPP Control Panel** (typically found at `C:\xampp\xampp-control.exe` or from the Start menu).
2. Locate the **MySQL** module row.
3. Click the **Start** button next to MySQL.
4. Verify that the MySQL module background turns **green** and shows port `3306`.
5. *(Optional)* Start the **Apache** module if you want to access phpMyAdmin in your web browser.

---

## 2. Open phpMyAdmin (Optional GUI)

1. Open your web browser.
2. Navigate to:
   ```
   http://localhost/phpmyadmin/
   ```
3. You will see the phpMyAdmin dashboard.

---

## 3. Create the Database & Execute Initialization Scripts

### Method A: Automated PowerShell Import (Fastest & Recommended)

Open a PowerShell terminal in the project root:

```powershell
cd "d:\DBMS PROJECT\Database_Management_System"

# Step 1: Create the new database (self_healing_test_db)
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -h 127.0.0.1 < database\01_create_database.sql"

# Step 2: Create all 16 InnoDB tables and immutability triggers
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -h 127.0.0.1 self_healing_test_db < database\02_create_tables.sql"

# Step 3: Insert clean baseline relational data (departments, instructors, courses, students, enrollments)
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -h 127.0.0.1 self_healing_test_db < database\03_insert_sample_data.sql"

# Step 4: Seed predefined integrity rules catalog (orphans, duplicates, nulls, domains)
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -h 127.0.0.1 self_healing_test_db < database\04_integrity_rules.sql"

# Step 5: (Optional for testing) Inject controlled demo violations
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -h 127.0.0.1 self_healing_test_db < database\05_demo_violations.sql"
```

---

### Method B: Manual GUI Import via phpMyAdmin

1. In phpMyAdmin, click on the **Import** tab on the top navigation bar.
2. Click **Choose File** and select `database/01_create_database.sql`.
3. Scroll down and click **Import** (or **Go**).
4. In the left database sidebar, click on `self_healing_test_db` to select it as the active database.
5. With `self_healing_test_db` selected, click **Import** and sequentially import:
   - `database/02_create_tables.sql`
   - `database/03_insert_sample_data.sql`
   - `database/04_integrity_rules.sql`
   - `database/05_demo_violations.sql` (if preparing demo anomalies)

---

## 4. SQL File Import Order

Always maintain this execution order to respect foreign key hierarchies:

| Sequence | SQL Script | Purpose |
|---|---|---|
| **1st** | `database/01_create_database.sql` | Creates database `self_healing_test_db` (utf8mb4). |
| **2nd** | `database/02_create_tables.sql` | Creates all 16 InnoDB tables, constraints, check bounds, and audit triggers. |
| **3rd** | `database/03_insert_sample_data.sql` | Inserts clean academic baseline data. |
| **4th** | `database/04_integrity_rules.sql` | Configures active integrity rules catalog. |
| **5th** | `database/05_demo_violations.sql` | Injects 11 controlled demo violations across 5 anomaly categories. |
| *Ref* | `database/06_test_queries.sql` | Verification SQL queries to run manually. |
| *Ref* | `database/07_reset_demo_data.sql` | Resets database back to clean baseline state. |

---

## 5. Configure `backend/.env`

Verify that `backend/.env` contains your local XAMPP configuration:

```ini
# Database Configuration for XAMPP MySQL
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=self_healing_test_db
DB_USER=root
DB_PASSWORD=
DB_CHARSET=utf8mb4

# Application Configuration
APP_ENV=development
API_PREFIX=/api
FRONTEND_ORIGIN=http://localhost:5173
DEBUG=True
```

*(Note: Default XAMPP installations have user `root` with an empty password. If you have configured a password in phpMyAdmin, set `DB_PASSWORD=your_password`).*

---

## 6. Install Backend Dependencies

In PowerShell:

```powershell
cd "d:\DBMS PROJECT\Database_Management_System"
pip install -r backend/requirements.txt
```

---

## 7. Install Frontend Dependencies

In PowerShell:

```powershell
cd "d:\DBMS PROJECT\Database_Management_System\frontend"
npm install
```

---

## 8. Start the FastAPI Backend

In Terminal 1:

```powershell
cd "d:\DBMS PROJECT\Database_Management_System"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive OpenAPI Swagger UI is accessible at:
```
http://127.0.0.1:8000/docs
```

---

## 9. Start the React Frontend

In Terminal 2:

```powershell
cd "d:\DBMS PROJECT\Database_Management_System\frontend"
npm run dev
```

The web application dashboard will be live at:
```
http://localhost:5173
```

---

## 10. Verify Connection

1. Open `http://localhost:5173` in your browser.
2. In the top navbar and sidebar:
   - Status badge shows: **MySQL Connected** (green indicator).
   - Database name shows: `self_healing_test_db`.
   - Discovered tables: `16 Tables`.
   - Latency indicator: e.g., `< 50 ms`.
3. Or test via cURL:
   ```powershell
   curl http://127.0.0.1:8000/api/health
   ```
   Expected response:
   ```json
   {
     "success": true,
     "message": "System health check status",
     "data": {
       "database": {
         "connected": true,
         "database_name": "self_healing_test_db",
         "table_count": 16
       }
     }
   }
   ```

---

## 11. How to Inject Demonstration Violations

### Via Web UI:
1. Navigate to **Settings & Status** (`/settings`) from the left sidebar.
2. Click the **Re-Inject Demonstration Violations** button.
3. 11 controlled anomalies will be loaded into `staging_enrollments` and `students`.
4. Navigate to **Integrity Scanner** (`/scanner`) and click **Run Scan Now**.

### Via Terminal:
```powershell
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -h 127.0.0.1 self_healing_test_db < database\05_demo_violations.sql"
```

---

## 12. How to Reset Demonstration Data

### Via Web UI:
1. Navigate to **Settings & Status** (`/settings`).
2. Click the **Reset Database to Clean Baseline** button.
3. This purges staging records and demo violations, leaving clean baseline academic data.

### Via Terminal:
```powershell
cmd /c "C:\xampp\mysql\bin\mysql.exe -u root -h 127.0.0.1 self_healing_test_db < database\07_reset_demo_data.sql"
```

