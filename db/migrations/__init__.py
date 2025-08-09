# Migrations package 
from .base import migration_manager

# Import and register migrations using importlib to avoid invalid decimal literal in module names
import importlib

for mod in (
    'db.migrations.001_initial_schema_consolidated',
    'db.migrations.002_fix_food_entries_schema',
    'db.migrations.003_increase_image_url_length',
    'db.migrations.004_replicache_state',
):
    try:
        importlib.import_module(mod)
    except Exception:
        pass