from django.db.models import F, Q


def Q_phenomenon_time(from_aware, to_aware):
    """Return filter of phenomenon_time with instant/period logic."""
    return Q(phenomenon_time__gte=from_aware) & (
        Q(phenomenon_time_to__lt=to_aware) | (
            Q(phenomenon_time_to=to_aware) &
            ~Q(phenomenon_time_to=F('phenomenon_time'))
        )
    )
