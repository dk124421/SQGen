from django.db import models

# Create your models here.
class MCQTest(models.Model): 
    topic = models.CharField(max_length=100)
    num_questions = models.IntegerField()
    difficulty = models.CharField(max_length=100)