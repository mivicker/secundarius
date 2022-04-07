from django.http import HttpResponse
from django.shortcuts import render
from .forms import StartDateForm, EndDateForm
from .forms import UploadFileForm
import xlrd


def invoice(request):
    # Group deliveries by date

    # Group deliveries by timeslot

    # Summarize values for each menu
    
    # Find Warehouse that has those values
    context = {
        "file_form": UploadFileForm(),
        "start_date_form": StartDateForm(),
        "end_date_form": EndDateForm(),
    }
    return render(request, "counts/invoice.html", context=context)


def replace_empty(val):
    return 0 if val == '' else val


def cols_to_values(row):
    return row[0].value, row[6].value


def extract_warehouse_tag(tup):
    return tup[0].split()[1]


def post_invoice(request):
    file = request.FILES.get('file')
    book = xlrd.open_workbook(file_contents=file.read())

    sh = book.sheet_by_index(0)

    next_warehouse = "empty warehouse"

    result = []
    for rx in range(sh.nrows):
        tup = cols_to_values(sh.row(rx))
        print(tup)
        """
        if (tup[0].startswith('On Hand') | tup[0].startswith('Report')):
            continue
        if (tup[0].startswith('Warehouse')):
            next_warehouse = extract_warehouse_tag(tup)
            continue
        result.append((tup[0], int(replace_empty(tup[1])), next_warehouse))
        """

    return HttpResponse("This worked")
