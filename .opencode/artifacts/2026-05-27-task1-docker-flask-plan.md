# Task 1: Docker + Flask Backend — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Set up Docker Compose + Flask backend with all routes for G3Files file sharing.

**Architecture:** Single Docker container running Flask on port 9929, with a mounted `./shared/` volume. HTTP Basic Auth for admin routes using `ADMIN_PASSWORD` env var.

**Tech Stack:** Python 3.11, Flask, Docker Compose, tarfile (stdlib)

---

### Task 1.1: Create `requirements.txt`

**File:** `requirements.txt`

```
Flask==3.0.0
```

Only Flask — no other dependencies. Minimal.

---

### Task 1.2: Create `Dockerfile`

**File:** `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

EXPOSE 9929

CMD ["python", "app/server.py"]
```

- Uses slim Python image
- Copies `requirements.txt` first for layer caching
- Copies `app/` directory
- Exposes port 9929

---

### Task 1.3: Create `docker-compose.yml`

**File:** `docker-compose.yml`

```yaml
version: "3.8"

services:
  g3files:
    build: .
    ports:
      - "9929:9929"
    environment:
      - ADMIN_PASSWORD=${ADMIN_PASSWORD:-admin}
    volumes:
      - ./shared:/app/shared
```

- Single service
- Port 9929 exposed
- `ADMIN_PASSWORD` env var with default "admin"
- Mounts `./shared/` to `/app/shared`

---

### Task 1.4: Create `app/server.py`

**File:** `app/server.py`

```python
import os
import tarfile
import io
from pathlib import Path

from flask import Flask, render_template, request, send_file, abort, Response, redirect, url_for
from functools import wraps

app = Flask(__name__)

SHARED_DIR = Path("/app/shared")
SHARED_DIR.mkdir(exist_ok=True)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")


def check_auth(username, password):
    return username == "admin" and password == ADMIN_PASSWORD


def authenticate():
    return Response(
        "Authentication required",
        401,
        {"WWW-Authenticate": 'Basic realm="G3Files Admin"'},
    )


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def list_shared_items():
    """Return (dirs, files) tuples sorted by name, case-insensitive."""
    items = list(SHARED_DIR.iterdir())
    dirs = sorted(
        [p for p in items if p.is_dir()],
        key=lambda p: p.name.lower(),
    )
    files = sorted(
        [p for p in items if p.is_file()],
        key=lambda p: p.name.lower(),
    )
    return dirs, files


def make_tar_gz(path: Path) -> bytes:
    """Create a .tar.gz archive of a directory in memory."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(path, arcname=path.name)
    buf.seek(0)
    return buf.read()


def make_tar_gz_for_download(path: Path):
    """Return a send_file response for a .tar.gz of the directory."""
    data = make_tar_gz(path)
    return send_file(
        io.BytesIO(data),
        as_attachment=True,
        download_name=f"{path.name}.tar.gz",
        mimetype="application/gzip",
    )


@app.route("/")
def client_index():
    dirs, files = list_shared_items()
    return render_template("client.html", dirs=dirs, files=files)


@app.route("/admin")
@requires_auth
def admin_index():
    dirs, files = list_shared_items()
    msg = request.args.get("msg")
    return render_template("admin.html", dirs=dirs, files=files, msg=msg)


@app.route("/dl/<path:filename>")
def download(filename):
    filepath = SHARED_DIR / filename
    if not filepath.exists():
        abort(404)

    # Prevent path traversal
    try:
        filepath = filepath.resolve()
        SHARED_DIR.resolve()
        if not str(filepath).startswith(str(SHARED_DIR.resolve())):
            abort(403)
    except (ValueError, OSError):
        abort(403)

    if filepath.is_dir():
        return make_tar_gz_for_download(filepath)
    else:
        return send_file(filepath, as_attachment=True)


@app.route("/admin/upload", methods=["POST"])
@requires_auth
def upload():
    if "file" not in request.files:
        return redirect(url_for("admin_index", msg="Erreur : aucun fichier sélectionné"))
    f = request.files["file"]
    if f.filename == "":
        return redirect(url_for("admin_index", msg="Erreur : fichier invalide"))
    # Allow directory upload via webkitdirectory
    filename = f.filename
    # Handle path separators for directory uploads
    # Browsers may send "subdir/filename" or "subdir\\filename"
    safe_name = filename.replace("\\", "/").lstrip("/")
    # Normalize and prevent path traversal
    normalized = os.path.normpath(safe_name)
    if normalized.startswith("..") or normalized.startswith("/"):
        return redirect(url_for("admin_index", msg="Erreur : chemin invalide"))
    dest = SHARED_DIR / normalized
    dest.parent.mkdir(parents=True, exist_ok=True)
    f.save(dest)
    return redirect(url_for("admin_index", msg="Fichier uploadé avec succès"))


@app.route("/admin/delete/<path:filename>", methods=["POST"])
@requires_auth
def delete(filename):
    filepath = SHARED_DIR / filename
    if not filepath.exists():
        return redirect(url_for("admin_index", msg="Erreur : fichier introuvable"))

    # Prevent path traversal
    try:
        filepath = filepath.resolve()
        if not str(filepath).startswith(str(SHARED_DIR.resolve())):
            return redirect(url_for("admin_index", msg="Erreur : chemin invalide"))
    except (ValueError, OSError):
        return redirect(url_for("admin_index", msg="Erreur : chemin invalide"))

    if filepath.is_dir():
        import shutil
        shutil.rmtree(filepath)
    else:
        filepath.unlink()
    return redirect(url_for("admin_index", msg="Élément supprimé"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9929, debug=False)
```

---

### Routes Summary

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/` | GET | No | Client index page — lists files |
| `/admin` | GET | Yes | Admin index page — lists files |
| `/dl/<path>` | GET | No | Download file or `.tar.gz` of directory |
| `/admin/upload` | POST | Yes | Upload file(s) via multipart form |
| `/admin/delete/<path>` | POST | Yes | Delete file or directory |

### Edge Cases

1. **Path traversal** — `/dl/../../../etc/passwd` blocked by resolve+startswith check
2. **Empty shared dir** — `list_shared_items` returns empty tuples; templates handle
3. **Missing file** — returns 404
4. **Upload with paths** — directory upload sends `subdir/filename`; handled by `Path.mkdir(parents=True)`
5. **Filename sanitization** — strips leading `/` and `.` to prevent traversal in upload
6. **Non-existent ADMIN_PASSWORD** — defaults to "admin"

### Testing Strategy

Manual testing via `docker compose up`:
1. Visit `http://localhost:9929/` — should show empty list
2. Visit `http://localhost:9929/admin` — should prompt for auth
3. Login with admin/admin — should see admin page
4. Upload a file — should appear in list
5. Upload a directory — should appear as subdirectory
6. Download a file — should download
7. Download a directory — should download `.tar.gz`
8. Delete a file — should disappear
9. Delete a directory — should disappear

### Exit Criteria

- [ ] `docker compose up` starts without errors
- [ ] `/` returns client page
- [ ] `/admin` returns 401 without auth, 200 with auth
- [ ] File upload works at `/admin/upload`
- [ ] File download works at `/dl/<filename>`
- [ ] Directory download returns `.tar.gz` at `/dl/<dirname>`
- [ ] Delete works at `/admin/delete/<filename>`
- [ ] Path traversal attempts return 403
- [ ] Empty shared directory shows empty list
