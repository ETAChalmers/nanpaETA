import pytz
from collections import defaultdict
from ipware import get_client_ip
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render
from .models import TimeRange


def index(request):
    timezone.activate("europe/stockholm")

    ip = get_client_ip(request)[0]
    lastrange = TimeRange.objects.last()
    now = timezone.now().astimezone(pytz.timezone("europe/stockholm"))
    if ip == "129.16.13.37":
        if now - lastrange.end_time < timezone.timedelta(minutes=5):
            lastrange.end_time = now
        else:
            lastrange.end_time += timezone.timedelta(minutes=1)
            lastrange.save()
            lastrange = TimeRange(start_time=now, end_time=now)

        lastrange.save()

    if now - lastrange.end_time < timezone.timedelta(minutes=1.5):
        status = "yes"
    elif now - lastrange.end_time < timezone.timedelta(minutes=5):
        status = "maybe"
    else:
        status = "no"

    ranges = [
        r
        for ranges in TimeRange.objects.filter(
            start_time__gt=now.date()
            - timezone.timedelta(days=int(request.GET.get("days", 14)) - 1)
        )
        for r in ranges.split()
    ]
    for r in ranges:
        r.start_time = r.start_time.astimezone(pytz.timezone("europe/stockholm"))
        r.end_time = r.end_time.astimezone(pytz.timezone("europe/stockholm"))
    ranges.sort(
        key=lambda r: r.start_time
    )  # might be redundant since times may already be sorted, i'm too tired to think about if this is the case right now
    days = {
        (timezone.now() - timezone.timedelta(days=i))
        .astimezone(pytz.timezone("europe/stockholm"))
        .date(): []
        for i in range(int(request.GET.get("days", 14)))
    }
    for r in ranges:
        start = r.start_time.time()
        end = r.end_time.time()
        startseconds = start.second + start.minute * 60 + start.hour * 3600
        endseconds = end.second + end.minute * 60 + end.hour * 3600
        startpercent = startseconds / (60 * 60 * 24) * 100
        endpercent = 100 - (endseconds / (60 * 60 * 24) * 100)
        days[r.start_time.date()].append([startpercent, endpercent])

    return render(
        request,
        "core/index.html",
        {
            "status": status,
            "start": lastrange.start_time,
            "end": lastrange.end_time,
            "duration": timezone.now()
            - (lastrange.end_time if status == "no" else lastrange.start_time),
            "days": days,
        },
    )
