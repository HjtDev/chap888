from django.db import models
from django_jalali.db import models as jmodels
from jdatetime import date


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name='سوال')
    answer = models.TextField(max_length=1000, verbose_name='جواب')
    is_video = models.BooleanField(default=False, verbose_name='ویدیو')
    is_visible = models.BooleanField(default=True, verbose_name='نمایش در سایت')

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        if self.is_video and '<style>' in self.answer or '<div' in self.answer:
            self.answer = self.answer[self.answer.index('<iframe'):self.answer.index('</iframe>') + 9]
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'


class Comment(models.Model):
    objects = jmodels.jManager()
    name = models.CharField(max_length=30, verbose_name='نام')
    commented_at = jmodels.jDateField(default=date.today, verbose_name='تاریخ ثبت نظر')
    text = models.TextField(max_length=450, verbose_name='نظر')
    is_visible = models.BooleanField(default=True, verbose_name='نمایش در سایت')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'نظر کاربران'
        verbose_name_plural = 'نظرات کاربران'

