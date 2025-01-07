from django.db import models
from django_resized import ResizedImageField
from datetime import datetime
from pdf2image import convert_from_path
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import transaction


def document_path(instance, filename):
    return f'documents/{datetime.today().strftime("%Y/%m/%d")}/{filename}'


class Documents(models.Model):
    pdf = models.FileField(upload_to=document_path, verbose_name='فایل')
    thumbnail = ResizedImageField(upload_to=document_path, size=[60, 70], quality=100, keep_meta=True,
                                  editable=False, null=True, blank=True)

    def __str__(self):
        return self.pdf.name

    def create_thumbnail(self):
        print('create_thumbnail called for:', self.pdf.name)
        try:
            images = convert_from_path(self.pdf.path, first_page=1, last_page=1)
            if images:
                thumbnail_io = BytesIO()
                images[0].convert('RGB').save(thumbnail_io, format='JPEG', quality=100)
                thumbnail_file = ContentFile(thumbnail_io.getvalue(),
                                             name=os.path.basename(self.pdf.name).replace('.pdf', '.jpg'))

                with transaction.atomic():
                    self.thumbnail.save(thumbnail_file.name, thumbnail_file)
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
