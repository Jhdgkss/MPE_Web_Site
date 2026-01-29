# Migration merge fix (core)

You have two migrations with the same number (0016) in `core`:
- `0016_site_theme_fields`
- `0016_site_theme_navbar`

This patch adds a merge migration so Django has a single leaf node.

## Apply
1. Copy the included `core/migrations/0017_merge_...py` into your project (overwrite if prompted).
2. Run:

```bash
python manage.py migrate
```

Do **not** run `makemigrations --merge` after applying this patch; this patch is the merge.
