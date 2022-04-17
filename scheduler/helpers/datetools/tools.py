from typing import List
from datetime import datetime, timedelta
from gstorm import GraphQLType
from inflect import engine


eng = engine()
tolerance = timedelta(minutes=2)

map_scales = {
    "microseconds": 1e-3,
    "seconds": 1,
    "minutes": 60,
    "hours": 3600,
    "days": 86400,
}


def time_conversor(date_obj: datetime, pivot: datetime, factor: int = 1) -> int:
    return round((date_obj - pivot).total_seconds() / factor)


def to_int(date_obj: datetime, pivot: datetime, scale: str = "seconds") -> int:
    """Convert datetime.datetime object into integer given a pivot datetime for
    getting the diference

    Args:
        date_obj (datetime): Datetime object to convert
        pivot (datetime, optional): Datetime as a reference point.
        scale (str, optional): Scale of time to convert returned integer. May be
            one of the followings: "seconds", "minutes", "hours", "days". Defaults to "seconds".

    Raises:
        NotImplementedError: In case 'scale' it is not defined

    Returns:
        int: Number that reflects the datetime convert to interger given scale time
    """
    if scale not in map_scales:
        raise NotImplementedError(
            f"Scale '{scale}' not registered. You may try one of the followings: {list(map_scales)}")
    return time_conversor(date_obj, pivot, map_scales[scale])


def to_iso8601(date_obj: datetime, t: bool = True, z: bool = True) -> str:
    """Datetime function to get a string from a datetime object in ISO-8601 format

    Args:
        date_obj (datetime): Datetime object
        t (bool, optional): True if date is needed. Defaults to True.
        z (bool, optional): True if hour is needed. Defaults to True.

    Raises:
        TypeError: If 'date_obj' is not a datetime instance

    Returns:
        str: Datetime's string in ISO-8601
    """
    if not isinstance(date_obj, datetime):
        raise TypeError("'date_obj' is not datetime.datetime instance")
    string = ""
    if t:
        string += date_obj.strftime("%Y-%m-%dT")
    if z:
        string += date_obj.strftime("%H:%M:%SZ")
    return string


def is_intersected(obj_a: GraphQLType, obj_b: GraphQLType, strict: bool = False) -> bool:
    """Method to know if to Schedule-Logic's objects with 'startAt' & 'endAt' are intersected in time

    Args:
        obj_a (GraphQLType): Schedule Logic's model a
        obj_b (GraphQLType): Schedule Logic's model b
        strict (bool, optional): True if the two intervals are needed to be
            diferent even in frontier. Defaults to False.

    Returns:
        bool: True is both intervals are intersected
    """
    if strict:
        return obj_b.startAt <= obj_a.endAt and obj_a.startAt <= obj_b.endAt
    else:
        return obj_b.startAt < obj_a.endAt and obj_a.startAt < obj_b.endAt


def round_date(date_obj: datetime, scale: str) -> datetime:
    if not isinstance(date_obj, datetime):
        raise TypeError("'date_obj' is not datetime.datetime instance")

    singular_scale = eng.singular_noun(scale)
    scale = scale if not singular_scale else singular_scale
    scales = [
        "microsecond",
        "second",
        "minute",
        "hour",
        "day",
    ]

    if not scale in scales:
        raise NotImplementedError(
            f"Scale '{scale}' not registered. You may try one of the followings: {scales}")

    idx = scales.index(scale)
    rounded = {key: 0 for key in scales[:max(idx, 0)]}
    return date_obj.replace(**rounded)


def squash_intervals(objects: List[GraphQLType]) -> List[GraphQLType]:
    """This function take a list of Schedule-Logic instanes with [startAt, endAt]
    intervals. Then it merges them if any are overlaped

    Args:
        objects (List[GraphQLType]): List of Schedule-Logic's instances with
            [startAt, endAt] interval

    Returns:
        List[GraphQLType]: List of the same objects but merged and non-overlaped
    """
    objects = sorted(objects, key=lambda obj: obj.startAt)
    size = len(objects)
    uniques = [True for _ in range(size)]
    for i in range(1, size):
        if is_intersected(objects[i], objects[i-1]):
            objects[i].startAt = objects[i-1].startAt
            uniques[i-1] = False
    return [objects[i] for i in range(size) if uniques[i]]


if __name__ == "__main__":
    a = datetime.utcnow()
    b = datetime.utcnow()
    print(to_int(a, b, scale="days"))
    print(round_date(a, scale="microsecond"))

    # TODO: mover este codigo a sus test respectivos (no prioritario)
    from scheduler.models import Plan
    p1, p2 = Plan(), Plan()
    now = datetime.now()

    p1.startAt = datetime.min
    p1.endAt = now + timedelta(seconds=0)
    p2.startAt = now
    p2.endAt = datetime.max

    print(is_intersected(p2, p1))
    print(is_intersected(p2, p1, False))
