from sqlalchemy import Column,Integer, String,Text,Boolean
from sqlalchemy import ForeignKey,UniqueConstraint,create_engine
from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json
from cmdb.types import get_instance
from cmdb.util.utils import getlogger
logger = getlogger(__name__, 'd:/{}.log'.format(__name__)) # 路径自行更换


Base = declarative_base()

class Schema(Base):
    __tablename__ = "schema"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45),nullable=False,unique=True)
    desc = Column(String(128), nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)
    fields = relationship('Field')

class Refrence:
    def __init__(self, ref:dict):
        self.schema = ref['schema']
        self.field = ref['field']
        self.on_delete = ref.get('on_delete', 'disable')
        self.on_update = ref.get('on_update', 'disable')

class FieldMeta:
    def __init__(self, metastr:str):
        meta = json.loads(metastr)
        if isinstance(meta, str):
            self.instance = get_instance(meta)

        else:
            option = meta['type'].get('option')
            if option:
                self.instance = get_instance(meta['type']['name'], **option)
            else:
                self.instance = get_instance(meta['type']['name'])
        self.unique = meta.get('unique', False)
        self.nullable = meta.get('nullable', False)
        self.default = meta.get('default', False)
        self.multi = meta.get('multi', False)
        ref = meta.get('reference')
        if ref:
            self.reference = Refrence(ref)
        else:
            self.reference = None
class Field(Base):
    __tablename__ = "field"
    __table_args__ = (UniqueConstraint('schema_id', 'name'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45),nullable=False)
    schema_id = Column(Integer, ForeignKey('schema.id'), nullable=False)
    meta = Column(Text, nullable=False)
    ref_id = Column(Integer, ForeignKey('field.id'), nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)

    schema = relationship('Schema')
    ref = relationship('Field', uselist=False)
    # @property
    # def meta_data(self):
    #     return FieldMeta(self.meta)

class Entity(Base):
    __tablename__ = "entity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(45),nullable=False)
    schema_id = Column(Integer, ForeignKey('schema.id'), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)

    schema = relationship('Schema')

class Value(Base):
    __tablename__ = "value"
    __table_args__ = (UniqueConstraint('entity_id', 'field_id', name='uq_entity_field'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Text, nullable=False)
    field_id = Column(Integer, ForeignKey('field.id'), nullable=False)
    entity_id = Column(Integer, ForeignKey('entity.id'), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)

    entity = relationship('Entity')
    field = relationship('Field')

engine = create_engine("mysql+pymysql://root:123@127.0.0.1:3306/cmdb2", echo=True)

def create_all():
    Base.metadata.create_all(engine)
def drop_all():
    Base.metadata.drop_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
