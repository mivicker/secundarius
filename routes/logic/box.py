"""
The box module handles the particulars of food box creation,
and provides useful functions for reporting.
"""
import datetime
from dataclasses import dataclass, field
from functools import reduce
from itertools import chain
from operator import concat
from typing import Dict, List, NamedTuple, Tuple, Optional
from collections import defaultdict, Counter
from returns.context import RequiresContext
from returns.curry import curry
from classes import typeclass


ChangeCommand = Tuple[str, tuple]


@dataclass
class BoxOrder:
    """Order creation object to send to box module"""

    menu_name: str
    changes: List[ChangeCommand] = field(default_factory=list)


# Box info comes out of the db like this.
Prototype = List[Tuple[str, int]]


@dataclass(frozen=True)
class Item:
    """Details about the products in the box"""

    item_code: str
    description: str
    rack: str
    price: float
    type: str
    food_group: str
    recurrance: int = 1
    expand_rule: str = '111'


class Share(NamedTuple):
    """An item paired with the quantity in the box"""

    item: Item
    quantity: int


@dataclass
class Box:
    """A list of shares defined to use typeclass"""

    shares: List[Share]
    bin_label: str = "unlabeled"


@dataclass
class Labeler:
    """Keeps the grouping of data for label of bins"""

    label_pool: Optional[List[str]] = field(default_factory=list)
    bin_listen_to: Optional[Tuple[str, str]] = field(default_factory=tuple)
    bin_labels: Optional[Dict[tuple, str]] = field(default_factory=dict)
    bin_quantities: Optional[Dict[tuple, int]] = field(default_factory=dict)


@dataclass
class Warehouse:
    """Holds information to the box building process"""

    date: datetime.datetime
    window: str
    changes: List[ChangeCommand]

    menus: Dict[str, Prototype]
    items: Dict[str, Item]
    rack_order: Optional[List[str]] = field(default_factory=list)
    labeler: Labeler = field(default_factory=Labeler)

    def asdict(self):
        """Only save the important stuff to the database."""
        return {
            k: v
            for k, v in self.__dict__.items()
            if k in ["date", "window", "changes"]
        }


Racks = Dict[str, Box]


@typeclass
def estimate_cost() -> float:
    """estimates cost for objects"""


@estimate_cost.instance(Share)
def _(share: Share):
    """estimates cost of a share"""
    return share.quantity * share.item.price


@estimate_cost.instance(Box)
def _(box: Box):
    """estimates cost of a box"""
    return sum(estimate_cost(share) for share in box.shares)


@curry
def count_items_by(attr: str, box: Box) -> Counter:
    """Makes the items attributes available for counting"""
    return Counter([share.item.__getattribute__(attr) for share in box.shares])


@curry
def make_bin_key(attr: str, target: str, box: Box) -> Tuple:
    """Returns a tuple that can be used in a dict to label subsets
    of products from menus"""
    empty_box = Box(shares=[], bin_label="N/A")
    return tuple(to_prototype(split_box(attr, box).get(target, empty_box)))


def print_letter_label(box: Box) -> RequiresContext[str, Warehouse]:
    """Return the next label after updating the state of the warehouse."""

    def inner(warehouse: Warehouse):
        if not warehouse.labeler.bin_listen_to:
            return None
        attr, target = warehouse.labeler.bin_listen_to
        key = make_bin_key(attr, target, box)
        if not warehouse.labeler.bin_labels.get(key):
            warehouse.labeler.bin_labels[key] = warehouse.labeler.label_pool.pop()

        warehouse.labeler.bin_quantities[key] = warehouse.labeler.bin_quantities.get(key, 0) + 1
        return warehouse.labeler.bin_labels[key]

    return RequiresContext(inner)


def build_box(prototype: Prototype) -> RequiresContext[Box, Warehouse]:
    """Builds box from the List[Tuple] prototype, needs a warehouse"""

    def inner(warehouse: Warehouse):
        box = Box(
            shares=[
                Share(warehouse.items[item_code], quantity)
                for item_code, quantity in prototype
            ]
        )
        box.bin_label = print_letter_label(box)(warehouse)
        return box

    return RequiresContext(inner)


