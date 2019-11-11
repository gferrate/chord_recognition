from django.db import models
import uuid
import os


def get_default_filename():
    return os.path.join('img/pcp', 'chords_' + str(uuid.uuid1()).split('-')[0] + '.png')


class PCPFile(models.Model):
    path = models.CharField(max_length=255, default=get_default_filename)
    deleted = models.BooleanField(default=False)
