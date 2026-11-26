"""SQLModel table models — import every model module here for Alembic discovery.

Alembic's env.py imports this package so that SQLModel.metadata contains all
tables when autogenerating migrations. Add an import line each time you create
a new model file.
"""

# Step 3 will add:
#   from app.models.user import User  # noqa: F401
#   from app.models.workspace import Workspace  # noqa: F401
#   ...
