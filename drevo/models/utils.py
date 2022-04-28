from django.db import models
from django.db import OperationalError


class Stub:
    def __getattribute__(self, attr):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __iter__(self):
        yield ''


def get_model_or_stub(model):
    try:
        # breakpoint()
        model.objects.first()
        return model
    except OperationalError:
        return Stub()
