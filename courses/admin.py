from django.contrib import admin

from . import models


class TextInLine(admin.StackedInline):
    model = models.Text


class QuizInLine(admin.StackedInline):
    model = models.Quiz


class AnswerInLine(admin.StackedInline):
    model = models.Answer


class CourseAdmin(admin.ModelAdmin):
    inlines = [TextInLine, QuizInLine]

    search_fields = ['title', 'description']


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInLine, ]


class QuizAdmin(admin.ModelAdmin):
    fields = ['course', 'title', 'description', 'order', 'total_questions']


admin.site.register(models.Course)
admin.site.register(models.Text)
admin.site.register(models.Quiz, QuizAdmin)
admin.site.register(models.MultipleChoiceQuestion, QuestionAdmin)
admin.site.register(models.TrueFalseQuestion, QuestionAdmin)
admin.site.register(models.Answer)
