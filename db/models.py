from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Crea un motor de base de datos SQLite3
engine = create_engine("sqlite:///db/ListaDeComprasDB.sqlite3", echo=True)

Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True) # ID único de telegram
    name = Column(String) # Nombre elegido por el usuario
    username = Column(String) # Nombre de usuario (@username)
    
class Item(Base):
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True, autoincrement=True) # ID único para identificar el registro
    user_id = Column(Integer, ForeignKey('users.id')) # ID único del usuario dueño del registro
    name = Column(String) # Texto indicando el producto a comprar

Base.metadata.create_all(engine)