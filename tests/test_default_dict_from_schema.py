
# SCHEMA_4 = schemadict({
#     'time': {
#         'type': str,
#         'default': time_now
#     },
#     'person': {
#         'type': str,
#         'default': 'C.Lindbergh'
#     },
#     'age': {
#         'type': int
#     },
#     'pets': {
#         'type': dict,
#         'schema': {
#             'dog': {'type': bool, 'default': None},
#             'cat': {'type': bool}
#         },
#     },
# })

# def test_default_value_dict():
#     """Test 'get_default_value_dict()'"""

#     defaults = SCHEMA_1.get_default_value_dict()
#     assert defaults == SCHEMA_1_DEFAULT_VALUE_DICT

#     defaults = SCHEMA_4.get_default_value_dict()
#     assert isinstance(defaults['time'], str)

#     # Time may vary
#     del SCHEMA_4_DEFAULT_VALUE_DICT['time']
#     del defaults['time']

#     assert defaults == SCHEMA_4_DEFAULT_VALUE_DICT


