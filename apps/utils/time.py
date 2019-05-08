from datetime import timedelta, timezone

UTC_P0100 = timezone(timedelta(hours=1))


def format_delta(delta):
    if delta.total_seconds() == 0:
        return "instant"
    else:
        seconds = delta.seconds
        hours = seconds // 3600
        seconds -= hours * 3600
        minutes = seconds // 60
        seconds -= minutes * 60
        parts = [
            {
                'value': delta.days,
                'label': 'd'
            },
            {
                'value': hours,
                'label': 'h'
            },
            {
                'value': minutes,
                'label': 'm'
            },
            {
                'value': seconds,
                'label': 's'
            },
        ]
        while parts[-1]['value'] == 0:
            parts.pop()
        parts.reverse()
        while parts[-1]['value'] == 0:
            parts.pop()
        parts.reverse()
        parts = map(lambda p: str(p['value']) + ' ' + p['label'], parts)
        return ' '.join(parts)
