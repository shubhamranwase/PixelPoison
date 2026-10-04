from sqlalchemy import Column, Integer, String, DateTime
import datetime
from database import Base

class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    original_filename = Column(String, index=True)
    intensity_level = Column(Integer)
