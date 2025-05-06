from sqlalchemy import Column, Integer, String, Text
from app.database.database import Base

class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    template_type = Column(String) 