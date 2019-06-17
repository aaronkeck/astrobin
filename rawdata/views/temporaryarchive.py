# Django
from django.views.generic import DetailView

# This app
from rawdata.models import TemporaryArchive


class TemporaryArchiveDetailView(DetailView):
    model = TemporaryArchive
