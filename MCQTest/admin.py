from django.contrib import admin
from MCQTest.models import MCQTest

# Register your models here.


class MCQTestAdmin(admin.ModelAdmin):
    list_display = ('topic', 'num_questions', 'difficulty')

admin.site.register(MCQTest, MCQTestAdmin)  # Register your models here.    