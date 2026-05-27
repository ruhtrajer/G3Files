# Task 3: Client Template (client.html) — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create `client.html` — the client-facing file list page compatible with very old browsers (Netscape 4, IE 5, Classilla).

**Architecture:** Jinja2 template rendered by Flask's `render_template("client.html", dirs=dirs, files=files)`. No JavaScript, no modern CSS, HTML 4.01 Transitional. Auto-refresh every 10 seconds via `<meta http-equiv="refresh">`.

**Tech Stack:** Flask / Jinja2, HTML 4.01 Transitional

**Prior Work:**
- Task 1 plan: `.opencode/artifacts/2026-05-27-task1-docker-flask-plan.md`
- Task 2 plan: `.opencode/artifacts/2026-05-27-task2-admin-template-plan.md`

---

### Context

The `client_index()` route does:
```python
@app.route("/")
def client_index():
    dirs, files = list_shared_items()
    return render_template("client.html", dirs=dirs, files=files)
```

Where `list_shared_items()` returns `(dirs, files)` — lists of `Path` objects sorted by name.

Download route:
```python
@app.route("/dl/<path:filename>")
def download(filename):
    # Returns file or .tar.gz of directory
```

The template receives:
- `dirs` — list of `Path` objects for subdirectories
- `files` — list of `Path` objects for files

### Design Constraints (from spec)

1. **No JavaScript** — all links are `<a href="/dl/...">` — no onclick, no event handlers
2. **No modern CSS** — no flexbox, no grid, no CSS3
3. **HTML 4.01 Transitional** — backward-compatible doctype
4. **Auto-refresh** — `<meta http-equiv="refresh" content="10">` reloads page every 10s
5. **Table layout** — `<table border="1">` with basic attributes
6. **Old browser compat** — must render on Netscape 4, IE 5, Classilla (no JS, no modern features)
7. **Directory download** — clicking a directory downloads `.tar.gz` via `/dl/<dirname>`

### File: `app/templates/client.html`

```html
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="fr">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta http-equiv="refresh" content="10">
    <title>G3Files</title>
</head>
<body>
    <h1>G3Files — Fichiers partagés</h1>

    <hr>

    <p><a href="{{ url_for('admin_index') }}">Administration</a></p>

    <hr>

    {% if not dirs and not files %}
    <p><em>Aucun fichier partagé pour le moment.</em></p>
    {% endif %}

    {% if dirs or files %}
    <table border="1" cellpadding="4" cellspacing="0" width="100%">
        <tr>
            <th>Nom</th>
            <th>Type</th>
            <th>Taille</th>
            <th>Téléchargement</th>
        </tr>
        {% for d in dirs %}
        <tr>
            <td><strong>{{ d.name }}/</strong></td>
            <td>Dossier</td>
            <td align="right">—</td>
            <td align="center"><a href="{{ url_for('download', filename=d.name) }}">&#128229; Télécharger (.tar.gz)</a></td>
        </tr>
        {% endfor %}
        {% for f in files %}
        {% set size = f.stat().st_size %}
        <tr>
            <td>{{ f.name }}</td>
            <td>Fichier</td>
            <td align="right">
                {% if size < 1024 %}
                    {{ size }} o
                {% elif size < 1048576 %}
                    {{ (size / 1024)|round(1) }} Ko
                {% elif size < 1073741824 %}
                    {{ (size / 1048576)|round(1) }} Mo
                {% else %}
                    {{ (size / 1073741824)|round(1) }} Go
                {% endif %}
            </td>
            <td align="center"><a href="{{ url_for('download', filename=f.name) }}">&#128229; Télécharger</a></td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}

    <hr>

    <p><em>Cette page se rafraîchit automatiquement toutes les 10 secondes.</em></p>

</body>
</html>
```

---

### Key Design Decisions

1. **Auto-refresh** — `<meta http-equiv="refresh" content="10">` causes page to reload every 10s (standard HTML 4, works on all old browsers)
2. **Download links** — `url_for('download', filename=d.name)` generates proper URL-encoded paths to `/dl/<name>`
3. **Directory indicator** — directory names shown with trailing slash and `(Dossier)` label
4. **Size formatting** — Jinja2 filters for human-readable sizes (o/Ko/Mo/Go); uses `f.stat().st_size` on Path objects
5. **No size for directories** — shown as `—` since .tar.gz is generated on the fly
6. **Admin link** — button linking to `/admin` for admin access (uses `url_for('admin_index')`)
7. **`url_for` everywhere** — ensures proper URL encoding for special characters in filenames
8. **Download icon** — `&#128229;` (📥) as visual indicator; falls back gracefully on old browsers

### Edge Cases

1. **Empty shared directory** — shows "Aucun fichier partagé pour le moment"
2. **Very long filenames** — table cells wrap naturally
3. **Special characters in filenames** — `url_for` handles URL encoding
4. **10-second refresh delay** — may cause flash of empty page on first load; acceptable
5. **Directory with many files** — all rendered in a single table; no pagination (spec doesn't require it)
6. **Files > 2GB** — `st_size` is Python int (unbounded), so math works; formatting still readable
7. **Refresh while downloading** — browser typically continues download even if page refreshes; acceptable

### Testing

Manual testing:
1. Start with empty `shared/` directory — client page shows empty message
2. Add a file to `shared/` — appears in table with download link after refresh
3. Add a subdirectory — appears with `.tar.gz` download link
4. Click file download — file downloads
5. Click directory download — `.tar.gz` downloads
6. Verify page auto-refreshes after 10s
7. Test in Classilla/Netscape 4/IE 5 if available

### Exit Criteria

- [ ] Template renders without errors
- [ ] Auto-refresh meta tag present
- [ ] No JavaScript anywhere in template
- [ ] Files listed with download links
- [ ] Directories listed with `.tar.gz` download links
- [ ] Empty state shown when no files
- [ ] Human-readable file sizes displayed
- [ ] Admin link present
- [ ] Uses `url_for` for all URLs
