import datetime

from django.db.models import Q
from django.db.models.functions import TruncDate
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, GenericAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from records.models import Record, Content
from records.serializer import RecordSerializer, ContentSerializer, RecordCreateSerializer, RecordListQuerySerializer, \
    RandomContentQuerySerializer, RecordListSerializer, CreateRecordSerializer
from accounts.models import CommonProfile
from utils.time import KST


class ContentViewSet(viewsets.GenericViewSet):
    model = Record
    serializer_class = ContentSerializer
    permission_classes = [IsAuthenticated]

    def get_prev_filter(self) -> Q:
        prev = self.request.query_params.get('prev')
        if not prev:
            return Q()
        return ~Q(id=int(prev))

    @swagger_auto_schema(
        operation_summary="랜덤 질문 조회 API",
        query_serializer=RandomContentQuerySerializer
    )
    @action(methods=['GET'], detail=False)
    def random(self, request, *args, **kwargs):
        prev_filter = self.get_prev_filter()
        queryset = Content.objects.filter(
            prev_filter
        ).order_by(
            '?'
        ).first()

        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


@extend_schema(tags=["Record Domain"])
class RecordViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin):
    model = Record
    serializer_class = RecordListSerializer
    permission_classes = [IsAuthenticated]

    def get_target_dates(self) -> (datetime.date, datetime.date):
        q_target_date = self.request.query_params.get('target_date')
        if q_target_date:
            target_date_end = datetime.datetime.strptime(q_target_date, '%Y-%m-%d').date()
        else:
            target_date_end = datetime.datetime.today().astimezone(tz=KST).date()
        target_date_st = target_date_end - datetime.timedelta(days=6)
        return target_date_st, target_date_end

    def get_queryset(self):
        target_date_st, target_date_end = self.get_target_dates()

        queryset = Record.objects.filter(
            profile__user=self.request.user
        ).annotate(
            record_date=TruncDate('created_at', tzinfo=KST)
        ).filter(
            record_date__gte=target_date_st,
            record_date__lte=target_date_end
        ).select_related(
            'content'
        ).order_by(
            'created_at'
        )

        return queryset

    @extend_schema(
        request=RecordCreateSerializer,
        summary="기록 조회 API",
        description="기록을 조회합니다.",
        responses={status.HTTP_200_OK: RecordListSerializer(many=True)},
    )
    @swagger_auto_schema(  # todo: extend_schema 적용
        operation_summary="기록 조회 API",
        query_serializer=RecordListQuerySerializer,
        responses={status.HTTP_200_OK: RecordListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        target_date_st, target_date_end = self.get_target_dates()
        queryset = self.filter_queryset(self.get_queryset())

        serializer = RecordSerializer(queryset, many=True)
        records = serializer.data

        results = []
        while target_date_st <= target_date_end:
            results.append(dict(
                date=target_date_st.strftime('%Y-%m-%d'),
                records=list(filter(
                    lambda x: datetime.datetime.fromisoformat(x.get('created_at')).astimezone(
                        KST).date() == target_date_st,
                    records
                ))
            ))
            target_date_st += datetime.timedelta(days=1)
        return Response(results)

    @extend_schema(
        request=RecordCreateSerializer,
        summary="기록 생성 API",
        description="기록을 생성합니다.",
        responses={status.HTTP_201_CREATED: RecordSerializer},
        exclude=True
    )
    @swagger_auto_schema(  # todo: extend_schema 적용
        operation_summary="기록 생성 API",
        request_body=CreateRecordSerializer,
        responses={status.HTTP_201_CREATED: RecordSerializer(many=True)}
    )
    def create(self, request, *args, **kwargs):
        serializer: CreateRecordSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        content_id = serializer.validated_data.get('content_id')
        text = serializer.validated_data.get('text')

        profile = request.user.common_profile

        record = Record.objects.create(
            content_id=content_id,
            profile=profile,
            text=text
        )

        record_serializer = RecordSerializer(record)

        return Response(record_serializer.data)


# deprecated under


class RandomContentAPIView(GenericAPIView):
    serializer_class = ContentSerializer

    def get_prev_filter(self) -> Q:
        prev = self.request.query_params.get('prev')
        if not prev:
            return Q()
        return ~Q(id=int(prev))

    @swagger_auto_schema(deprecated=True, operation_description="to [GET] api/records/content/random/")
    def get(self, request: Request):
        prev_filter = self.get_prev_filter()
        queryset = Content.objects.filter(
            prev_filter
        ).order_by(
            '?'
        ).first()

        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


class RecordCreateAPIView(CreateAPIView):
    serializer_class = RecordCreateSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        deprecated=True,
        operation_description="to [POST] api/records/"
    )
    def post(self, request: Request, *args, **kwargs):
        serializer: RecordCreateSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        content_id = serializer.validated_data.get('content_id')
        text = serializer.validated_data.get('text')

        profile = CommonProfile.objects.get(name=username)

        record = Record.objects.create(
            content_id=content_id,
            profile=profile,
            text=text
        )

        record_serializer = RecordSerializer(record)

        return Response(record_serializer.data)


class RecordListAPIView(ListAPIView):
    serializer_class = RecordListSerializer
    permission_classes = [IsAuthenticated]

    def get_target_dates(self) -> (datetime.date, datetime.date):
        q_target_date = self.request.query_params.get('target_date')
        if q_target_date:
            target_date_end = datetime.datetime.strptime(q_target_date, '%Y-%m-%d').date()
        else:
            target_date_end = datetime.datetime.today().astimezone(tz=KST).date()
        target_date_st = target_date_end - datetime.timedelta(days=6)
        return target_date_st, target_date_end

    def get_queryset(self):
        target_date_st, target_date_end = self.get_target_dates()

        queryset = Record.objects.filter(
            profile__user=self.request.user
        ).annotate(
            record_date=TruncDate('created_at', tzinfo=KST)
        ).filter(
            record_date__gte=target_date_st,
            record_date__lte=target_date_end
        ).select_related(
            'content'
        ).order_by(
            'created_at'
        )

        return queryset

    def list(self, request, *args, **kwargs):
        target_date_st, target_date_end = self.get_target_dates()
        queryset = self.filter_queryset(self.get_queryset())

        serializer = RecordSerializer(queryset, many=True)
        records = serializer.data

        results = []
        while target_date_st <= target_date_end:
            results.append(dict(
                date=target_date_st.strftime('%Y-%m-%d'),
                records=list(filter(
                    lambda x: datetime.datetime.fromisoformat(x.get('created_at')).astimezone(
                        KST).date() == target_date_st,
                    records
                ))
            ))
            target_date_st += datetime.timedelta(days=1)
        return Response(results)

    @swagger_auto_schema(
        deprecated=True,
        operation_description="to [GET] api/records/",
        query_serializer=RecordListQuerySerializer
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
