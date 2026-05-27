# Task 2: Admin Template (admin.html) — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create `admin.html` — the password-protected admin interface for managing shared files.

**Architecture:** Jinja2 template rendered by Flask's `render_template("admin.html", dirs=dirs, files=files)`. Compatible with old browsers (no JS, no modern CSS). Uses HTTP Basic Auth via Flask decorator.

**Tech Stack:** Flask / Jinja2, HTML 4.01 Transitional

**Prior Work:** Routes defined in `app/server.py` (see Task 1 plan at `.opencode/artifacts/2026-05-27-task1-docker-flask-plan.md`)

---

### Context from Task 1

The `admin_index()` route does:
```python
@app.route("/admin")
@requires_auth
def admin_index():
    dirs, files = list_shared_items()
    return render_template("admin.html", dirs=dirs, files=files)
```

Where `list_shared_items()` returns `(dirs, files)` — lists of `Path` objects sorted by name.

The template receives:
- `dirs` — list of `Path` objects for subdirectories
- `files` — list of `Path` objects for files

Additional routes that the template links to:
- `POST /admin/upload` — file upload
- `POST /admin/delete/<path>` — delete item
- `/` — back to client page (optional link)

---

### File: `app/templates/admin.html`

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="fr">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="viewport" content="width=device-width">
    <title>G3Files — Administration</title>
</head>
<body>
    <h1>G3Files — Administration</h1>

    {% if msg %}
    <p><strong>{{ msg }}</strong></p>
    <hr>
    {% endif %}

    <hr>

    <h2>Fichiers partagés</h2>

    {% if not dirs and not files %}
    <p><em>Aucun fichier partagé.</em></p>
    {% endif %}

    {% if dirs or files %}
    <table border="1" cellpadding="4" cellspacing="0" width="100%">
        <tr>
            <th>Nom</th>
            <th>Type</th>
            <th>Action</th>
        </tr>
        {% for d in dirs %}
        <tr>
            <td><strong>{{ d.name }}/</strong></td>
            <td>Dossier</td>
            <td>
                <form action="{{ url_for('delete', filename=d.name) }}" method="post" style="display:inline;">
                    <button type="submit">&#128465; Supprimer</button>
                </form>
            </td>
        </tr>
        {% endfor %}
        {% for f in files %}
        <tr>
            <td>{{ f.name }}</td>
            <td>Fichier</td>
            <td>
                <form action="{{ url_for('delete', filename=f.name) }}" method="post" style="display:inline;">
                    <button type="submit">&#128465; Supprimer</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}

    <hr>

    <h2>Ajouter des fichiers</h2>

    <form action="/admin/upload" method="post" enctype="multipart/form-data">
        <p>
            <label for="file-files">Fichier(s) :</label>
            <input type="file" name="file" id="file-files" multiple>
        </p>
        <p>
            <button type="submit">Uploader</button>
        </p>
    </form>

    <form action="/admin/upload" method="post" enctype="multipart/form-data">
        <p>
            <label for="file-dir">Dossier :</label>
            <input type="file" name="file" id="file-dir" webkitdirectory mozdirectory msdirectory odirectory directory multiple>
        </p>
        <p>
            <button type="submit">Uploader le dossier</button>
        </p>
    </form>

    <hr>

    <p><a href="{{ url_for('client_index') }}">&#8592; Retour à l'interface client</a></p>

</body>
</html>
```

---

### Key Design Decisions

1. **No JavaScript** — all interactions use HTML forms with `POST`
2. **`border="1"` on table** — ensures visible borders even on very old browsers that ignore CSS
3. **`cellpadding` and `cellspacing`** — classic HTML table attributes for spacing
4. **`style="display:inline"`** on delete forms — keeps delete buttons inline with text; this is inline CSS which works on all browsers (not modern CSS like flex/grid)
5. **Unicode trash icon** — uses `&#128465;` (🗑) which renders as text; falls back to garbage/box on very old browsers but remains readable
6. **Two separate forms** — one for files (`multiple` attribute), one for directories (`webkitdirectory` attribute)
7. **`enctype="multipart/form-data"`** — required for file upload
8. **Empty state** — shows "Aucun fichier partagé" when no files
9. **Link to client page** — bottom link for navigation

### Edge Cases

1. **No files** — empty state message shown
2. **Special characters in filenames** — Jinja2 auto-escapes `{{ d.name }}` by default (safe with `|e`); Flask's `url_for` not used because we need dynamic path segments
3. **Long filenames** — table width 100% handles overflow by wrapping
4. **Very old browser without UTF-8** — trash icon may not render but text "Supprimer" is also present

### Testing

Manual testing after `docker compose up`:
1. Visit `/admin` — should get auth prompt
2. Login with admin/admin — see empty table with "Aucun fichier partagé"
3. Upload a file — file appears in table with delete button
4. Create a directory via webkitdirectory upload — directory appears with delete button
5. Click delete — file/directory disappears
6. Test with non-ASCII filenames — should display correctly

### Exit Criteria

- [ ] File renders without errors in Netscape 4 / IE 5 / Classilla
- [ ] Delete buttons submit POST to `/admin/delete/<name>`
- [ ] Two upload forms: one for files, one for directories
- [ ] Empty state renders correctly
- [ ] Table shows dirs before files, sorted by name
- [ ] Link to `/` present
