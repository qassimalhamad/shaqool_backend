import datetime
import os
import enum
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, Enum , DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define the base class for SQLAlchemy models
Base = declarative_base()

# Define Enums for User types, Categories, and Services
class UserEnum(enum.Enum):
    customer = 'customer'
    provider = 'provider'
    admin = 'admin'

class CategoryEnum(enum.Enum):
    home_repairs = 'home_repairs'
    cleaning = 'cleaning'
    gardening = 'gardening'

class ServiceEnum(enum.Enum):
    plumbing = 'plumbing'
    electrician = 'electrician'
    handyman = 'handyman'
    cleaning = 'cleaning'
    painting = 'painting'
    welding = 'welding'

class BookingStatusEnum(enum.Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'

# Define User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    phone = Column(String)
    address = Column(String)
    user_type = Column(Enum(UserEnum), default=UserEnum.customer)

    # Relationships
    provider_services = relationship("ProviderService", back_populates="user")
    bookings = relationship("Booking", back_populates="customer")

# Define Category model
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(CategoryEnum), unique=True, index=True)
    description = Column(String, nullable=True)
    services = relationship('Service', back_populates='category')

# Define Service model
class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(ServiceEnum), unique=True, index=True)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    # Relationships
    category = relationship('Category', back_populates='services')
    provider_services = relationship("ProviderService", back_populates="service")
class ProviderService(Base):
    __tablename__ = 'provider_services'

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Provider ID from User model
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)  # Service ID from Service model
    price = Column(Integer, nullable=False)  # Price in cents
    description = Column(String, nullable=False)

    # Define relationships
    user = relationship("User", back_populates="provider_services")  
    service = relationship("Service", back_populates="provider_services")

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    provider_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Add this line for provider
    status = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.pending)
    # Relationships
    service = relationship("Service")
    customer = relationship("User", foreign_keys=[customer_id])
    provider = relationship("User", foreign_keys=[provider_id])


# Function to get environment variables
def get_env_variable(var_name, default_value=None):
    """Get the environment variable or return a default value."""
    return os.getenv(var_name, default_value)

# Create a database engine
engine = create_engine(
    f"postgresql://{get_env_variable('POSTGRES_USER')}:{get_env_variable('POSTGRES_PASSWORD')}@{get_env_variable('POSTGRES_HOST')}:{get_env_variable('POSTGRES_PORT', '5432')}/{get_env_variable('POSTGRES_DBNAME')}",
    echo=True
)

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def insert_initial_data(session):
    # Insert categories
    categories = [category for category in CategoryEnum]
    for category in categories:
        if not session.query(Category).filter(Category.name == category).first():
            new_category = Category(name=category)
            session.add(new_category)

    session.commit()  # Commit after adding categories

    # Insert services
    services = [
        ('plumbing', 'Plumbing services', CategoryEnum.home_repairs),
        ('electrician', 'Electrical services', CategoryEnum.home_repairs),
        ('handyman', 'Handyman services', CategoryEnum.home_repairs),
        ('cleaning', 'Cleaning services', CategoryEnum.cleaning),
        ('painting', 'Painting services', CategoryEnum.cleaning),
        ('welding', 'Welding services', CategoryEnum.gardening)
    ]
    for service_name, description, category_enum in services:
        if not session.query(Service).filter(Service.name == ServiceEnum[service_name]).first():
            # Get the category ID for each service
            category = session.query(Category).filter(Category.name == category_enum).first()
            if category:
                new_service = Service(name=ServiceEnum[service_name], description=description, category_id=category.id)
                session.add(new_service)

    session.commit()  # Commit after adding services

# Populate initial data
session = SessionLocal()
try:
    insert_initial_data(session)
except Exception as e:
    print(f"Error inserting initial data: {str(e)}")
finally:
    session.close()
