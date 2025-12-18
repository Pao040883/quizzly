# Quizly Backend

Django REST API Backend für die Quizly Quiz-Anwendung mit KI-gestützter Quiz-Generierung aus YouTube-Videos.

## 📋 Anforderungen

### Systemanforderungen
- Python 3.10+
- **FFMPEG** (global installiert) - **ERFORDERLICH** für Whisper AI
- Git

### FFMPEG Installation

#### Windows
1. Download von https://www.gyan.dev/ffmpeg/builds/
2. Extrahiere die Datei
3. Füge den `bin`-Ordner zur PATH-Umgebungsvariable hinzu
4. Teste mit: `ffmpeg -version`

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

## 🚀 Installation

### 1. Repository klonen
```bash
git clone <repository-url>
cd backend
```

### 2. Virtuelle Umgebung erstellen und aktivieren
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Gemini API Key einrichten
1. Gehe zu: https://aistudio.google.com/app/apikey
2. Erstelle einen kostenlosen API-Key
3. Öffne `core/settings.py`
4. Trage deinen API-Key ein:
```python
GEMINI_API_KEY = 'dein_api_key_hier'
```

### 5. Datenbank migrieren
```bash
python manage.py migrate
```

### 6. Admin-User erstellen (optional)
```bash
python manage.py createsuperuser
```

### 7. Server starten
```bash
python manage.py runserver
```

Die API läuft nun unter: `http://localhost:8000`

## 📚 API Endpoints

### Authentication Endpoints

#### POST `/api/register/`
Registriert einen neuen Benutzer.

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password",
  "confirmed_password": "your_password",
  "email": "your_email@example.com"
}
```

**Response (201):**
```json
{
  "detail": "User created successfully!"
}
```

#### POST `/api/login/`
Meldet den Benutzer an und setzt Auth-Cookies.

**Request Body:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response (200):**
```json
{
  "detail": "Login successfully!",
  "user": {
    "id": 1,
    "username": "your_username",
    "email": "your_email@example.com"
  }
}
```

#### POST `/api/logout/`
Meldet den Benutzer ab und löscht alle Tokens.

**Authentication:** Required

**Response (200):**
```json
{
  "detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."
}
```

#### POST `/api/token/refresh/`
Erneuert den Access-Token mithilfe des Refresh-Tokens.

**Response (200):**
```json
{
  "detail": "Token refreshed",
  "access": "new_access_token"
}
```

### Quiz Endpoints

#### POST `/api/createQuiz/`
Erstellt ein neues Quiz basierend auf einer YouTube-URL.

**Authentication:** Required

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Quiz Title",
  "description": "Quiz Description",
  "created_at": "2023-07-29T12:34:56.789Z",
  "updated_at": "2023-07-29T12:34:56.789Z",
  "video_url": "https://www.youtube.com/watch?v=example",
  "questions": [
    {
      "id": 1,
      "question_title": "Question 1",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Option A",
      "created_at": "2023-07-29T12:34:56.789Z",
      "updated_at": "2023-07-29T12:34:56.789Z"
    }
  ]
}
```

#### GET `/api/quizzes/`
Ruft alle Quizzes des authentifizierten Benutzers ab.

**Authentication:** Required

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Quiz Title",
    "description": "Quiz Description",
    "created_at": "2023-07-29T12:34:56.789Z",
    "updated_at": "2023-07-29T12:34:56.789Z",
    "video_url": "https://www.youtube.com/watch?v=example",
    "questions": [...]
  }
]
```

#### GET `/api/quizzes/{id}/`
Ruft ein spezifisches Quiz ab.

**Authentication:** Required

**Response (200):** Quiz-Objekt (siehe oben)

#### PATCH `/api/quizzes/{id}/`
Aktualisiert einzelne Felder eines Quiz.

**Authentication:** Required

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated Description"
}
```

**Response (200):** Aktualisiertes Quiz-Objekt

#### DELETE `/api/quizzes/{id}/`
Löscht ein Quiz permanent.

**Authentication:** Required

**Response (204):** Kein Content

## 🔒 Authentifizierung

Die API verwendet JWT-Authentifizierung mit HTTP-only Cookies:
- `access_token`: Gültig für 60 Minuten
- `refresh_token`: Gültig für 7 Tage
- Tokens werden automatisch als Blacklist markiert beim Logout

## 🛠️ Technologie-Stack

- **Django 5.0.7** - Web Framework
- **Django REST Framework 3.15.2** - REST API
- **djangorestframework-simplejwt 5.3.1** - JWT Authentication
- **django-cors-headers 4.3.1** - CORS Support
- **OpenAI Whisper** - Audio Transkription
- **Google Gemini Flash AI** - Quiz-Generierung
- **yt-dlp** - YouTube Download
- **SQLite** - Datenbank (Standard)

## 📁 Projektstruktur

```
backend/
├── core/                      # Django Projekt Settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/            # Authentication App
│   ├── authentication.py      # Custom JWT Auth
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── quizzes/                   # Quizzes App
│   ├── models.py              # Quiz & Question Models
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── functions.py           # YouTube, Whisper, Gemini Utils
│   └── admin.py
├── manage.py
└── requirements.txt
```

## 🔧 Konfiguration

### CORS Einstellungen
In `core/settings.py` können die erlaubten Origins angepasst werden:
```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5500',
    'http://127.0.0.1:5500',
    'http://localhost:3000',
]
```

### JWT Einstellungen
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

## 📝 Admin Panel

Das Admin Panel ist verfügbar unter: `http://localhost:8000/admin/`

Features:
- Benutzer-Verwaltung
- Quiz-Verwaltung mit Inline-Fragen
- Fragen bearbeiten und hinzufügen
- Such- und Filterfunktionen

## 🐛 Troubleshooting

### FFMPEG nicht gefunden
Stelle sicher, dass FFMPEG korrekt installiert und im PATH ist:
```bash
ffmpeg -version
```

### Gemini API Key Fehler
Überprüfe, ob der API Key in `settings.py` eingetragen ist:
```python
GEMINI_API_KEY = 'dein_api_key_hier'
```

### CORS Fehler
Füge die Frontend-URL zu `CORS_ALLOWED_ORIGINS` hinzu.

## 📄 Lizenz

Dieses Projekt ist Teil des Developer Akademie Backend-Kurses.

## 👨‍💻 Entwicklung

### Code Style
- PEP-8 konform
- Funktionen maximal 14 Zeilen
- Sprechende Variablennamen (snake_case)
- Docstrings für alle Funktionen

### Tests ausführen
```bash
python manage.py test
```

## 📞 Support

Bei Fragen oder Problemen erstelle ein Issue im Repository oder kontaktiere den Entwickler.
