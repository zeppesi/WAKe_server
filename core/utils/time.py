from django.utils import timezone
import datetime
from dateutil.relativedelta import relativedelta
import pytz

KST = datetime.timezone(datetime.timedelta(hours=9))


class TimeManager:
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    WEEKDAY = ('월', '화', '수', '목', '금', '토', '일')

    @classmethod
    def today(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = timezone.localtime(timezone=KST)
        today = timezone.datetime(_from.year, _from.month, _from.day, tzinfo=KST)
        if end:
            today = today + datetime.timedelta(days=1)
        return today

    @classmethod
    def tomorrow(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = timezone.localtime(timezone=KST) + datetime.timedelta(days=1)
        tomorrow = timezone.datetime(_from.year, _from.month, _from.day, tzinfo=KST)
        if end:
            tomorrow = tomorrow + datetime.timedelta(days=1)
        return tomorrow

    @classmethod
    def yesterday(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = timezone.localtime(timezone=KST) - datetime.timedelta(days=1)
        yesterday = timezone.datetime(_from.year, _from.month, _from.day, tzinfo=KST)
        now = _from
        datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, tzinfo=KST)
        if end:
            yesterday = yesterday + datetime.timedelta(days=1)
        return yesterday

    @classmethod
    def before_weekday(cls, _from: datetime = None, end=False):
        """
        _from을 기준으로 해당 요일의 전주를 return
        """
        today = cls.today(_from=_from, end=end)
        return today - datetime.timedelta(days=7)

    @classmethod
    def next_weekday(cls, _from: datetime = None, end=False):
        """
        _from을 기준으로 해당 요일의 차주를 return
        """
        today = cls.today(_from=_from, end=end)
        return today + datetime.timedelta(days=7)

    @classmethod
    def this_monday(cls, _from: datetime = None, end=False):
        today = cls.today(_from=_from, end=end)
        return today - datetime.timedelta(days=today.weekday())

    @classmethod
    def this_month(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = cls.today()
        this_month = datetime.datetime(year=_from.year, month=_from.month, day=1, tzinfo=KST)
        if end:
            this_month += relativedelta(months=1)
        return this_month

    @classmethod
    def before_monday(cls, _from: datetime = None, end=False):
        this_monday = cls.this_monday(_from=_from, end=end)
        return this_monday - datetime.timedelta(days=7)

    @classmethod
    def this_friday(cls, _from: datetime = None, end=False):
        today = cls.today(_from, end=end)
        return today - datetime.timedelta(days=today.weekday() - 4)

    @classmethod
    def before_friday(cls, _from: datetime = None, end=False):
        this_friday = cls.this_friday(_from=_from, end=end)
        return this_friday - datetime.timedelta(days=7)

    @classmethod
    def this_saturday(cls, _from: datetime = None, end=False):
        today = cls.today(_from, end=end)
        return today - datetime.timedelta(days=today.weekday() - 5)

    @classmethod
    def this_sunday(cls, _from: datetime = None, end=False):
        today = cls.today(_from, end=end)
        return today - datetime.timedelta(days=today.weekday() - 6)

    @classmethod
    def before_sunday(cls, _from: datetime = None, end=False):
        this_sunday = cls.this_sunday(_from, end=end)
        return this_sunday - datetime.timedelta(days=7)

    @classmethod
    def now(cls) -> datetime.datetime:
        return timezone.localtime(timezone=KST)

    @classmethod
    def floor_minute(cls, _from: datetime.datetime) -> datetime.datetime:
        return datetime.datetime(
            _from.year, _from.month, _from.day, _from.hour, _from.minute, tzinfo=_from.tzinfo
        )

    @classmethod
    def day_before_in_business_day(cls, _from: datetime = None, end=False):
        if _from is None:
            _from = timezone.localtime(timezone=KST)
        today = timezone.datetime(_from.year, _from.month, _from.day, tzinfo=KST)
        if end:
            today = today + datetime.timedelta(days=1)
        if today.weekday() == cls.MONDAY:
            return today - datetime.timedelta(days=3)
        else:
            return today - datetime.timedelta(days=1)

    @classmethod
    def get_kst_time_from_timestamp(cls, timestamp: int) -> datetime:
        return datetime.datetime.fromtimestamp(timestamp, KST)
