from datetime import datetime, timezone
from functools import partial
from typing import Any
from uuid import UUID

from sqlalchemy import ARRAY, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

postgres_now = partial(datetime.now, timezone.utc)


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text('uuid_generate_v4()'))

    type_annotation_map = {
        dict[str, Any]: JSONB,  # allows to use Mapped[dict[str, Any]] notation
        list[str]: ARRAY(String),  # allows to use Mapped[list[str]] notation
        list[UUID]: ARRAY(PostgresUUID)  # allows to use Mapped[list[UUID]] notation
    }


class MilestonesAware:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=postgres_now,
                                                 server_default=func.now())
    # updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=postgres_now,
    #                                              server_default=func.now(), onupdate=postgres_now)
