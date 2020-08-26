from cmdb.model.models import session, Schema,Field,Entity,Value,FieldMeta,Refrence
import logging
import math

from cmdb.types import get_instance
from cmdb.util.utils import getlogger
logger = getlogger(__name__, 'd:/{}.log'.format(__name__))
def get_schema_by_name(name:str, deleted:bool=False):
    query = session.query(Schema).filter(Schema.name == name.strip())
    if not deleted:
        query = query.filter(Schema.deleted == False)
    return query.first()

def add_schema(name, desc=None):
    schema = Schema()
    schema.name = name
    schema.desc = desc
    session.add(schema)
    try:
        session.commit()
        return schema
    except Exception as e:
        session.rollback()
        logger.error('Failed to add a new schema {}.Error:{}'.format(name, e))
def delete_schema(id:int):
    try:
        schema = session.query(Schema).filter((Schema.id == id) & (Schema.deleted == False)).first()
        if schema:
            schema.deleted = True
            session.add(schema)
            try:
                print(schema)
                session.commit()
                return schema
            except Exception as e:
                session.rollback()
                raise e
        else:
            raise ValueError('Wrong ID {}'.format(id))
    except Exception as e:
        logger.error('Fail to delete a schema. id={}.Error:{}'.format(id,e))

def paginate(page, size, query):
    try:
        page = page if page>0 else 1
        size = size if 0<size<102 else 20
        count = query.count()
        pages =  math.ceil(count/size)
        result = query.limit(size).offset(size*(page-1)).all()
        return result,(page, size, count, pages)
    except Exception as e:
        logger.error("{}".format(e))

def list_schema(page:int=1, size:int=20, deleted:bool=False):
    query = session.query(Schema)
    if not deleted:
        query = query.filter(Schema.deleted == False)
    return paginate(page, size, query)
# result, (page, size, count, pages)  = list_schema()
# print(result[1].name, page, size, pages)

def get_field(schema_name, field_name, deleted=False):
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('{} is not a tablename'.format(schema_name))
    query = session.query(Field).filter((Field.schema_id  == schema.id) & (Field.name == field_name))
    if not deleted:
        query=query.filter(Field.deleted==False)
    return query.first()
# query = get_field('host', 'hostname2')
# print(query)

def table_used(schema_id, deleted=False):
    query = session.query(Entity).filter(Entity.schema_id == schema_id)
    if not deleted:

        query=query.filter(deleted==False)
        print(query.first())
    return query.first() is not None

def _add_field(field:Field):
    session.add(field)
    try:
        session.commit()
        return field
    except Exception as e:
        session.rollback()
        logger.error('Fail to add a field {}.Error:{}'.format(field.name, e))

def add_field(schema_name, name, meta):
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('{} is not a tablename'.format(schema_name))
    meta_data = FieldMeta(meta)
    # print(meta_data)
    # print(meta_data.reference, meta_data.instance)
    field = Field()
    field.name=name.strip()
    field.schema_id = schema.id
    field.meta=meta
    if meta_data.reference:
        print(meta_data.nullable)
        ref = get_field(meta_data.reference.schema, meta_data.reference.field)
        if not ref:
            raise TypeError('Wrong Reference {}.{}'.format(meta_data.reference.schema, meta_data.reference.field))
        field.ref_id = ref.id
    if not table_used(schema.id):
        return _add_field(field)
    if meta_data.nullable:
        return _add_field(field)
    if meta_data.unique:
        raise TypeError('this field is required an unique')
    if not meta_data.default:
        raise TypeError('this field is required an default')
    else:
        entities = session.query(Entity).filter((Entity.schema_id==schema.id) & (Entity.deleted==False)).all()
        for entity in entities:
            value = Value()
            value.entity_id = entity.id
            value.field=field
            value.value= meta_data.default
            session.add(value)
        return _add_field(field)
def delete_field(id:int, field_name):
    field = session.query(Field).filter((Field.schema_id == id) & (Field.name==field_name)& (Field.deleted == False)).first()
    if field:
        field.deleted = True
        session.add(field)
        try:
            print(field)
            session.commit()
            return field
        except Exception as e:
            session.rollback()
            raise e
    else:
        raise ValueError('Wrong ID {}'.format(id))
    # except Exception as e:
    #     logger.error('Fail to delete a schema. id={}.Error:{}'.format(id,e))

def get_entity(schema_name, deleted=False):
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('{} is not a tablename'.format(schema_name))
    query = session.query(Entity).filter((Entity.schema_id == schema.id))
    if not deleted:
        query = query.filter(Field.deleted == False)
    return query.first()
def list_entity(schema_name,page:int=1, size:int=20, deleted=False):
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('{} is not a tablename'.format(schema_name))
    query = session.query(Entity).filter((Entity.schema_id == schema.id))
    if not deleted:
        query = query.filter(Field.deleted == False)
    return paginate(page, size, query)
def list_entity_all(schema_name, deleted=False):
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError('{} is not a tablename'.format(schema_name))
    query = session.query(Entity).filter((Entity.schema_id == schema.id))
    if not deleted:
        query = query.filter(Field.deleted == False)
        result = query.all()
    return query.all()
def list_value(schema_name, deleted=False):
    result = list_entity_all(schema_name)
    print(len(result))
    for entity in result:

        query = session.query(Value).filter((Value.entity_id == entity.id))
        if not deleted:
            query = query.filter(Value.deleted == False)
        yield from query.all()

meta = """
{
    "type":{
        "name":"cmdb.types.Int",
        "option":{
            "min":10,
            "max":30
        }
    },
    "reference":{
        "schema":"host",
        "field":"hostname",
        "on_delete":"enable",
        "on_update":"enable"
    },
    "default":123
}
"""


# add_field('host','count2',meta)
# delete_schema(3)
# add_schema('test')

# delete_schema(2)

# field = get_field('host', 'hostname')
# print(field.id)
#
# get_value('ippool')

# delete_field(1, 'hostname')

result=list_value('host')
for i in result:
    print(i.id, i.value)