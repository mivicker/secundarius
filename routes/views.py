import json
import io
import csv
import string
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.core.files.uploadedfile import UploadedFile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from counts.models import Warehouse
from routes.models import Depot
from .logic.adapter import (
    build_named_labeler,
    clean_upload,
    build_fulfillment_context,
    Translator,
    build_route_context,
    build_frozen_context,
    build_warehouse_from_db,
    build_basic_warehouse,
    extract_date_from_order,
    extract_time_from_order,
    try_parsing_date,
    depot_from_db,
)
from .forms import DateForm, DepotForm
from .logic.download_deliveries import collect_time_blocks, make_csv
from texts.forms import UploadFileForm
from counts.forms import WarehouseForm


def load_csv(file: UploadedFile):
    data = file.read().decode("UTF-8")
    io_string = io.StringIO(data)
    return csv.DictReader(io_string)


@login_required
def landing(request: HttpRequest):
    return render(request, "routes/landing.html", context={})


@login_required
def fulfillment_menu(request: HttpRequest):
    return render(request, "routes/fulfillmenu.html")


@login_required
def fulfillment_options(request: HttpRequest) -> HttpResponse:
    file = request.session["order"]
    cleaned = clean_upload(json.loads(file))
    date = try_parsing_date(extract_date_from_order(cleaned))
    time_window = extract_time_from_order(cleaned)
    try:
        warehouse = Warehouse.objects.get(date=date, time_window=time_window)
    except Warehouse.DoesNotExist:
        warehouse = Warehouse.objects.order_by("-date").first()

    defaults = {
        "substitutions": [sub.pk for sub in warehouse.substitutions.all()],
        "out": [sub.pk for sub in warehouse.out.all()],
        "additions": [sub.pk for sub in warehouse.additions.all()],
    }

    return render(
        request,
        "routes/fulfillment_options.html",
        context={"form": WarehouseForm(defaults, instance=warehouse)},
    )


@login_required
def select_date(request: HttpRequest):
    if request.method == "POST":
        form = DateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data["date"]
            time_blocks = collect_time_blocks(date)
            request.session["delivery date"] = date.strftime("%m-%d-%Y")
            request.session["time blocks"] = time_blocks
        return redirect("select-time")
    return render(request, "routes/select_date.html", context={"form": DateForm()})


@login_required
def select_time(request: HttpRequest):
    return render(
        request,
        "routes/select_time.html",
        context={"available_blocks": reversed(request.session["time blocks"].keys())},
    )


@login_required
def download_csv(request: HttpRequest, time: str) -> HttpResponse:
    blocks = request.session["time blocks"]
    date = request.session["delivery date"]
    csv = make_csv(blocks[time])

    response = HttpResponse(csv)

    response["Content-Type"] = "application/vnd.ms-excel"
    response[
        "Content-Disposition"
    ] = f'attachment; filename="Deliveries{date}{time}.csv"'

    return response


@login_required
def csv_drop_off(request: HttpRequest) -> HttpResponse:
    return render(request, "routes/csv_drop.html", context={"form": UploadFileForm()})


@login_required
def post_csv(request: HttpRequest) -> HttpResponse:
    """
    This needs to look at the file and check if the date is for the next
    day or not.
    """
    request.session["order"] = json.dumps(list(load_csv(request.FILES["file"])))
    return redirect("document-navigation")


@login_required
def documents_menu(request: HttpRequest) -> HttpResponse:
    return render(request, "routes/documents-menu.html")


@login_required
def fulfillment_navagation(request: HttpRequest) -> HttpResponse:
    return render(request, "routes/fulfillment_navagation.html")


@login_required
def add_warehouse(request: HttpRequest) -> HttpResponse:
    file = request.session["order"]
    cleaned = clean_upload(json.loads(file))
    date = try_parsing_date(extract_date_from_order(cleaned))
    time_window = extract_time_from_order(cleaned)
    warehouse, _ = Warehouse.objects.get_or_create(date=date, time_window=time_window)

    form = WarehouseForm(request.POST, instance=warehouse)

    if form.is_valid():
        form.save()
        return redirect("fulfillment-navagation")
    redirect("update-warehouse")


@login_required
def fulfillment_vue_page(request: HttpRequest) -> HttpResponse:
    return render(request, "routes/fulfillment_inner.html")


@login_required
def fulfillment_tickets(request: HttpRequest):
    return render(
        request,
        "routes/fulfillment_inner.html",
    )


@login_required
def fulfillment_tickets_json(request: HttpRequest):
    file = request.session["order"]
    cleaned = clean_upload(json.loads(file))
    date = try_parsing_date(extract_date_from_order(cleaned))
    time_window = extract_time_from_order(cleaned)

    translator = Translator()
    warehouse = build_warehouse_from_db(
        Warehouse.objects.get(date=date, time_window=time_window)
    )
    labeler = build_named_labeler(
        list(string.ascii_uppercase), ("rack", "Frozen"), warehouse
    )
    warehouse.labeler = labeler
    return JsonResponse(build_fulfillment_context(cleaned, warehouse, translator))


@login_required
def frozen_tickets(request: HttpRequest):
    file = request.session["order"]
    cleaned = clean_upload(json.loads(file))

    date = try_parsing_date(extract_date_from_order(cleaned))
    time_window = extract_time_from_order(cleaned)

    translator = Translator()
    warehouse = build_warehouse_from_db(
        Warehouse.objects.get(date=date, time_window=time_window)
    )
    labeler = build_named_labeler(
        list(string.ascii_uppercase), ("rack", "Frozen"), warehouse
    )
    warehouse.labeler = labeler

    return render(
        request,
        "routes/froz.html",
        context=build_frozen_context(cleaned, warehouse, translator),
    )


@login_required
def create_depot(request: HttpRequest) -> HttpResponse:
    return render(request, "routes/create_depot.html", context={"form": DepotForm()})


@login_required
def post_depot(request: HttpRequest) -> HttpResponse:
    file = request.session["order"]
    cleaned = clean_upload(json.loads(file))
    date = try_parsing_date(extract_date_from_order(cleaned))
    time_window = extract_time_from_order(cleaned)
    depot, created = Depot.objects.get_or_create(date=date, time_window=time_window)

    form = DepotForm(request.POST, instance=depot)

    if form.is_valid():
        form.save()
        return redirect("route-lists")
    redirect("create-depot")


@login_required
def route_lists_json(request: HttpRequest):
    file = request.session["order"]
    cleaned = clean_upload(json.loads(file))
    date = try_parsing_date(extract_date_from_order(cleaned))
    time_window = extract_time_from_order(cleaned)

    translator = Translator()
    warehouse = build_basic_warehouse()

    depot = Depot.objects.get(date=date, time_window=time_window)

    routes = build_route_context(cleaned, warehouse, depot_from_db(depot), translator)
    return JsonResponse({"routes": routes})


@login_required
def route_lists(request: HttpRequest):
    return render(request, "routes/lists.html")


@login_required
def upload_error(request: HttpRequest):
    return render(request, "routes/upload_error.html")
