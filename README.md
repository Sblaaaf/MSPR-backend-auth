# HealthAI Auth Service

Service d'authentification pour HealthAI. Il vérifie l'email et le mot de passe contre la table `utilisateur` de la base PostgreSQL `healthai`.

## Endpoint principal

- `POST /login` : authentifie l'utilisateur

## Configuration

Le service se connecte à la base PostgreSQL via :

- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

## Exécution

```bash
cd services/auth
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

## Exemple Postman

### 1) Request de login

POST `http://localhost:8004/login`

Headers
- `Content-Type: application/json`

Body JSON
```json
{
  "email": "jean.dupont@example.com",
  "password": "secret123"
}
```

### 2) Réponse attendue en cas de succès

```json
{
  "success": true,
  "message": "Authentification réussie.",
  "user_id": 1,
  "email": "jean.dupont@example.com"
}
```

### 3) Exemple d’échec (mot de passe incorrect)

POST `http://localhost:8004/login`

Headers
- `Content-Type: application/json`

Body JSON
```json
{
  "email": "jean.dupont@example.com",
  "password": "mauvaismotdepasse"
}
```

Réponse attendue : `401 Unauthorized`

```json
{
  "detail": "Email ou mot de passe incorrect."
}
```

### 4) Via le gateway

Si tu souhaites passer par le gateway :
- `POST http://localhost:8000/auth/login`

Le body JSON est identique.

