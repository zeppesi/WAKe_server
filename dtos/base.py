import copy
import typing
from dataclasses import dataclass, field
from typing import Union, Optional, get_origin, get_args, Any, ForwardRef, _TypedDictMeta

from drf_spectacular.plumbing import ResolvedComponent, get_openapi_type_mapping
from drf_spectacular.types import PYTHON_TYPE_MAPPING
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from typeguard import check_type

from dtos import _DefinedDTO, DICT_TYPE, LIST_TYPE, _DTODict

if typing.TYPE_CHECKING:
    from WAKe_server.settings.base_schema import DTOSchema


class ErrorStatus:
    http_status: int
    error_code: int  # "-" 생략해주세요.
    error_msg: str

    def __init__(self, http_status, error_code, error_msg=''):
        self.http_status = http_status
        self.error_code = min(error_code, error_code * -1)
        self.error_msg = error_msg

    def as_md(self, error_msg=None, description=None):
        md = f'> **{description}**\n\n'
        md += '```\n{\n'
        md += f'\t"status_code": {self.http_status},\n'
        md += f'\t"code": {self.error_code},\n'
        md += f'\t"erros": "{error_msg or self.error_msg}"\n'
        md += '}\n'
        md += '```\n'
        return md


class DTOMeta(type):

    def __init__(cls, name, bases, dct):
        super(DTOMeta, cls).__init__(name, bases, cls)

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        setattr(cls, 'func', cls)
        setattr(cls, 'is_DTO', property(lambda self: True))

        cls.dto_fields = {}

        if not hasattr(cls, 'is_DTOResponse'):
            for base in reversed(cls.mro()):
                if hasattr(base, 'dto_fields'):
                    cls.dto_fields.update({
                        key: val for key, val in base.dto_fields.items() if key != 'dto_name' and key != 'dto_fields'
                    })

        if '__annotations__' in namespace:
            cls.dto_fields.update({
                key: val for key, val in namespace['__annotations__'].items() if key != 'dto_name'
            })

        if 'dto_name' in namespace:
            _DefinedDTO[namespace['dto_name'].default] = cls
            _DTODict[name] = cls

        return cls


class BaseDTO(metaclass=DTOMeta):
    dto_fields: dict
    dto_name: str = field(default='base_dto', init=False)

    def __init__(self):
        raise Exception('This is an abstract class')

    def __post_init__(self):
        """
        - enforce type for dto
        - 해당 필드가 지정한 필드타입이 아닌 경우 raise
        """
        for field_name, field_type in self.dto_fields.items():
            check_type(field_name, getattr(self, field_name), field_type)

    @classmethod
    def schema_render(cls, auto_schema: Optional['DTOSchema'] = None):
        responses = {}
        component = ResolvedComponent(
            name=cls.dto_name,
            type=ResolvedComponent.SCHEMA,
            object=cls,
        )
        if component in auto_schema.registry:
            # 이거면 맨 처음이 아님
            return auto_schema.registry[component].ref
        for key, val in cls.dto_fields.items():
            responses[key] = build_type(val, auto_schema)
        component = ResolvedComponent(
            name=cls.dto_name,
            type=ResolvedComponent.SCHEMA,
            object=cls,
            schema={'type': 'object', 'properties': responses}
        )

        auto_schema.registry.register(component)
        return auto_schema.registry[component].ref

    def field_to_dict(self):
        return {field: getattr(self, field) for field in self.dto_fields}


def build_type(schema, auto_schema: Optional['DTOSchema'] = None):
    openapi_type_mapping = get_openapi_type_mapping()
    origin_schema = typing.get_origin(schema)
    if hasattr(schema, 'dto_fields'):
        val: BaseDTO
        return schema.schema_render(auto_schema)
    elif origin_schema is Union:
        return build_union_type(schema, auto_schema)
    elif origin_schema is list:
        return build_array_type(schema, auto_schema)
    elif origin_schema is dict:
        return openapi_type_mapping[PYTHON_TYPE_MAPPING[schema.__origin__]]
    elif type(schema) is ForwardRef:
        return build_forward_value(schema, auto_schema)
    elif type(schema) is _TypedDictMeta:
        return build_typeddict_type(schema, auto_schema)
    else:
        return openapi_type_mapping[PYTHON_TYPE_MAPPING[schema]]


def build_typeddict_type(schema, auto_schema: Optional['DTOSchema'] = None):
    responses = {}
    for key, val in schema.__annotations__.items():
        responses[key] = build_type(val, auto_schema)
    return {'type': 'object', 'properties': responses}


def build_array_type(schema, auto_schema: Optional['DTOSchema'] = None):
    schema = typing.get_args(schema)[0]
    return {'type': 'array', 'items': build_type(schema, auto_schema)}


