from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from infrastructure.models.base import Base


class TaskEvaluation(Base):
    __tablename__ = 'employee_evaluations'

    id: Mapped[int] = mapped_column(primary_key=True)
    score_quality: Mapped[int]
    task_id: Mapped[int] = mapped_column(
        ForeignKey('tasks.id', ondelete='SET NULL'), unique=True
    )

    task = relationship('Task', back_populates='evaluation')

    __table_args__ = (
        UniqueConstraint('task_id', name='uq_task_id'),
        CheckConstraint('score_quality BETWEEN 1 AND 10', name='chk_score_quality'),
    )

    def __repr__(self):
        return f'<Score {self.score_quality} - task {self.task_id}>'
