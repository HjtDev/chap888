from django.db import models
from django_resized import ResizedImageField
from datetime import datetime
from pdf2image import convert_from_path
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.db import transaction
from PyPDF2 import PdfReader
from django.core.exceptions import ValidationError


def document_path(instance, filename):
    return f'documents/{datetime.today().strftime("%Y/%m/%d")}/{filename}'

def pdf_size_validator(pdf):
    if pdf.size > 10485760:  # 10MB
        raise ValidationError('حجم فایل باید کمتر از 10 مگابایت باشد.')



class Documents(models.Model):
    pdf = models.FileField(upload_to=document_path, verbose_name='فایل', validators=[pdf_size_validator])
    # thumbnail = ResizedImageField(upload_to=document_path, size=[60, 70], quality=100, keep_meta=True,
    #                               editable=False, null=True, blank=True)

    def __str__(self):
        return self.pdf.name.split('/')[-1]

    def create_thumbnail(self):
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

    def get_page_count(self) -> int:
        try:
            with open(self.pdf.path, 'rb') as f:
                reader = PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return 0

    get_page_count.short_description = 'صفحه'

    class Meta:
        verbose_name = 'فایل'
        verbose_name_plural = 'فایل ها'