def to_prototype(box: Box) -> Prototype:
    """Returns a built box to prototype form"""
    return [(share.item.item_code, share.quantity) for share in box.shares]


def add_prototypes(a: Prototype, b: Prototype) -> Prototype:
    """Add prototypes to each other"""
    result = defaultdict(int)
    for key, value in chain(a, b):
        result[key] += value
    return list(result.items())


def sum_prototypes(prototypes: List[Prototype]) -> Prototype:

    return reduce(add_prototypes, prototypes)


def positive_only(prototype: Prototype) -> Prototype:
    """Remove and 0 and negative entries from prototype"""
    return [product for product in prototype if product[1] > 0]


def sum_boxes(boxes: List[Box]) -> RequiresContext[Box, Warehouse]:
    """Adds boxes together"""
    prototype = sum_prototypes([to_prototype(box) for box in boxes])
    return RequiresContext(
        lambda warehouse: build_box(positive_only(prototype))(warehouse)
    )


@curry
def split_box(attr: str, box: Box) -> Racks:
    """Breaks box into racks (a dictionary) along a particular *item* attr"""
    result: defaultdict = defaultdict(lambda: Box(shares=[]))
    for share in box.shares:
        result[share.item.__getattribute__(attr)].shares.append(share)

    return dict(result)


def simple_change(item_code: str, delta: int) -> Prototype:
    """Returns a tiny prototype."""
    return [(item_code, delta)]


@curry
def exchange(
    prototype: Prototype, remove_item_code: str, add_item_code: str, ratio: int
) -> Prototype:
    """Returns a change prototype that when added to the provided box
    prototype will exchange one product for another"""
    lookup = dict(prototype)
    return [
        (add_item_code, lookup.get(remove_item_code, 0) * ratio),
        (remove_item_code, lookup.get(remove_item_code, 0) * -1),
    ]


@curry
def remove(prototype: Prototype, remove_item_code: str) -> Prototype:
    """Returns a change prototype that removes a product from a box prototype."""
    lookup = dict(prototype)
    return [(remove_item_code, lookup.get(remove_item_code, 0) * -1)]


def make_change(c_command: ChangeCommand) -> RequiresContext[Prototype, Prototype]:
    """Chooses the strategey for creating the change, and returns
    the change prototype (once the referrence prototype is applied"""

    def inner(prototype):
        commands = {
            "change": simple_change,
            "exchange": exchange(prototype),
            "remove": remove(prototype),
        }
        command, *args = c_command
        return commands[command](*args)

    return RequiresContext(inner)


def make_changes(
    commands: List[ChangeCommand],
) -> RequiresContext[Prototype, Prototype]:
    """Turns a list of commands into a change prototype."""
    return RequiresContext(
        lambda prototype: reduce(
            concat, [make_change(command)(prototype) for command in commands], []
        )
    )


def modify(prototype: Prototype, changes: List[ChangeCommand]) -> Prototype:
    """Applies the changes to the prototype, only allow positive shares through"""
    return add_prototypes(prototype, make_changes(changes)(prototype))


def build_box_from_order(order: BoxOrder) -> RequiresContext[Box, Warehouse]:
    """The ideal box is what the customer wants, the real box,
    the closest thing the warehouse can provide."""

    def inner(warehouse: Warehouse) -> Box:
        prototype = warehouse.menus[order.menu_name]

        ideal_box = modify(prototype, order.changes)
        real_box = modify(ideal_box, warehouse.changes)
        return build_box(positive_only(real_box))(warehouse)

    return RequiresContext(inner)


def lookup_share(box: Box, item_code: str) -> Share:
    """returns the first share in the box with the matching item code"""
    return next(
        (share for share in box.shares if share.item.item_code == item_code), None
    )


def lookup_record(prototype: Prototype, item_code: str) -> Tuple[str, int]:
    """returns the first record in the prototype with the matching item code"""
    return next((record for record in prototype if record[0] == item_code))
