# Task 2: Admin Template (admin.html) — Review

## Issues Found

### Issue 1 — BLOCKING
**Location:** Delete form action URLs

**Problem:** When a filename contains special characters (spaces, `?`, `&`, `/`, `#`), the URL `/admin/delete/{{ d.name }}` will break. For example, a file named `foo bar.txt` would POST to `/admin/delete/foo bar.txt` which is an invalid URL. The `POST` method doesn't encode the filename in the URL body, but the URL itself needs to be properly encoded. Jinja2's `{{ d.name }}` auto-escapes HTML entities but does NOT URL-encode for path segments. Need to use `{{ d.name | urlencode }}` or Flask's `url_for`.

However, `url_for('delete', filename=d.name)` would correctly encode the path. Since the route is `@app.route("/admin/delete/<path:filename>")`, Flask's `url_for` with `filename=d.name` will produce a properly encoded URL.

**Fix:** Delete forms should use `{{ url_for('delete', filename=d.name) }}` instead of hardcoded `/admin/delete/{{ d.name }}`.

Similarly, the link to client page should use `url_for('client_index')`.

### Issue 2 — BLOCKING
**Location:** Delete action for directories

**Problem:** The delete form submits `POST /admin/delete/{{ d.name }}`. For a directory named `my folder/`, the trailing slash is part of the directory name on the filesystem. The `d.name` from a `Path` object does NOT include a trailing slash. So `d.name` for a directory is just `my folder`. But the URL path segment `my folder` (even URL-encoded) maps correctly to `<path:filename>` in Flask. So the filename passed to the `delete()` route will be `my folder`. That's correct.

BUT wait — if a directory is named with a trailing space or special characters, `Path.name` preserves them. URL encoding via `url_for` handles this. **No fix needed.**

### Issue 3 — REQUIRED
**Location:** Delete confirmation

**Problem:** There is no confirmation before deleting. Since the spec says "Icône poubelle à côté de chaque élément pour arrêter le partage (suppression)", the spec does NOT require confirmation. The delete is immediate on form submission. This is acceptable — the spec doesn't mention confirmation. **No change needed.**

### Issue 4 — REQUIRED
**Location:** `style="display:inline"` on form elements

**Problem:** Very old browsers (Netscape 4) may not support `display:inline` via CSS. However, the `style` attribute is HTML 4.01 valid, and `display:inline` was supported since CSS1 (Netscape 4 supported basic CSS). The fallback is that the form would appear on its own line, which is acceptable. **No change needed.**

### Issue 5 — SUGGESTION
**Location:** Upload form — no feedback after upload

**Problem:** The upload and delete actions return `204 No Content` (or error codes). The admin page doesn't show success/error messages. The spec says "Afficher le résultat des actions (succès/erreur)". Need a feedback mechanism.

**Fix:** Modify `server.py` to redirect back to `/admin` with a query parameter or flash message. Since we can't use JS, the simplest approach is a 302 redirect. But the current routes return 204/4xx. Change upload and delete to redirect to `/admin` with a message query param. The template reads `?msg=success` or `?msg=error`.

Actually, the simplest fix without modifying the server.py plan (which is Task 1) is to modify the upload and delete routes to redirect back to `/admin` instead of returning 204. This is a change to `server.py`.

### Issue 6 — SUGGESTION
**Location:** No message display in admin.html

**Problem:** Even if the server redirects with a message, the template doesn't display it.

**Fix:** Add message handling to admin.html:
```html
{% if msg %}
<p><strong>{{ msg }}</strong></p>
{% endif %}
```

And modify server.py upload/delete to redirect: `redirect(url_for('admin_index', msg='Fichier supprimé'))`

---

## Verdict

**NEEDS FIXES** — Issue 1 (URL encoding for filenames with special chars) is BLOCKING. Issue 5/6 (feedback after actions) is REQUIRED per spec.

## Required Fixes

### Fix 1: Use `url_for` in template action URLs

Replace:
```html
<form action="/admin/delete/{{ d.name }}" method="post" style="display:inline;">
```
With:
```html
<form action="{{ url_for('delete', filename=d.name) }}" method="post" style="display:inline;">
```

And replace:
```html
<form action="/admin/delete/{{ f.name }}" method="post" style="display:inline;">
```
With:
```html
<form action="{{ url_for('delete', filename=f.name) }}" method="post" style="display:inline;">
```

And replace:
```html
<p><a href="/">&#8592; Retour à l'interface client</a></p>
```
With:
```html
<p><a href="{{ url_for('client_index') }}">&#8592; Retour à l'interface client</a></p>
```

### Fix 2: Add message feedback to admin.html

Add after `<h1>`:
```html
{% if msg %}
<p><strong>{{ msg }}</strong></p>
{% endif %}
```

### Fix 3: Modify server.py to redirect with messages

Update upload route to redirect instead of returning 204:
```python
from flask import redirect, url_for

@app.route("/admin/upload", methods=["POST"])
@requires_auth
def upload():
    if "file" not in request.files:
        return redirect(url_for("admin_index", msg="Erreur : aucun fichier sélectionné"))
    f = request.files["file"]
    if f.filename == "":
        return redirect(url_for("admin_index", msg="Erreur : fichier invalide"))
    # ... rest of upload logic ...
    return redirect(url_for("admin_index", msg="Fichier uploadé avec succès"))
```

Update delete route similarly:
```python
@app.route("/admin/delete/<path:filename>", methods=["POST"])
@requires_auth
def delete(filename):
    # ... existing logic ...
    return redirect(url_for("admin_index", msg="Élément supprimé"))
```

---

## Round 2 — Re-review

### Fix 1: Applied ✓
`url_for('delete', filename=d.name)` and `url_for('delete', filename=f.name)` used in both delete forms. Link to client page uses `url_for('client_index')`.

### Fix 2: Applied ✓
Message block added after `<h1>`: `{% if msg %}...{% endif %}`

### Fix 3: Applied ✓
Task 1 plan updated — `upload()` and `delete()` routes now redirect with `msg` query parameter. `admin_index()` passes `msg` to template via `request.args.get("msg")`.

## Verdict (Round 2)

**READY** — All BLOCKING and REQUIRED issues resolved.
