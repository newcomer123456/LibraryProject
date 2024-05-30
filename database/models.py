from sqlalchemy import Column, Integer, String

from database.database import Base

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)  
    description = Column(String) 
    num_pages = Column(Integer)

    def __str__(self):
        return f"{self.id=} {self.title=} {self.author=} {self.num_pages=} {self.description=}"
    def __repr__(self):
        return f"{self.id=} {self.title=} {self.author=} {self.num_pages=} {self.description=}"
    
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)  

    def __str__(self):
        return f"{self.id=} {self.username=} {self.password=}"
    def __repr__(self):
        return f"{self.id=} {self.username=} {self.password=}"


