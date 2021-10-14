import pytz
import random
from collections import defaultdict
from ipware import get_client_ip
from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import TimeRange

DEFAULT_DAYS_SHOWN = 7

def index(request):
    if "firefox" not in request.META['HTTP_USER_AGENT'].lower() and random.random() < 0.1:
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

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

    n_days = int(request.GET.get("days", DEFAULT_DAYS_SHOWN))

    ranges = [
        r
        for ranges in TimeRange.objects.filter(
            start_time__gt=now.date()
            - timezone.timedelta(days=n_days - 1)
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
        for i in range(n_days)
    }
    total_open = 0.0
    for r in ranges:
        start = r.start_time.time()
        end = r.end_time.time()
        startseconds = start.second + start.minute * 60 + start.hour * 3600
        endseconds = end.second + end.minute * 60 + end.hour * 3600
        startpercent = startseconds / (60 * 60 * 24) * 100
        endpercent = 100 - (endseconds / (60 * 60 * 24) * 100)
        days[r.start_time.date()].append({
            "start_prec": startpercent,
            "end_prec": endpercent,
            "start_time": f"{start.hour:02}:{start.minute:02}",
            "end_time": f"{end.hour:02}:{end.minute:02}",
        })
        total_open += ((100 - endpercent) - startpercent) / n_days

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
            "n_days": n_days,
            "total_open_prec": f"{total_open:.3}",
        },
    )
