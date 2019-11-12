from django.db import models
import uuid
import os
from chord_recognition.settings import PCP_IMAGES_ROOT


class MyQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        paths = self.values_list('path', flat=True)
        for path in paths:
            os.remove(os.path.join(PCP_IMAGES_ROOT, path))
        return super().delete(*args, **kwargs)


class DeleteFilesManager(models.Manager):
    def get_queryset(self):
        return MyQuerySet(self.model, using=self._db)


def get_default_filename():
    return 'chords_' + str(uuid.uuid1()).split('-')[0] + '.png'


class PCPFile(models.Model):
    path = models.CharField(max_length=255, default=get_default_filename)
    objects = DeleteFilesManager()

    def __str__(self):
        return f'path: {self.path}'

    def delete(self):
        os.remove(os.path.join(PCP_IMAGES_ROOT, self.path))
        super().delete()

    def get_full_path():
        return os.path.join('img/pcp', self.path)
