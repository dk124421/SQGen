from django.contrib import admin
from PaperGenerator.models import PaperGenerator
# from .models import PaperGenerator

# Register your models here.

class PaperGeneratorAdmin(admin.ModelAdmin):
    list_display = ('exam_type', 'subject', 'syllabus', 'difficulty')

admin.site.register(PaperGenerator, PaperGeneratorAdmin)
