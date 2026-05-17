import re

with open("alembic/env.py", "r") as f:
    env_content = f.read()

env_content = env_content.replace(
    "target_metadata = None",
    "import sys; import os; sys.path.insert(0, os.path.dirname(os.path.dirname(__file__))); from app.core.database import Base; import app.models; target_metadata = Base.metadata"
)

with open("alembic/env.py", "w") as f:
    f.write(env_content)

with open("alembic.ini", "r") as f:
    ini_content = f.read()

ini_content = re.sub(
    r"sqlalchemy\.url = .*",
    "sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/aegisai_db",
    ini_content
)

with open("alembic.ini", "w") as f:
    f.write(ini_content)

print("Alembic configured")
