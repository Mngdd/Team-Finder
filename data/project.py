import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Project(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'project'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    collaborators = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    tags = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)

    users = orm.relationship("User")

    def __repr__(self):
        return
