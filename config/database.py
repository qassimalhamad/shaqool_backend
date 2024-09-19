import os
import enum

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, Enum, Float, Text,TIMESTAMP, Boolean, func 

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

from dotenv import load_dotenv

load_dotenv()


class UserEnum(enum.Enum):
    customer = 'customer'
    provider = 'provider'
    admin = 'admin'

class ServiceEnum(enum.Enum):
    plumbing = 'plumbing'
    electrician = 'electrician'
    handyman = 'handyman'
    cleaning = 'cleaning'
    painting = 'painting'
    gardening = 'gardening'
    welding = 'welding'

Base = declarative_base()

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
    services = relationship('Service', back_populates='provider')
    bookings = relationship('Booking', back_populates='customer')

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(ServiceEnum), nullable=False)
    description = Column(String)
    provider_id = Column(Integer, ForeignKey('users.id'))

    # Relationships
    provider = relationship('User', back_populates='services')
    bookings = relationship('Booking', back_populates='service')

class BookingEnum(enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    completed = 'completed'
    canceled = 'canceled'

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey('services.id'))
    customer_id = Column(Integer, ForeignKey('users.id'))
    booking_date = Column(TIMESTAMP, nullable=False)
    status = Column(Enum(BookingEnum), default=BookingEnum.pending)

    # Relationships
    service = relationship('Service', back_populates='bookings')
    customer = relationship('User', back_populates='bookings')



def get_env_variable(var_name, default_value=None):
    """Get the environment variable or return a default value."""
    return os.getenv(var_name, default_value)

engine = create_engine(
    f"postgresql://{get_env_variable('POSTGRES_USER')}:{get_env_variable('POSTGRES_PASSWORD')}@{get_env_variable('POSTGRES_HOST')}:{get_env_variable('POSTGRES_PORT', '5432')}/{get_env_variable('POSTGRES_DBNAME')}",
    echo=True
)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)