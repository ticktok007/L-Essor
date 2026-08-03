# load_synthetic_data — Usage
**Project:** Campus Innovation & Engagement Intelligence Hub
**Phase:** 2 — Backend Foundation

## Example Commands

```bash
# Default load from data/final/ with chunk size 1000
python manage.py load_synthetic_data

# Custom base directory
python manage.py load_synthetic_data --base-dir /path/to/data/final

# Custom chunk size (smaller batches for debugging)
python manage.py load_synthetic_data --chunk-size 100

# Flush all existing rows then reload (full reset)
python manage.py load_synthetic_data --flush-existing

# Full reset with custom source and chunk size
python manage.py load_synthetic_data --flush-existing --base-dir data/final --chunk-size 500
```

## Safety Notes
- `--flush-existing` deletes ALL rows in reverse FK order before loading.
  Do not run this against any database that has real production data.
- The command targets whatever database is configured in the active Django
  settings module (`DJANGO_SETTINGS_MODULE`). Confirm you are on `dev` before
  running: `echo $DJANGO_SETTINGS_MODULE` should show `campushub.settings.dev`.
- Invalid JSON fields or unresolvable FK IDs raise `CommandError` and roll back
  the current table transaction — previous tables already committed remain loaded.
- Run `python manage.py showmigrations` and confirm all migrations are applied
  before running this command.

## Exit Status
Command ready for immediate use against the dev database.