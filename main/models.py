from django.db import models


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name='سوال')
    answer = models.TextField(max_length=1000, verbose_name='جواب')
    is_visible = models.BooleanField(default=True, verbose_name='نمایش در سایت')

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'

