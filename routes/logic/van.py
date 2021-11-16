"""
The van module handles the particulars of deliveries.
"""
import datetime
import itertools
from typing import Counter, Protocol, List, Dict, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from itertools import permutations
from returns.curry import curry


Stop = dict


class Deliverable(Protocol):
    """This is the thing carried by the visit class"""


class Empty:
    """When you don't need delivery"""
    pass


@dataclass
class Depot:
    """This holds details specific to the route in question."""
    active_drivers: List[str] # The str is a driver email address.


@dataclass
class Visit:
    member_id: str
    date: datetime.date
    time_window: str
    stop: Stop
    route: str
    labels: str = "A"
    deliverable: Deliverable = field(default_factory=Empty)
    racks: dict = field(default_factory=dict)

    def __getattr__(self, attr):
        return self.stop[attr]


@curry
def split_visits(attr: str, visits: List[Visit]) -> Dict[str, List[Visit]]:
    """Groups visits on a certain value, visit will look into stop
    dict for attribute if necessary."""
    result: defaultdict = defaultdict(list)
    for visit in visits:
        result[visit.__getattribute__(attr)].append(visit)

    return dict(result)


def fill_gap(drivers:List[str], num_routes:int) -> List[str]:
    return [driver for _, driver in itertools.zip_longest(range(num_routes), drivers, fillvalue='not assigned')]


def assign_drivers(
    depot: Depot, routes: List[List[str]], summary: Counter
) -> Tuple[str, ...]:
    arrangements = permutations(fill_gap(depot.active_drivers, len(routes)))

    scores = sorted(
        [
            (arrangement, score_arrangement(arrangement, routes, summary))
            for arrangement in arrangements
        ],
        key=lambda x: x[1],
        reverse=True,
    )

    return scores[0][0]


def score_arrangement(
    drivers: Tuple[str], routes: List[List[Visit]], summary: Counter
) -> int:

    return sum(
        score_route(driver, route, summary) for driver, route in zip(drivers, routes)
    )


def score_route(driver: str, route: List[Visit], summary: Counter) -> int:
    return sum(summary.get((visit.member_id, driver), 0) for visit in route)
