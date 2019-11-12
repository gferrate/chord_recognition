from django.db import models
import uuid
import os
from chord_recognition.settings import PCP_IMAGES_ROOT


def get_default_filename():
    return 'chords_' + str(uuid.uuid1()).split('-')[0] + '.png'


class PCPFile(models.Model):
    path = models.CharField(max_length=255, default=get_default_filename)
    #deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'path: {self.path}'

    def delete(self):
        os.remove(os.path.join(PCP_IMAGES_ROOT, self.path))
        super().delete()

    def get_full_path():
        return os.path.join('img/pcp', self.path)
