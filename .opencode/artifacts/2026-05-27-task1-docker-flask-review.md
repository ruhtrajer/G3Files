# Task 1: Docker + Flask Backend — Review

## Review Process
Compared each proposed file against the spec requirements and project conventions.

## Issues Found

### Issue 1 — BLOCKING
**Location:** `app/server.py` — `list_shared_items()` function

**Problem:** The spec says the admin page shows "Icône poubelle à côté de chaque élément" and the client page has "Icône de téléchargement à côté de chaque élément". The `list_shared_items()` returns `Path` objects. The templates need more than just paths — they need to know if an item is a file or directory to render icons. The current approach passes `Path` objects which can be checked with `.is_dir()` in templates, but `client.html` also needs to differentiate download icon vs tar.gz icon. This is fine as-is since Jinja can call `.is_dir()`.

However, the template needs `dirs` and `files` as already separated — this is correct. **No change needed**, the separation is already done. Marking as SUGGESTION instead.

### Issue 2 — REQUIRED
**Location:** `app/server.py` — `make_tar_gz_for_download()` function

**Problem:** `send_file` with `download_name` parameter requires Flask >= 2.0. The requirements.txt pins Flask==3.0.0, so this is fine. But the `download_name` parameter was added in Flask 2.0 — confirmed OK.

**Fix:** None needed. Verified.

### Issue 3 — REQUIRED
**Location:** `app/server.py` — `upload()` function

**Problem:** When a directory is uploaded via the HTML form with `webkitdirectory`, the browser sends multiple files with paths like `subdir/file.txt`. The current code creates `dest.parent.mkdir(parents=True, exist_ok=True)` and saves at `dest`, but it also does `safe_name = safe_name.lstrip("/").lstrip(".")`. The `.lstrip(".")` will only strip leading dots, not leading `./` or `../`. For example, `../foo` would become `foo` (strips the first `.` then the `/` is gone). But `./foo` would become `/foo` after `.lstrip`. Actually `lstrip("/")` on `./foo` gives `.foo`, then `lstrip(".")` gives `foo`. That works by accident.

A more robust approach would be to use `os.path.normpath` to resolve the path and verify it stays within `SHARED_DIR`.

**Fix:** Replace sanitization logic with normpath + prefix check.

### Issue 4 — REQUIRED
**Location:** `app/server.py` — `requires_auth` decorator

**Problem:** The `requires_auth` decorator uses `functools.wraps` correctly. However, the spec says "l'interface admin est protégée par mot de passe (HTTP Basic Auth), les fichiers partagés ne sont pas accessibles sans auth." The `/dl/` route is NOT protected — this is correct per spec, as the client page needs to download files without auth. All `/admin/*` routes are protected. **Verified correct.**

### Issue 5 — SUGGESTION
**Location:** `Dockerfile`

**Problem:** The Dockerfile uses `python:3.11-slim` but any version >= 3.8 would work. Using a more specific version or `python:3-slim` could be simpler. But 3.11 is fine.

**Fix:** Optional — pin to last LTS for reproducibility.

## Verdict

**NEEDS FIXES** — Issue 3 (upload path sanitization) is REQUIRED.

## Required Fix

In `upload()` function in `app/server.py`:

Replace:
```python
safe_name = filename.replace("\\", "/")
safe_name = safe_name.lstrip("/").lstrip(".")
dest = SHARED_DIR / safe_name
dest.parent.mkdir(parents=True, exist_ok=True)
f.save(dest)
```

With:
```python
safe_name = filename.replace("\\", "/").lstrip("/")
# Normalize path and ensure it stays within shared dir
normalized = os.path.normpath(safe_name)
if normalized.startswith("..") or normalized.startswith("/"):
    return "Invalid path", 400
dest = SHARED_DIR / normalized
dest.parent.mkdir(parents=True, exist_ok=True)
f.save(dest)
```

This properly blocks `../` traversal and absolute paths.

---

## Round 2 — Re-review

### Fix 1: Applied ✓
Upload path sanitization updated to use `os.path.normpath` + prefix check instead of fragile `lstrip` approach.

## Verdict (Round 2)

**READY** — All issues resolved.
