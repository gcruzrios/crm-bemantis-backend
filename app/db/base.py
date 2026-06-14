from app.db.base_class import Base  # noqa: F401

# Import all models here so Alembic can detect them
from app.models.user import User          # noqa: F401, E402
from app.models.company import Company    # noqa: F401, E402
from app.models.contact import Contact    # noqa: F401, E402
from app.models.deal import Deal          # noqa: F401, E402
from app.models.service import Service    # noqa: F401, E402
from app.models.quote import Quote        # noqa: F401, E402
from app.models.quote_item import QuoteItem  # noqa: F401, E402
from app.models.activity import Activity  # noqa: F401, E402
