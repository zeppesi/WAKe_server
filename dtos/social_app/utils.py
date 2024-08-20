import re
from typing import Any, List

from django.db import models

output_dto_field_mapping = {
    models.BigAutoField: int,
    models.AutoField: int,
    models.BigIntegerField: int,
    models.BooleanField: bool,
    models.CharField: str,
    models.CommaSeparatedIntegerField: str,
    models.DateField: float,
    models.DateTimeField: float,
    #     models.DecimalField: DecimalField,
    #     models.DurationField: DurationField,
    models.EmailField: str,
    #     models.Field: ModelField,
    #     models.FileField: FileField,
    models.FloatField: str,
    models.ImageField: Any,
    models.IntegerField: int,
    models.NullBooleanField: bool,
    models.PositiveIntegerField: int,
    models.PositiveSmallIntegerField: int,
    #     models.SlugField: SlugField,
    models.SmallIntegerField: int,
    models.TextField: str,
    models.TimeField: float,
    models.URLField: str,
    #     models.UUIDField: UUIDField,
    #     models.GenericIPAddressField: IPAddressField,
    #     models.FilePathField: FilePathField,
}


def get_model_basic_fields(model: models.Model) -> List[models.Field]:
    return list(filter(lambda field: field.related_model is None, [field for field in model._meta.get_fields()]))


def model_field_to_python_type(field_class: models.fields.Field):
    return output_dto_field_mapping.get(field_class)


def pascal_to_snake(pascal_str: str) -> str:
    snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', pascal_str).lower()
    return snake_str

def print_model_to_output_dto(model: models.Model):
    class_name = model._meta.object_name
    class_name_to_snake_case = pascal_to_snake(class_name)
    fields = get_model_basic_fields(model)

    print('@dataclass')
    print(f'class {class_name}OutputDTO(BaseOutputDTO):')
    for field in fields:
        field_name = field.attname
        allow_null = field.null
        model_field_type = type(field)
        python_type = model_field_to_python_type(model_field_type)
        python_type_name = python_type.__name__
        if allow_null:
            python_type_name = f'Optional[{python_type_name}]'
        print(f'    {field_name}: {python_type_name}')

    print(f'\n    dto_name: str = field(default="{class_name_to_snake_case}_output_dto", init=False)')
