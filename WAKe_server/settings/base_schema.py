from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import ResolvedComponent, build_media_type_object, modify_media_types_for_versioning
from drf_spectacular.utils import OpenApiResponse

from dtos import BaseDTO, ErrorStatus


class DTOSchema(AutoSchema):
    def _get_response_bodies(self, direction='response'):
        response_serializers = self.get_response_serializers()

        if hasattr(response_serializers, 'dto_name'):
            response_serializers: BaseDTO
            component = self.resolve_dto(response_serializers)
            response = {200: {'content': {'application/json': {'schema': component.ref}}}}
            return response
        elif isinstance(response_serializers, dict):
            responses = {}
            for code, serializer in response_serializers.items():
                if isinstance(code, tuple):
                    code, media_types = str(code[0]), code[1:]
                else:
                    code, media_types = str(code), None
                content_response = self._get_response_for_code(serializer, code, media_types, direction)
                if code in responses:
                    responses[code]['content'].update(content_response['content'])
                else:
                    responses[code] = content_response
            return responses

        else:
            response = super()._get_response_bodies(direction)
            return response

    def _get_response_for_code(self, serializer, status_code, media_types=None, direction='response'):
        if hasattr(serializer, 'dto_name'):
            if isinstance(serializer, OpenApiResponse):
                serializer, description, examples = (
                    serializer.response, serializer.description, serializer.examples
                )
            else:
                description, examples = '', []

            serializer: BaseDTO
            component = self.resolve_dto(serializer)
            headers = self._get_response_headers_for_code(status_code, direction)
            headers = {'headers': headers} if headers else {}

            if not media_types:
                media_types = self.map_renderers('media_type')
            media_types = modify_media_types_for_versioning(self.view, media_types)

            return {
                **headers,
                'content': {
                    media_type: build_media_type_object(
                        component.ref,
                        self._get_examples(component, direction, media_type, status_code, examples)
                    )
                    for media_type in media_types
                },
                'description': description
            }
        elif isinstance(serializer, str):
            description, examples = '', []
            serializer: ErrorStatus
            headers = self._get_response_headers_for_code(status_code, direction)
            headers = {'headers': headers} if headers else {}

            if not media_types:
                media_types = self.map_renderers('media_type')
            media_types = modify_media_types_for_versioning(self.view, media_types)

            schema = {
                'type': 'object',
                'properties': {
                    'status_code': {'type': 'integer'},
                    'code': {'type': 'integer'},
                    'errors': {'type': 'string'},
                },
            }

            return {
                **headers,
                'content': {
                    media_type: build_media_type_object(
                        schema,
                        self._get_examples(schema, direction, media_type, status_code, examples)
                    )
                    for media_type in media_types
                },
                'description': serializer
            }

        else:
            super()._get_response_for_code(serializer, '200', media_types, direction)

    def _get_request_body(self, direction='request'):
        if self.method not in ('PUT', 'PATCH', 'POST'):
            return None

        request_serializers = self.get_request_serializer()

        if hasattr(request_serializers, 'dto_name'):
            request_serializers: BaseDTO
            component = self.resolve_dto(request_serializers)
            request = {'content': {'application/json': {'schema': component.ref}}}
            return request
        else:
            request = super()._get_request_body(direction)
            return request

    def resolve_dto(self, dto,) -> ResolvedComponent:
        component = ResolvedComponent(
            name=dto.dto_name,
            type=ResolvedComponent.SCHEMA,
            object=dto,
        )
        if component not in self.registry:
            dto.schema_render(self)

        return self.registry[component]
