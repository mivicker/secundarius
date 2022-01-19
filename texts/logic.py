import io
import csv
from typing import List, Iterable, Set
from dataclasses import dataclass
from returns.result import safe, Failure
from returns.context import RequiresContext
from returns.curry import curry
from jinja2 import Environment, BaseLoader, meta
from twilio.rest import Client


@dataclass
class SendDeps:
    words: str
    from_: str
    client: Client


def read_csv(data:str):
    stream = io.StringIO(data)
    return csv.DictReader(stream)


def set_environment() -> Environment:
    return Environment(loader=BaseLoader(),
        block_start_string='@@',
        block_end_string='@@',
        variable_start_string='$$',
        variable_end_string='$$')


def pluck_variables(string: str) -> Set[str]:
    """This will read the broadcast and show which columns
       will need to be provided from the csv."""

    parsed = set_environment().parse(string)
    return meta.find_undeclared_variables(parsed)


def render_sms_template(words:str, context):
    """This is pluck the variables from the csv and render the
       given template per text with the variables."""

    template = set_environment().from_string(words)
    return template.render(**context)


class SendException(Exception):
    pass


@curry
@safe
def send_text(deps:SendDeps, contact: dict):
    try:
        return deps.client.messages.create(
                body=render_sms_template(deps.words, contact),
                from_=f'+{deps.from_}',
                to=contact['phone']
        )
    except:
        raise SendException(
            f'Unable to send sms to {contact["phone"]}. Check Twilio dashboard for more information.'
            )


def send_each(contacts:List[dict]) -> RequiresContext[List[dict], SendDeps]:
    return RequiresContext( lambda deps: map(send_text(deps), contacts))


def filt_for_failures(return_messages:Iterable) -> Iterable:
    return filter(lambda msg: type(msg) == Failure, return_messages)
