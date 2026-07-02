# 🔐 JWT Authentication — Django

A **Django** implementation of JWT authentication with **user registration**, **login**, and **access + refresh tokens**. Part of a three-part series implementing the *same* auth flow in Flask, Django, and FastAPI.

> **Django's philosophy: batteries included.** Django's built-in `User` model and auth system handle password hashing and credential checks for you, so you write far less token plumbing than in Flask.

---

## ✨ Features

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/register` | POST | Create an account — password hashed via Django's auth system |
| `/login` | POST | Verify credentials, return an **access** + **refresh** token |
| `/refresh` | POST | Exchange a valid refresh token for a new access token |
| `/me` | GET | Protected route — requires a valid access token |

Built on **Django** with **PyJWT** for signing tokens. (The same pattern works cleanly with `djangorestframework-simplejwt` if you prefer DRF.)

---

## 🚀 Quick start

```bash
# 1. Clone
git clone <your-repo-url>
cd jwt-auth-django

# 2. Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up the database
python manage.py migrate

# 5. Run
python manage.py runserver
```

The server starts at **http://127.0.0.1:8000**.

---

## 🧪 Try it out

**1. Register**
```bash
curl -X POST http://127.0.0.1:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"priya","email":"priya@email.com","password":"mypass123"}'
```

**2. Login** — returns `access` and `refresh`
```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"priya","password":"mypass123"}'
```

**3. Access a protected route**
```bash
curl http://127.0.0.1:8000/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**4. Refresh**
```bash
curl -X POST http://127.0.0.1:8000/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<REFRESH_TOKEN>"}'
```

> 💡 **On Windows PowerShell**, use `curl.exe` or the [Thunder Client](https://www.thunderclient.com/) VS Code extension.

---

## 🧠 How it works

1. **Register** → `User.objects.create_user()` hashes the password automatically; only the hash is stored.
2. **Login** → `authenticate()` verifies the credentials, then a signed **access token** (15 min) and **refresh token** (7 days) are issued via PyJWT.
3. **Protected requests** → the view decodes the `Authorization: Bearer` token, confirms it's an *access* token, and loads the user. No server-side session.
4. **Refresh** → the `/refresh` endpoint accepts only a *refresh*-type token and returns a fresh access token.

---

## ⚠️ Notes worth knowing

- Response fields are **`access`** and **`refresh`** (not `access_token` / `refresh_token`).
- Login authenticates by **`username`**, which is Django's default. Email-based login requires a custom user model.

---

## 🔒 Security notes

- Django's `SECRET_KEY` signs the tokens — load it from an environment variable in production and never commit it.
- Token lifetimes are set in `accounts/views.py` (15 min access, 7 day refresh).
- Always serve over **HTTPS**.

---

## 🛠 Tech stack

| Component | Library |
|-----------|---------|
| Web framework | Django |
| JWT handling | PyJWT |
| Password hashing | Django auth (built-in) |
| Database | SQLite (default) |

---

## 📚 The full series

- 🧪 **Flask** — manual & explicit
- 🎸 **Django** ← *you are here*
- ⚡ **FastAPI** — modern, typed, with auto-generated interactive docs

⭐ If this helped you understand JWT, consider starring the repo!
