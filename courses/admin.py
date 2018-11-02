from django.contrib import admin
from datetime import date

from . import models


class TextInLine(admin.StackedInline):
    model = models.Text


class QuizInLine(admin.StackedInline):
    model = models.Quiz


class AnswerInLine(admin.StackedInline):
    model = models.Answer


class YearListFilter(admin.SimpleListFilter):
    title = 'year created'
    parameter_name = 'year'  # Shows up in url

    def lookups(self, request, model_admin):
        return (
            ('2018', '2018'),  # one will go in url and one will go in sidebar
            ('2017', '2017'),
            ('2016', '2016'),
            ('2015', '2015'),
        )

    def queryset(self, request, queryset):
        if self.value() == '2018':
            return( queryset.filter(created_at__gte=date(2018, 1, 1),
                                   created_at__lte=date(2018, 12, 31)))

        if self.value() == '2017':
            return( queryset.filter(created_at__gte=date(2017, 1, 1),
                                   created_at__lte=date(2017, 12, 31)))

        if self.value() == '2016':
            return( queryset.filter(created_at__gte=date(2016, 1, 1),
                                   created_at__lte=date(2016, 12, 31)))

        if self.value() == '2015':
            return( queryset.filter(created_at__gte=date(2015, 1, 1),
                                   created_at__lte=date(2015, 12, 31)))

class CourseAdmin(admin.ModelAdmin):
    inlines = [TextInLine, QuizInLine]

    search_fields = ['title', 'description']

    list_filter = ['created_at', 'published', YearListFilter]

    list_display = ['title', 'created_at', 'published', 'time_to_complete']

    list_editable = ['published']


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInLine, ]

    search_fields = ['prompt']

    list_display = ['prompt', 'quiz', 'order']

    list_editable = ['quiz', 'order']

class QuizAdmin(admin.ModelAdmin):
    fields = ['course', 'title', 'description', 'order', 'total_questions']


class AnswerAdmin(admin.ModelAdmin):

    search_fields = ['prompt']

    list_display = ['question', 'text', 'correct']

admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Text)
admin.site.register(models.Quiz, QuizAdmin)
admin.site.register(models.MultipleChoiceQuestion, QuestionAdmin)
admin.site.register(models.TrueFalseQuestion, QuestionAdmin)
admin.site.register(models.Answer, AnswerAdmin)
