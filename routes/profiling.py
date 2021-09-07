import cProfile
import pstats
from pathlib import Path
import json

from django.shortcuts import render
from django.http import HttpRequest

from routes.business.handlers import build_fulfillment_context
from routes.business.clean_up import clean_upload

path = Path(Path.home(), 'Desktop', 'secundarius', 'routes', 'fixtures', 'upload.json')
template_path = Path(Path.home(), Path.home(), 'Desktop', 'secundarius', 'routes', 'templates', 'routes', 'fulfillment.html')

def main():
    with open(path) as f:
        cleaned = clean_upload(json.load(f))
        context = build_fulfillment_context(cleaned)
        render(HttpRequest(), template_path, context={'order':context})

with cProfile.Profile() as pr:
    main()

stats = pstats.Stats(pr)
stats.sort_stats(pstats.SortKey.TIME)
stats.dump_stats('from_profiling.prof')