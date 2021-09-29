import datetime
import pytz
from django.db import models
from django.utils import timezone


class TimeRange(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def split(self):
        start = self.start_time.astimezone(pytz.timezone("europe/stockholm"))
        end = self.end_time.astimezone(pytz.timezone("europe/stockholm"))

        if start.date() == end.date():
            return [self]

        results = [
            TimeRange(
                start_time=start,
                end_time=timezone.make_aware(
                    timezone.datetime.combine(start.date(), datetime.time.max),
                    pytz.timezone("europe/stockholm"),
                ),
            )
        ]
        start = timezone.make_aware(
            timezone.datetime.combine(
                start.date() + timezone.timedelta(days=1), datetime.time.min
            ),
            pytz.timezone("europe/stockholm"),
        )

        while start.date() != end.date():
            results.append(
                TimeRange(
                    start_time=start,
                    end_time=timezone.make_aware(
                        timezone.datetime.combine(start.date(), datetime.time.max),
                        pytz.timezone("europe/stockholm"),
                    ),
                )
            )
            start += timezone.timedelta(days=1)

        results.append(TimeRange(start_time=start, end_time=end))

        return results

    def __str__(self):
        return f"{self.start_time.isoformat()} - {self.end_time.isoformat()}"