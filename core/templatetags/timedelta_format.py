from django import template

register = template.Library()


@register.filter()
def timedelta_format(duration):
    seconds = duration.total_seconds()

    hours, seconds = divmod(round(seconds), 3600)
    minutes, seconds = divmod(seconds, 60)

    result = ""
    if hours:
        result += f"{hours} {'timmar' if hours > 1 else 'timme'} och "
    result += f"{minutes} {'minuter' if minutes > 1 else 'minut'}"

    return result
