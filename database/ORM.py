from database.database import engine, Base, session_factory
from database.models import Book, User
from sqlalchemy import and_

class ORM:
    @staticmethod
    def create_tables():
        Base.metadata.create_all(engine)

    @staticmethod
    def drop_tables():
        Base.metadata.drop_all(engine)

    @staticmethod
    def add_record(record):
        with session_factory() as session:
            session.add(record)
            session.commit()

    @staticmethod
    def get_user_by_username(username):
        with session_factory() as session:
            user = session.query(User).filter(User.username == username).first()
            return user
    
    @staticmethod
    def get_user_by_username_and_password(username, password):
        with session_factory() as session:
            user = session.query(User).filter(and_(User.username == username, User.password == password)).first()
            return user
    
    
    @staticmethod
    def remove_book_by_id(id: int) -> bool:
        """Remove a book from the database by its ID."""
        with session_factory() as session:
            res = session.query(Book).get(id)
            if res:
                session.delete(res)
                session.commit()
                return True
            else:
                return False 
            
    @staticmethod
    def get_book_by_title(title):
        with session_factory() as session:
            book = session.query(Book).filter(Book.title == title).first()
            return book 
        
    @staticmethod
    def get_book_by_id(id):
        with session_factory() as session:
            book = session.query(Book).filter(Book.id == id).first()
            return book 

    @staticmethod
    def get_all_books():
        with session_factory() as session:
            books = session.query(Book).all()
            return books