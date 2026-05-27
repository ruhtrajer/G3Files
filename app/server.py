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
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(path, arcname=path.name)
    buf.seek(0)
    return buf.read()


def make_tar_gz_for_download(path: Path):
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
    filename = f.filename
    safe_name = filename.replace("\\", "/").lstrip("/")
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
