from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Column, Sequence

dbase = declarative_base()

class UserRegistered(dbase):
    __tablename__ = 'UserRegistered'

    user_id = Column(
        BigInteger, 
        Sequence('user_id', start=1000, increment=1),
        primary_key=True, 
        )
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

class TodoElements(dbase):
    __tablename__ = 'TodoElement'

    id = Column(BigInteger, primary_key=True, nullable=False)
    id_todo = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey("UserRegistered.user_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Boolean, nullable=False, default=False)

    uid = relationship("UserRegistered")