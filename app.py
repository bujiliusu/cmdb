# jsonstr = """
# {
#     "type":"cmdb.types.Intt",
#     "value":"192.168.1.100",
#     "option": {
#         "prefix":"192.168"
#     }
# }"""
#
# obj = json.loads(jsonstr)
#
#
# print(get_instance(obj['type'], **obj['option']).stringify(obj['value']))

# drop_all()
# create_all()

import json
data1 = {
    'no': 1,
    'name': 'Runoob',
    'url': 'http://www.runoob.com'
}
data1 = "type:wwww"

json_str = json.dumps(data1)
print("Python 原始数据：", repr(data1))
print("JSON 对象：", json_str)
