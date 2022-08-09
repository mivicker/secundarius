"""
Separate django stuff, box stuff, and van stuff, hide the good stuff
deep in an underground bunker to stay away from sharepoint.
"""

import contextlib
from typing import Dict, Tuple, List
import datetime
import re
import string
import itertools
from dataclasses import dataclass, field, asdict
from collections import Counter
from returns.curry import curry
from returns.pipeline import flow
from returns.context.requires_context import RequiresContext
import routes.logic.box as boxes
import routes.logic.van as van
from counts import models as count_models
from routes import models as route_models


ADDITIONS_DICT = {
    "Turkey": [("change", "MG1024", 1)],
    "ChickenBreast": [("change", "MG1380", 1)],
    "ChickenHalal": [("change", "MG1241", 1)],
    "ChickenQuarters": [("change", "MG1048", 1)],
    "HalalQuarters": [("change", "MG1385P", 1)],
    "Cheese": [("change", "MG1056", 1)],
    "Bananas": [("change", "MG0030", 1)],
    "Bread": [("change", "MG1136", 1)],
    "MixedVegetables": [("change", "MG1178", 1)],
    "Strawberries": [("change", "MG1286", 1)],
    "MilkGallon": [("change", "MG1063", 1)],
    "MilkHalfGallon": [("change", "MG1186", 1)],
}


EXCHANGES_DICT = {
    "peanutfree": [("exchange", "MG1018", "MG1006", 1)],
    "dairyfree": [
        ("exchange", "MG1186", "MG1187", 1),
        ("exchange", "MG1063", "MG1187", 2),
    ],
}


@dataclass
class Translator:
    """The translator holds the dictionaries that translate
    the stop information to the changes tuples needed for the
    box module."""

    additions: dict = field(default_factory=lambda: ADDITIONS_DICT)
    exchanges: dict = field(default_factory=lambda: EXCHANGES_DICT)


def get_additions_from(
    notes: str,
) -> RequiresContext[List[boxes.ChangeCommand], Translator]:
    """Returned hash-tagged phrases from delivery notes."""
    return lambda translator: [
        translator.additions[addition]
        for addition in get_magic_words(notes)
        if addition in translator.additions
    ]


def get_exchanges_from(
    stop: van.Stop,
) -> RequiresContext[List[boxes.ChangeCommand], Translator]:
    return lambda translator: [
        exchange
        for field, exchange in translator.exchanges.items()
        if stop[field] == "Yes"
    ]


def get_all_modifications(
    stop: van.Stop,
) -> RequiresContext[List[boxes.ChangeCommand], Translator]:
    def inner(translator: Translator):
        additions = get_additions_from(stop.get("delivery_notes", ""))(translator)
        exchanges = get_exchanges_from(stop)(translator)

        return list(itertools.chain(*(additions + exchanges)))

    return inner


def build_warehouse_from_db(
    warehouse: count_models.Warehouse, **kwargs
) -> boxes.Warehouse:
    """Pulls the key stuff from the db, and everything else
    is passed by keyword."""
    return boxes.Warehouse(
        **warehouse.as_dict(),
        menus=build_menu_cache(),
        items=build_item_cache(),
        **kwargs,
        )


def build_relationship_lookup() -> Counter:
    return Counter(
        dict(cache.as_tuple() 
             for cache in route_models.RelationshipCache.objects.all())
    )


def make_entry(command: str) -> tuple:
    return tuple(command.split())


def breakout_substitutions(commands: str) -> Tuple:
    return [make_entry(commands.split("\n"))]


def get_magic_words(notes: str) -> list:
    return re.findall(r"#Add([A-Za-z]+)", notes)


@curry
def build_box_order(stop: van.Stop, translator: Translator) -> boxes.BoxOrder:
    return boxes.BoxOrder(
        menu_name=string_box(stop),
        changes=get_all_modifications(stop)(translator),
    )


def organize_racks(box: boxes.Box) -> Dict[str, boxes.Box]:
    """Displays racks in proper order."""
    # Need to pull this into a config.
    rack_order = [
        "Dry Rack 1",
        "Cooler Rack",
        "Dry Rack 2",
        "Produce Rack",
        "Bakery Trays",
        "Frozen",
        "Dock",
    ]
    racks = boxes.split_box("rack", box)

    return {
        rack_name: racks.get(rack_name, [])
        for rack_name in rack_order
        if racks.get(rack_name, [])
    }


def route_num_to_letter(name: str, start=4):
    """Takes 'Route int'throws away 'Route' and changes int to uppercase
    letter"""
    _, num = name.split()
    index = int(num) - 1

    return string.ascii_uppercase[-start + index]


def build_visit_for_fulfillment(
    stop: van.Stop, warehouse: boxes.Warehouse, translator: Translator
) -> van.Visit:

    attr, target = warehouse.labeler.bin_listen_to
    letter = route_num_to_letter(stop["route_num"])
    box = boxes.build_box_from_order(build_box_order(stop)(translator))(warehouse)

    return van.Visit(
        member_id=stop["member_id"],
        date=stop["delivery_date"],
        time_window=stop["deliverytime"],
        racks=organize_racks(box),
        labels=warehouse.labeler.bin_labels.get(boxes.make_bin_key(attr, target, box)),
        route=letter,
        stop=van.Stop(**stop),
    )


def populate_visits_for_fulfillment(
    upload: List[Dict], warehouse: boxes.Warehouse, translator: Translator
) -> List[van.Visit]:
    return [build_visit_for_fulfillment(stop, warehouse, translator) for stop in upload]


