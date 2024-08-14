import datetime
from xmlrpc.client import Boolean
from sqlalchemy import MetaData, Integer, String, TIMESTAMP, ForeignKey,Table,Column,Boolean

metadata= MetaData()

role = Table(
    'role',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String,nullable=False),
)

user = Table(
    'user',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column('email', String, nullable=False),
    Column('hashed_password', String, nullable=False),
    Column('profile_id', Integer , ForeignKey("user.id")),
    Column('is_active',Boolean, default=True, nullable=False),
    Column('is_superuser',Boolean, default=False, nullable=False),
    Column('is_verified',Boolean, default=False, nullable=False),
    Column('role_id',Integer, nullable=False),
)

profile = Table(
    "profile",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("surname", String, nullable=False),
    Column("name", String, nullable=False),
    Column("patronymic", String, nullable=False),
    Column("phone_number", String, nullable=False),
    Column("birth_date", String, nullable=False),
    Column("tg", String, nullable=False),
    Column('user_id', Integer , ForeignKey("profile.id")),
)


auth_token = Table(
    "auth_token",
    metadata,
    Column("id",Integer,primary_key=True, autoincrement=True),
    Column('token', String, nullable=False),
    Column('create', TIMESTAMP, default=datetime.time.utcoffset),
    Column('ip', String, nullable=False),
    Column('device_id', String, nullable=False),
    Column('term', String, nullable=False),
    Column('is_valid', String, nullable=False),
    Column('last_entrance', String, nullable=False),
    Column('user_id', Integer , ForeignKey("user.id")),
)

