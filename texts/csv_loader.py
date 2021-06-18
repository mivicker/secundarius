import io
import csv

def reader_from(file_input):
	stream = io.StringIO(file_input)
	return csv.DictReader(stream)