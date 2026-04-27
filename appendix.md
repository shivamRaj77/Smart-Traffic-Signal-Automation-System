# Smart Traffic System - Step-by-Step Run Commands (Windows CMD)

## A. Backend + PostgreSQL (CMD)

### 1. Open project root

```cmd
cd D:\Smart-Traffic-Signal-Automation-System
```

### 2. Activate virtual environment

```cmd
.venv\Scripts\activate.bat
```

### 3. Install backend dependencies

```cmd
cd smart_traffic
python -m pip install -r requirements.txt
```

### 4. Set PostgreSQL connection string (current CMD session)

Replace placeholders with your values.

```cmd
set DATABASE_URL=postgresql://USERNAME:PASSWORD@HOST:5432/DB_NAME
```

Example:

```cmd
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_traffic
```

### 5. Run backend API server

```cmd
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 6. Verify backend is running (new CMD terminal)

```cmd
cd D:\Smart-Traffic-Signal-Automation-System
curl http://127.0.0.1:8000/docs
```

If the server starts correctly, default admin is auto-created:
- username: admin
- password: admin123

## B. Frontend (CMD)

### 1. Open another CMD terminal

```cmd
cd D:\Smart-Traffic-Signal-Automation-System\traffic_frontend
npm install
npm run dev
```

### 2. Open app in browser

- Backend API docs: http://127.0.0.1:8000/docs
- Frontend app: URL shown after `npm run dev` (usually http://localhost:5173)

## C. Run Tests (CMD)

Open a new CMD terminal and run:

```cmd
cd D:\Smart-Traffic-Signal-Automation-System
.venv\Scripts\activate.bat
cd smart_traffic
python -m unittest discover -s tests -p "test_*.py" -v
```

## D. Stop Servers

In each terminal running a server, press Ctrl + C.

## E. Troubleshooting: PostgreSQL Connection Refused

If you see an error like:
- connection to server at localhost, port 5432 failed: Connection refused

it means PostgreSQL is not reachable with your current DATABASE_URL.

### Option 1 (Quick Run): Use SQLite fallback

In CMD, clear DATABASE_URL and start backend:

```cmd
cd D:\Smart-Traffic-Signal-Automation-System
.venv\Scripts\activate.bat
cd smart_traffic
set DATABASE_URL=
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Option 2 (PostgreSQL): Start DB and run with PostgreSQL URL

1. Find PostgreSQL service name:

```cmd
sc query type= service state= all | findstr /I postgres
```

2. Start the service (replace with your exact service name):

```cmd
net start postgresql-x64-16
```

3. Set DATABASE_URL and run backend:

```cmd
cd D:\Smart-Traffic-Signal-Automation-System
.venv\Scripts\activate.bat
cd smart_traffic
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_traffic
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Optional: If PostgreSQL is not installed, run it with Docker

```cmd
docker run --name smart-traffic-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=smart_traffic -p 5432:5432 -d postgres:16
```

## F. Troubleshooting: failed to resolve host 'Shivam'

If you see an error like:
- failed to resolve host 'Shivam': [Errno 11001] getaddrinfo failed

it means your DATABASE_URL currently points to a hostname that your machine cannot resolve.

### Fix in CMD (same terminal where you run uvicorn)

1. Check the current value:

```cmd
echo %DATABASE_URL%
```

2. Clear it:

```cmd
set DATABASE_URL=
```

3. Set a valid PostgreSQL URL (local):

```cmd
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smart_traffic
```

4. Start backend again:

```cmd
cd D:\Smart-Traffic-Signal-Automation-System
.venv\Scripts\activate.bat
cd smart_traffic
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### If PostgreSQL is on another machine

- Replace Shivam with that machine's IP address in DATABASE_URL.
- Example:

```cmd
set DATABASE_URL=postgresql://postgres:postgres@192.168.1.25:5432/smart_traffic
```

- Ensure port 5432 is reachable from your machine.

