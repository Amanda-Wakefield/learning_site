from django import forms

from . import models


class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = [
            'title',
            'description',
            'teacher',
            'published',
        ]


class QuizForm(forms.ModelForm):
    class Meta:
        model = models.Quiz
        fields = [
            'title',
            'description',
            'order',
            'total_questions',
        ]

class QuestionForm(forms.ModelForm):
    class Media:
        css = {'all': ('courses/css/order.css',)}
        js = ('courses/js/vendor/jquery.fn.sortable.min.js',
              'courses/js/order.js'
              )



class TrueFalseQuestionForm(QuestionForm):
    class Meta:
        model = models.TrueFalseQuestion
        fields = ['order', 'prompt']


class MultipleChoiceQuestionForm(QuestionForm):
    class Meta:
        model = models.MultipleChoiceQuestion
        fields = [
            'order',
            'prompt',
            'shuffle_answers'
        ]


class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = [
            'order',
            'text',
            'correct'
        ]

AnswerFormSet = forms.modelformset_factory(
    models.Answer,                       # specify which model this is for
    form = AnswerForm,                   # specify which form this is for
)

AnswerInlineFormSet = forms.inlineformset_factory(
    models.Question,
    models.Answer,
    extra=2,
    fields=('order', 'text', 'correct'),
    formset=AnswerFormSet,
    min_num=1,
)
