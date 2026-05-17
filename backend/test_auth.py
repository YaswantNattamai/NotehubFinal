from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import hashlib
import jwt
import datetime
import uuid

app = FastAPI()

SECRET_KEY = "test-secret"
ALGORITHM = "HS256"

# ── DB ─────────────────────

def get_db():
    conn = sqlite3.connect("test.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ── Models ─────────────────

class SignupRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# ── Helpers ────────────────

def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def create_token(user_id):
    return jwt.encode(
        {"sub": user_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

# ── Routes ─────────────────

@app.post("/signup")
def signup(body: SignupRequest):
    conn = get_db()
    try:
        user_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (user_id, body.email, hash_password(body.password))
        )
        conn.commit()
    except:
        raise HTTPException(400, "User exists")
    finally:
        conn.close()

    return {"message": "User created"}

@app.post("/login")
def login(body: LoginRequest):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email=? AND password_hash=?",
        (body.email, hash_password(body.password))
    ).fetchone()
    conn.close()

    if not user:
        raise HTTPException(401, "Invalid credentials")

    token = create_token(user["id"])
    return {"token": token}

# ── Simple HTML UI ─────────

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body>
        <h2>Login Test</h2>
        
        <h3>Signup</h3>
        <input id="s_email" placeholder="email"><br>
        <input id="s_pass" placeholder="password"><br>
        <button onclick="signup()">Signup</button>

        <h3>Login</h3>
        <input id="l_email" placeholder="email"><br>
        <input id="l_pass" placeholder="password"><br>
        <button onclick="login()">Login</button>

        <pre id="output"></pre>

        <script>
        async function signup() {
            let res = await fetch('/signup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email: document.getElementById('s_email').value,
                    password: document.getElementById('s_pass').value
                })
            });
            document.getElementById('output').innerText = await res.text();
        }

        async function login() {
            let res = await fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email: document.getElementById('l_email').value,
                    password: document.getElementById('l_pass').value
                })
            });
            document.getElementById('output').innerText = await res.text();
        }
        </script>
    </body>
    </html>
    """