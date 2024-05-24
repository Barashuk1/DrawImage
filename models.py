from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, select, Text, and_, desc, func
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, relationship

engine = create_engine('sqlite:///database.db')
DBSession = sessionmaker(bind=engine)
session = DBSession()

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)

class Picture(Base):
    __tablename__ = 'picture'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    user_id: Mapped[str] = mapped_column('user_id', Integer, ForeignKey('user.id'))
    user: Mapped['User'] = relationship(User)


Base.metadata.create_all(engine)