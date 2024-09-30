import datetime
import os
import enum
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, Enum, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv
from sqlalchemy.orm import Session 

load_dotenv()

Base = declarative_base()

# Enum definitions
class ServiceStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"

class ServiceCategoryEnum(str, enum.Enum):  
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    CLEANING = "cleaning"
    DELIVERY = "delivery"
    LANDSCAPING = "landscaping"
    PAINTING = "painting"
    CARPENTRY = "carpentry"
    MOVING = "moving"
    ASSEMBLY = "assembly"
    REPAIR = "repair"
    OTHER = "other"

class UserRole(str, enum.Enum):
    PROVIDER = "provider"
    CUSTOMER = "customer"
    ADMIN = "admin"

class ReviewRating(int, enum.Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    CANCELED = "canceled"

# Database models
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String, nullable=True)  
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    services = relationship('Service', back_populates='owner', cascade="all, delete-orphan")
    reviews = relationship('Review', back_populates='user', cascade="all, delete-orphan")
    bookings = relationship('Booking', back_populates='user', cascade="all, delete-orphan")


class ServiceCategoryModel(Base):  
    __tablename__ = 'service_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(ServiceCategoryEnum), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    services = relationship('Service', back_populates='category', cascade="all, delete-orphan")


class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('service_categories.id'))  # Ensure this line exists
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(Enum(ServiceStatus), default=ServiceStatus.OPEN)

    owner = relationship('User', back_populates='services')
    category = relationship('ServiceCategoryModel', back_populates='services')
    reviews = relationship('Review', back_populates='service', cascade="all, delete-orphan")
    bookings = relationship('Booking', back_populates='service', cascade="all, delete-orphan")



class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('services.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    service = relationship('Service', back_populates='bookings')
    user = relationship('User', back_populates='bookings')


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('services.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    rating = Column(Enum(ReviewRating), nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    service = relationship('Service', back_populates='reviews')
    user = relationship('User', back_populates='reviews')


# Load environment variables
def get_env_variable(var_name, default_value=None):
    """Get the environment variable or return a default value."""
    return os.getenv(var_name, default_value)

# Create engine and session
engine = create_engine(
    f"postgresql://{get_env_variable('POSTGRES_USER')}:{get_env_variable('POSTGRES_PASSWORD')}@{get_env_variable('POSTGRES_HOST')}:{get_env_variable('POSTGRES_PORT', '5432')}/{get_env_variable('POSTGRES_DBNAME')}",
    echo=True
)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def insert_service_categories(session: Session):
    for category in ServiceCategoryEnum:
        existing_category = session.query(ServiceCategoryModel).filter(ServiceCategoryModel.name == category.value).first()
        if existing_category is None:
            new_category = ServiceCategoryModel(name=category)
            session.add(new_category)
    session.commit()

def initialize_database():
    session = SessionLocal()
    try:
        insert_service_categories(session)
        print("Service categories inserted successfully.")
    except Exception as e:
        print(f"Error inserting service categories: {e}")
        session.rollback()  # Ensure any changes are rolled back in case of an error
    finally:
        session.close()

initialize_database()
    