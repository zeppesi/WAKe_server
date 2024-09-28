from typing import _eval_type

from rest_framework.serializers import ReturnDict, DictField, ReturnList

_DefinedDTO = {}
_DTODict = {}
DICT_TYPE = [dict, ReturnDict, DictField]
LIST_TYPE = [list, tuple, ReturnList]

from dtos.social_app import *
from dtos.base import *

for dto_name, dto_cls in _DefinedDTO.items():
    for key, value in dto_cls.dto_fields.items():
        if type(value) is str:
            value = ForwardRef(value)
        dto_cls.dto_fields[key] = _eval_type(value, globals(), globals())
