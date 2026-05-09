# SteriFlow Backend

Django REST API backend for the SteriFlow sterilization workflow management system.

## Setup

### 1. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Edit .env and fill in your Supabase DB password and a new SECRET_KEY
```

Generate a SECRET_KEY with:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run migrations (creates tables in your Supabase PostgreSQL)
```bash
python manage.py migrate
```

### 5. Create your first admin account
```bash
python manage.py createsuperuser
# Enter email, full_name, password when prompted
```

### 6. Run the development server
```bash
python manage.py runserver
```

---

## API Endpoints

| Method | URL | Auth Required | Description |
|--------|-----|--------------|-------------|
| POST | `/api/auth/login/` | ❌ | Login → returns JWT tokens |
| POST | `/api/auth/logout/` | ✅ | Blacklist refresh token |
| POST | `/api/auth/token/refresh/` | ❌ | Get new access token |
| GET/PUT | `/api/auth/me/` | ✅ | View/edit own profile |
| POST | `/api/auth/change-password/` | ✅ | Change own password |
| GET/POST | `/api/auth/users/` | ✅ Admin only | List / create users |
| GET/PATCH/DELETE | `/api/auth/users/<id>/` | ✅ Admin only | Manage a user |

## Role Summary

| Role | Can do |
|------|--------|
| `admin` | Create/deactivate users, view all lists, receive reports |
| `user` | Create and edit **their own** lists only |
| (viewer) | No account — scans QR code, can submit a report |
