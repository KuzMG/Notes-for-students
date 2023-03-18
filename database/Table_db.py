from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship

engine = create_engine("postgresql://postgres:qwe321loi@127.0.0.1/scheduleBD")



class Base(DeclarativeBase): pass

class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    group = Column(String)
    days_of_week = relationship("DaysOfWeek", back_populates="schedule", cascade="all, delete-orphan")


class DaysOfWeek(Base):
    __tablename__ = "days_of_week"
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String)
    schedule_id = Column(Integer, ForeignKey("schedule.id"))
    schedule = relationship("Schedule", back_populates="days_of_week")
    pair_number = relationship("PairNumber", back_populates="day_of_week", cascade="all, delete-orphan")


class PairNumber(Base):
    __tablename__ = "pair_number"
    id = Column(Integer, primary_key=True, index=True)
    pair_number = Column(Integer)
    date = Column(String)
    day_of_week_id = Column(Integer, ForeignKey("days_of_week.id"))
    day_of_week = relationship("DaysOfWeek", back_populates="pair_number")
    parity = relationship("ParityOfWeek", back_populates="pair_number", cascade="all, delete-orphan")


class ParityOfWeek(Base):
    __tablename__ = "parity_of_week"
    id = Column(Integer, primary_key=True, index=True)
    parity = Column(Boolean)
    pair_number_id = Column(Integer, ForeignKey("pair_number.id"))
    pair_number = relationship("PairNumber", back_populates="parity")
    pair = relationship("Pair", back_populates="parity_of_week", cascade="all, delete-orphan")


class Pair(Base):
    __tablename__ = "pair"
    id = Column(Integer, primary_key=True, index=True)
    discipline = Column(String)
    occupation = Column(String)
    name_of_the_teacher = Column(String)
    number_of_cabinet = Column(String)
    parity_of_week_id = Column(Integer, ForeignKey("parity_of_week.id"))
    parity_of_week = relationship("ParityOfWeek", back_populates="pair")

#
# создаем таблицы
Base.metadata.create_all(bind=engine)

print("База данных и таблица созданы")
