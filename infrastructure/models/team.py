from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from infrastructure.models.base import Base
from config.constants import TEAM_NAME_LENGTH


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(TEAM_NAME_LENGTH), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(nullable=True)

    team_lead_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
        unique=True,
    )

    members = relationship('User', back_populates='team', foreign_keys='User.team_id')
    team_lead = relationship(
        'User', back_populates='team_lead', foreign_keys=[team_lead_id]
    )

    __table_args__ = (UniqueConstraint('team_lead_id', name='uq_team_lead'),)

    def __repr__(self):
        return f'<Team: {self.name}, description:{self.description}, team lead id: {self.team_lead_id}>'
