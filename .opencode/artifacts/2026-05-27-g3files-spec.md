# G3Files — Specification

## Description
Logiciel de partage de fichiers entre un serveur moderne (Docker) et un client ancien (iMac G3, Mac OS 8.6) via câble RJ45.

## Architecture
- Un seul conteneur Flask dans Docker Compose
- Port exposé : 9929
- Interface serveur (admin) : `/admin` — protégé par mot de passe HTTP Basic Auth
- Interface client : `/` — compatible très vieux navigateurs (Netscape 4, IE 5, Classilla)
- Fichiers partagés stockés dans `./shared/` (volume Docker monté)

## Backend
- Python + Flask
- HTTP Basic Auth pour l'interface admin (mot de passe via variable d'environnement `ADMIN_PASSWORD`)
- Upload de fichiers via formulaire multipart
- Suppression de fichiers partagés
- Génération de `.tar.gz` pour les dossiers au téléchargement

## Structure du projet
```
G3Files/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── app/
│   ├── server.py           # Serveur Flask
│   ├── templates/
│   │   ├── admin.html       # Interface serveur
│   │   └── client.html      # Interface client
│   └── static/
│       └── (icones)
├── shared/                  # Volume monté, fichiers partagés
└── README.md
```

## Interface Serveur (`/admin`)
- Liste des dossiers et fichiers partagés (contenu de `./shared/`)
- Icône poubelle à côté de chaque élément pour arrêter le partage (suppression)
- Bouton pour ajouter un dossier à partager (input file avec directory selector)
- Bouton pour ajouter un fichier à partager (input file)
- Protégé par mot de passe HTTP Basic Auth

## Interface Client (`/`)
- Liste des fichiers et dossiers partagés (contenu de `./shared/`)
- Icône de téléchargement à côté de chaque élément
- Liens `<a href="/dl/nom_fichier">` pour téléchargement direct
- Dossiers servis en `.tar.gz` généré à la volée
- Pas de JavaScript — HTML 3.2/4.01 Transitional compatible
- Tableau `<table>` basique
- `<meta http-equiv="refresh" content="10">` pour rafraîchissement automatique

## Docker
- Docker Compose avec un seul service
- Volume monté : `./shared/:/app/shared`
- Variable d'environnement : `ADMIN_PASSWORD`

## Tâches à planifier

### Tâche 1 : Structure Docker + Flask backend
- `docker-compose.yml`
- `Dockerfile`
- `requirements.txt`
- `app/server.py` — routes Flask complètes :
  - `/` — page client (liste des fichiers partagés)
  - `/admin` — page admin (protégée par mot de passe)
  - `/dl/<path>` — téléchargement fichier ou dossier (.tar.gz)
  - `/admin/upload` — upload de fichier
  - `/admin/delete/<path>` — suppression
  - Fonction de génération `.tar.gz` pour dossiers
  - HTTP Basic Auth avec `ADMIN_PASSWORD`

### Tâche 2 : Template client (`admin.html`)
- Page d'administration protégée par mot de passe
- Liste des fichiers/dossiers avec icônes poubelle
- Formulaires d'upload (fichier et dossier)
- HTML compatible vieux navigateurs
- Afficher le résultat des actions (succès/erreur)

### Tâche 3 : Template client (`client.html`)
- Liste des fichiers/dossiers avec icônes téléchargement
- Liens directs vers `/dl/...`
- `<meta http-equiv="refresh" content="10">`
- Pas de JavaScript
- HTML compatible Netscape 4 / IE 5 / Classilla

## Critères de revue
1. **Compatibilité client ancien** — la page client doit fonctionner sans JavaScript, sans CSS moderne (flex/grid), sur Netscape 4 / IE 5 / Classilla
2. **Sécurité** — l'interface admin est protégée par mot de passe (HTTP Basic Auth), les fichiers partagés ne sont pas accessibles sans auth
3. **Simplicité** — pas de dépendances inutiles, Flask léger, code minimal et lisible
4. **Dockerisation** — le projet se lance avec `docker compose up`, un seul conteneur, port 9929 exposé
5. **Portabilité** — fonctionne sur macOS et Linux
6. **Arborescence** — respecte la structure convenue (`app/server.py`, `app/templates/`, `shared/`, etc.)
7. **Téléchargement dossier** — les dossiers sont servis en `.tar.gz` généré à la volée
8. **HTML sémantique** — utilisation correcte des balises `<table>`, `<a>`, `<form>`, `<input>` compatibles vieux navigateurs
