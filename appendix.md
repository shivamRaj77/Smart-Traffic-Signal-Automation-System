# Smart Traffic System - Step-by-Step Run Commands (Windows CMD)

## 1. Open project root

```cmd
cd D:\Smart-Traffic-Signal-Automation-System
```

## 2. Activate virtual environment

```cmd
.venv\Scripts\activate.bat
```

## 3. Install backend dependencies

```cmd
cd smart_traffic
python -m pip install -r requirements.txt
```

## 4. Run backend API server

```cmd
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## 5. Verify backend is running (new terminal)

Open a new CMD terminal and run:

```cmd
cd D:\Smart-Traffic-Signal-Automation-System
curl http://127.0.0.1:8000/docs
```

## 6. Install frontend dependencies (new terminal)

```cmd
cd D:\Smart-Traffic-Signal-Automation-System\traffic_frontend
npm install
```

## 7. Run frontend dev server

```cmd
npm run dev
```

## 8. Open app in browser

- Backend API docs: http://127.0.0.1:8000/docs
- Frontend app: URL shown in terminal after npm run dev (usually http://localhost:5173)

## 9. Stop servers

- In each running terminal, press Ctrl + C.

