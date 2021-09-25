from sqlalchemy import Column, Integer, String, Table, ForeignKey,create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

style_pic_table = Table('style_pic_table', Base.metadata,
                        Column('style_id', Integer, ForeignKey('style.id', ondelete="CASCADE")),
                        Column('picture_id', Integer, ForeignKey('picture.id', ondelete="CASCADE"))
                        )

shade_pic_table = Table('shade_pic_table', Base.metadata,
                        Column('shade_id', Integer, ForeignKey('shade.id',ondelete='CASCADE')),
                        Column('picture_id', Integer, ForeignKey('picture.id', ondelete="CASCADE"))
                        )


class Style(Base):
    __tablename__ = 'style'
    id = Column(Integer, primary_key=True)
    name = Column(String(31))

    pictures = relationship(
        'Picture',
        secondary=style_pic_table,
        back_populates='styles')


class Shade(Base):
    __tablename__ = 'shade'
    id = Column(Integer, primary_key=True)
    name = Column(String(31))
    pictures = relationship(
        'Picture',
        secondary=shade_pic_table,
        back_populates='shades')


class Picture(Base):
    __tablename__ = 'picture'
    id = Column(Integer, primary_key=True)
    name = Column(String(63))
    ph_url = Column(String(767))
    size = Column(String(127))
    author = Column(String(127))
    price = Column(Integer)
    year = Column(Integer)
    mats = Column(String(63))
    art_styles = Column(String(127))
    shades = relationship(
        'Shade',
        secondary=shade_pic_table,
        back_populates='pictures')
    styles = relationship(
        'Style',
        secondary=style_pic_table,
        back_populates='pictures')