def build_visit_for_routes(
    stop: van.Stop, warehouse: boxes.Warehouse, translator: Translator
) -> van.Visit:

    letter = route_num_to_letter(stop["route_num"])

    return van.Visit(
        member_id=stop["member_id"],
        date=stop["delivery_date"],
        time_window=stop["deliverytime"],
        route=letter,
        stop=van.Stop(**stop),
    )


def populate_visits_for_route(
    upload: List[Dict], warehouse: boxes.Warehouse, translator: Translator
) -> List[van.Visit]:
    return [build_visit_for_routes(stop, warehouse, translator) for stop in upload]


@curry
def build_fulfillment_context(
    upload: List[Dict], warehouse: boxes.Warehouse, translator: Translator
):
    return {
        route_name: serialize_route(route) 
        for route_name, route in van.split_visits(
        "route", populate_visits_for_fulfillment(upload, warehouse, translator)).items()
    }

def serialize_route(route: List[van.Visit]):
    return [asdict(visit) for visit in route]

def build_route_context(
    upload: dict, 
    warehouse: boxes.Warehouse, 
    depot: van.Depot, 
    translator: Translator
) -> List[dict]: 
    """Should be more thoughtful about whether we need to create visits,
    for this of if we can just split the list of dicts."""

    routes = van.split_visits(
        "route", populate_visits_for_route(upload, warehouse, translator)
    )

    relationships = dict(
        [cache.as_tuple() for cache in route_models.RelationshipCache.objects.all()]
    )

    assignments = van.assign_drivers(
        depot,
        routes.values(),
        relationships,
    )

    return [
        {
            "driver": driver,
            "route_name": route_name,
            "visits": [asdict(visit) for visit in route],
            "date": extract_date(route),
            "time": extract_time(route),
        }
        for driver, (route_name, route) in zip(assignments, routes.items())
    ]


def build_frozen_context(upload, warehouse: boxes.Warehouse, translator):

    # This just updates the warehouse state :(
    routes = populate_visits_for_fulfillment(upload, warehouse, translator)

    bins = [
        {
            "box": boxes.build_box(list(key))(warehouse),
            "quantity": quantity,
            "label": warehouse.labeler.bin_labels[key],
        }
        for key, quantity in warehouse.labeler.bin_quantities.items()
    ]

    return {
        "bins": sorted(bins, key=lambda bin: bin["quantity"], reverse=True),
        "date": extract_date(routes),
        "time": extract_time(routes),
    }


def change_keys(dictionary: Dict[str, str]) -> dict:
    return {
        key.lower().replace("#", "num").replace(" ", "_"): value
        for key, value in dictionary.items()
    }


def string_box(stop: van.Stop) -> str:
    """A hack..."""
    return stop["box_type"] + " " + stop["box_menu"] + " " + stop["box_size"]


def extract_date_from_order(order: List[dict]):
    return order[0]['delivery_date']


def extract_time_from_order(order: List[dict]):
    return order[0]['deliverytime']


def extract_date(route: List[van.Visit]):
    return route[0].date


def extract_time(route: List[van.Visit]):
    return route[0].time_window


def format_phone(phone_number: str) -> str:
    area_code, first, last = tuple(re.findall(r"\d{4}$|\d{3}", phone_number))
    return f"({area_code}) {first}-{last}"


def fix_phone(stop: van.Stop) -> van.Stop:
    phone_digits = re.findall(
        "[0-9]{10}", stop["phone"]
    )  # attempts to find a coherent phone number.
    if phone_digits:
        stop["phone"] = format_phone(phone_digits[0])
    if len(phone_digits) > 1:
        stop["delivery_notes"] = (
            stop.get("delivery_notes", "")
            + f" Alternate phone: {format_phone(phone_digits[1])}"
        )
    return stop


def try_parsing_date(text: str) -> datetime.datetime:
    for fmt in ("%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%d-%b-%y"):
        with contextlib.suppress(ValueError):
            return datetime.datetime.strptime(text, fmt)
    raise ValueError("no valid date format found")


def clean_stop(stop: van.Stop) -> van.Stop:
    """This may eventually need error handling."""
    return flow(stop, change_keys, fix_phone)


def clean_unrouted(upload: List[van.Stop]) -> List[van.Stop]:
    return [clean_stop(stop) for stop in upload]


def clean_upload(upload: List[van.Stop]) -> List[van.Stop]:
    """
    This cleans and filters and should be refactored.
    """
    return [
        clean_stop(stop) for stop in upload if re.match("Route[0-9]*", stop.get("Route #", ''))
    ]


def build_menu_cache() -> dict:
    return dict([menu.as_tup() for menu in count_models.Menu.objects.all()])


def build_item_cache() -> dict:
    return {
        item.item_code: boxes.Item(**item.as_dict())
        for item in count_models.Item.objects.all()
    }


def build_menu_name_lookup(listen_to, warehouse: boxes.Warehouse) -> Dict[Tuple, str]:
    attr, target = listen_to
    return {
        boxes.make_bin_key(attr, target, boxes.build_box(value)(warehouse)): key
        for key, value in reversed(warehouse.menus.items())
    }


def build_named_labeler(
    label_pool: List[str], listen_to: Tuple[str, str], warehouse: boxes.Warehouse
) -> boxes.Labeler:
    menu_name_lookup = build_menu_name_lookup(listen_to, warehouse)
    return boxes.Labeler(
        label_pool=label_pool, bin_labels=menu_name_lookup, bin_listen_to=listen_to
    )


def build_basic_warehouse() -> boxes.Warehouse:
    return boxes.Warehouse(
        date=datetime.datetime.now().date(),
        time_window='',
        changes=[],
        menus=build_menu_cache(),
        items=build_item_cache(),
    )


def depot_from_db(depot_record: route_models.Depot):
    return van.Depot(active_drivers=[driver.email for driver in depot_record.active_drivers.all()])
