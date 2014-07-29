from django.db import models

class LinkList(models.Model):
    id = models.AutoField(max_length=10, primary_key=True, verbose_name='ID')
    title = models.CharField(max_length=50, verbose_name='Link Name')
    address = models.CharField(max_length=100, verbose_name='Link Address')

    class Meta:
        verbose_name_plural = 'Links'