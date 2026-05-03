# PPG — Module M2 : IA & Génération (Sprint 1)
> Responsable : Khadija Ben Amor
> IA : Ollama + Mistral (local, gratuit, sans clé API)

---

## 🚀 Installation étape par étape

### 1. S'assurer qu'Ollama tourne
Ouvre un terminal et tape :
```
ollama serve
```
Laisse ce terminal ouvert. Ollama doit tourner en arrière-plan.

### 2. Créer l'environnement virtuel Python
```
python -m venv venv
venv\Scripts\activate
```

### 3. Installer les dépendances
```
pip install -r requirements.txt
```

### 4. Configurer le fichier .env
```
copy .env.example .env
```
Ouvre `.env` — pas besoin de changer quoi que ce soit, tout est déjà configuré pour Ollama !

### 5. Appliquer les migrations
```
python manage.py makemigrations
python manage.py migrate
```

### 6. Lancer le serveur
```
python manage.py runserver
```

---

## 🧪 Lancer les tests
```
python manage.py test ai_generation
```

---

## 📡 Endpoints disponibles

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/ai/generate-summary/` | Génère résumé + mots-clés |
| GET  | `/api/ai/summaries/` | Liste tous les résumés |
| PATCH | `/api/ai/summaries/<id>/validate/` | Valider ou rejeter |

---

## 📁 Structure du projet

```
ppg_sprint1_ollama/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── ppg_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── ai_generation/
    ├── models.py
    ├── services.py   ← appelle Ollama en local
    ├── views.py
    ├── urls.py
    ├── admin.py
    └── tests.py
```
