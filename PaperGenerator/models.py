from django.db import models

# Create your models here.

class PaperGenerator(models.Model):
    exam_type = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    syllabus = models.TextField(blank=True, null=True)
    difficulty = models.CharField(max_length=100)