def build_union_type(schema, auto_schema: Optional['DTOSchema'] = None):
    responses = {}
    union_args: tuple = typing.get_args(schema)
    if type(None) in union_args:
        child_val = list(set(union_args) - {type(None)})[0]
        responses['required'] = False
    else:
        child_val = union_args[0]
    a = build_type(child_val, auto_schema)
    return {**responses, **a}


def build_forward_value(schema: ForwardRef, auto_schema: Optional['DTOSchema'] = None):
    try:
        _schema = schema.__forward_value__
        if _schema is None:
            _schema = _DTODict[schema.__forward_arg__]
        if _schema is None:
            raise Exception()
        return build_type(_schema, auto_schema)
    except:
        '''warning 아직 정의되지 않은 forward value입니다.'''
        return {'type': schema.__forward_arg__}


@dataclass
class BaseInputDTO(BaseDTO):
    dto_type = 'input'


@dataclass
class BaseOutputDTO(BaseDTO):
    dto_type = 'output'


@dataclass
class FailOutputDTO(BaseOutputDTO):
    """
    test에서 일부러 fail을 생성하기 위한 dto입니다.
    """
    id: int

    dto_name: str = field(default='fail', init=False)


def dto_layer(dto_class: typing.Type) -> typing.Callable:
    def wrapper(cls):
        original_init = cls.__init__
        original_new = cls.__new__

        def __init__(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            setattr(self, "dto_class", dto_class)

        def __new__(_cls, *args, **kwargs):
            instance = original_new(_cls, *args, **kwargs)
            if not hasattr(instance, 'dto_class'):
                setattr(instance, 'dto_class', dto_class)
            elif getattr(instance, 'dto_class').dto_name != dto_class.dto_name:
                setattr(instance, 'dto_class', dto_class)
            return instance

        cls.__init__ = __init__
        cls.__new__ = __new__
        return cls

    return wrapper


@dataclass
class BaseResponseDTO(BaseDTO):
    """
    해당 클래스를 사용하진 않지만, response format의 약속의 의미로 남겨둠.
    """
    dto_type = 'response'

    results: Union[dict, list, str, None] = None
    errors: Union[list, dict, str, None] = None
    code: Optional[int] = None
    amplitude: Union[list, dict, str, None] = None
    prev: Optional[str] = None
    next: Optional[str] = None
    count: Optional[int] = None


class DTOResponseFormatter:
    @staticmethod
    def run(dto_results: Union[BaseDTO, dict, list, None] = None,
            errors: Union[list, dict, str, None] = None,
            code: Union[int, str, None] = None,
            amplitude: Union[BaseDTO, dict, None] = None,
            count: Optional[int] = None,
            next: Optional[str] = None,
            prev: Optional[str] = None) \
            -> dict:
        rtn = {}
        if dto_results is not None:
            rtn['results'] = dto_results
        if errors is not None:
            rtn['errors'] = errors
        if code is not None:
            rtn['code'] = code
        if amplitude is not None:
            rtn['amplitude'] = amplitude
        if count is not None:
            rtn['count'] = count
        if next is not None:
            rtn['next'] = next
        if prev is not None:
            rtn['prev'] = prev
        return rtn

    @staticmethod
    def error_run(
            error_interface: ErrorStatus,
            error_msg: Optional[str] = None,
            error_code: Optional[int] = None,
            http_code: Optional[int] = None,
    ) -> Response:
        # 편하게 쓰기 위한 함수입니다.
        return Response(
            DTOResponseFormatter.run(
                errors=error_interface.error_msg if error_msg is None else error_msg,
                code=error_interface.error_code if error_code is None else error_code
            ),
            status=error_interface.http_status if http_code is None else http_code
        )

    @staticmethod
    def pagination_run(
            dto_results: Union[BaseDTO, dict, None] = None,
            errors: Union[list, dict, str, None] = None,
            code: Union[int, str, None] = None,
            amplitude: Union[BaseDTO, dict, None] = None,
            count: Optional[int] = None,
            next: Optional[str] = None,
            prev: Optional[str] = None
    ):
        rtn = {}
        rtn['count'] = count
        rtn['prev'] = prev
        rtn['next'] = next
        if dto_results is not None:
            rtn['results'] = dto_results
        if errors is not None:
            rtn['errors'] = errors
        if code is not None:
            rtn['code'] = code
        if amplitude is not None:
            rtn['amplitude'] = amplitude
        return rtn


class DTOFormatter:
    @staticmethod
    def extract_dto_from_List(tp_name: str, tp):
        """
        tp should be formed like under cases
        - List[int], List[str], List[SomeTP] -> (int,), (str,), (SomeTp,)
        - List[Union[Atp, Btp, ~~]] -> (Atp, Btp, ~~)
        - Optional[List[]] -> extract_dto_from_list(tp_name, List[])
        """
        if tp is Any:
            return (Any,)
        tp_origin = get_origin(tp)
        tp_args = get_args(tp)
        if tp_origin == Union:
            return DTOFormatter.extract_dto_from_List(tp_name, tp_args[0])
        if tp_origin == list:
            if get_origin(tp_args[0]) == Union:
                return get_args(tp_args[0])
            return tp_args
        if tp_origin == tuple:
            if get_origin(tp_args[0]) == Union:
                return get_args(tp_args[0])
            return tp_args
        raise Exception(f'{tp_name} is not list type. : {tp}')

    @classmethod
    def _run(cls, dto, dto_class):
        if dto_class == Any:
            return dto
        elif type(dto) in DICT_TYPE:
            for field_name, field_value in dto.items():
                if type(field_value) in DICT_TYPE:
                    child_value_ok = False
                    try:
                        child_dto_class = dto_class.dto_fields.get(field_name)
                    except AttributeError:
                        child_dto_class = dto_class[field_name]
                    if child_dto_class == Any:
                        dto[field_name] = field_value
                        child_value_ok = True
                    elif get_origin(child_dto_class) == Union:
                        for tp_arg in get_args(child_dto_class):
                            try:
                                dto[field_name] = cls._run(field_value, tp_arg)
                                child_value_ok = True
                                break
                            except:
                                pass
                    else:
                        try:
                            dto[field_name] = cls._run(field_value, child_dto_class)
                            child_value_ok = True
                        except:
                            pass
                    if not child_value_ok:
                        raise Exception(f'child_type does not match.\n'
                                        f'parent dto: {dto_class}'
                                        f'child: {field_value}\n'
                                        f'expected type: {child_dto_class}')
                elif type(field_value) in LIST_TYPE:
                    if len(field_value) == 0:
                        dto[field_name] = field_value
                    else:
                        rtn = []
                        try:
                            tp = dto_class.dto_fields.get(field_name)
                        except AttributeError:
                            tp = dto_class.__annotations__.get(field_name)
                        tp_args = cls.extract_dto_from_List(field_name, tp)
                        for child_value in field_value:
                            child_type_ok = False
                            for tp in tp_args:
                                try:
                                    rtn.append(cls._run(child_value, tp))
                                    child_type_ok = True
                                    break
                                except Exception as e:
                                    pass
                            if not child_type_ok:
                                raise Exception(f'child_type does not match.\n'
                                                f'parent dto: {dto_class}\n'
                                                f'child: {child_value}\n'
                                                f'expected type: {tp_args}\n')
                        dto[field_name] = rtn
                else:
                    pass
            return dto_class(**dto)
        elif type(dto) in LIST_TYPE:
            rtn = []
            for arg in dto:
                rtn.append(cls._run(arg, dto_class))
            return rtn
        else:
            check_type(str(dto_class), dto, dto_class)
            return dto

    @classmethod
    def run(cls, dto, dto_class):
        """
        return dto instance from any type
        """
        return cls._run(dto, dto_class)


class DTOChecker:
    @classmethod
    def run(cls, dto, dto_class):
        dto = copy.deepcopy(dto)
        if type(dto) in DICT_TYPE:
            DTOFormatter.run(dto, dto_class)
        elif type(dto) in LIST_TYPE:
            DTOFormatter.run(dto, dto_class)
        elif hasattr(dto, 'dto_name'):
            assert isinstance(dto, dto_class), f'dto {dto} does not match {dto_class}'
        elif issubclass(type(dto), BaseSerializer):
            if not hasattr(dto, 'dto_class'):
                raise Exception(f'"{dto}" does not have decorator dto_layer!\n'
                                f'you have to set decorator @dto_layer(f{dto_class})')
            if not getattr(dto, 'dto_class') is dto_class:
                raise Exception(f'"{dto}" does not match with "{dto_class}"')
            DTOFormatter.run(dto.data, dto_class)
            raise Exception(f'Serializer instance does not accept although type check passed...\n'
                            f'plz, use dto.data or serializer.data')
        else:
            assert type(dto) == dto_class, f'dto {dto} is not match dto_class {dto_class}'
        return True


def DTOResponse(response_dto, many=None):
    @dataclass
    class Run(response_dto):
        if many:
            result_dto = list[response_dto]
        else:
            result_dto = response_dto

        results: result_dto

        dto_name: str = field(default=f'{response_dto.dto_name}_response', init=False)
        is_DTOResponse = True

    return Run


def PaginationDTOResponse(response_dto, many=None):
    @dataclass
    class Run(response_dto):
        if many:
            result_dto = list[response_dto]
        else:
            result_dto = response_dto

        results: Optional[result_dto]
        count: int
        next: Optional[str]
        prev: Optional[str]

        dto_name: str = field(default=f'pagination_{response_dto.dto_name}_response', init=False)
        is_DTOResponse = True

    return Run
