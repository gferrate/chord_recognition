from django.db import models
import uuid


def get_default_filename():
    return 'chords_' + str(uuid.uuid1()).split('-')[0] + '.png'


class PCPFile(models.Model):
    filename = models.CharField(max_length=255, default=get_default_filename)
    deleted = models.BooleanField(default=False)
