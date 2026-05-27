# Task 3: Client Template (client.html) — Review

## Issues Found

### Issue 1 — SUGGESTION
**Location:** Size computation in Jinja2

**Problem:** `{{ (size / 1048576)|round(1) }}` — Jinja2's `round` filter uses Python's `round()` which does bankers' rounding. For file sizes this is negligible. Acceptable.

### Issue 2 — SUGGESTION
**Location:** Style attribute on form button

**Problem:** `style="margin-bottom: 1em;"` — Netscape 4 may not support the `em` unit (it was introduced in CSS2 but Netscape 4 had limited CSS support). However, `margin-bottom` not being supported has no visible negative impact — the admin link still works. **No change needed.**

### Issue 3 — SUGGESTION
**Location:** `stat()` calls in template

**Problem:** Calling `f.stat().st_size` inside a Jinja2 loop makes a syscall per file. With thousands of files this could be slow. However, for a home file sharing app this is acceptable. The alternative (pre-computing sizes in the route) would add complexity. Leave as-is.

### Issue 4 — REQUIRED
**Location:** Admin link uses a `<form>` with `<button>`

**Problem:** This works, but using a simple `<a href="...">` link is more compatible with very old browsers and more semantic. The current form approach works but is unnecessarily complex. Change to a simple link.

**Fix:** Replace:
```html
<form action="/admin" method="get" style="margin-bottom: 1em;">
    <button type="submit">Administration</button>
</form>
```
With:
```html
<p><a href="{{ url_for('admin_index') }}">Administration</a></p>
```

### Issue 5 — SUGGESTION
**Location:** Unicode download icon `&#128229;`

**Problem:** Netscape 4 and very old IE may not render this Unicode character. It will show as a missing glyph box. The text "Télécharger" is also present, so the link remains understandable. **No change needed.**

---

## Verdict

**READY** — No BLOCKING issues. Issue 4 (admin link) is a minor REQUIRED fix.

## Required Fix

Change admin link from form+button to simple anchor tag.

---

## Round 2 — Re-review

### Fix 1: Applied ✓
Admin link changed from `<form>`+`<button>` to simple `<a href="{{ url_for('admin_index') }}">`.

## Verdict (Round 2)

**READY** — All issues resolved.
