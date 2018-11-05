from itertools import chain

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Sum
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic import(View, ListView, DetailView,
                                 CreateView, UpdateView, DeleteView
                                 )


from . import forms
from . import mixins
from . import models


class CourseListView(ListView):
    context_object_name = "courses"
    queryset = models.Course.objects.filter(
        published=True
    ).annotate(
        total_steps=Count('text', distinct=True)+Count('quiz', distinct=True)
    )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.queryset.aggregate(total=Sum('total_steps'))
        return context


class CourseCreate(LoginRequiredMixin, mixins.PageTitleMixin, CreateView):
    fields = ("title", "description", "teacher", "subject", "status")
    model = models.Course
    page_title = "Create a new course"  # This page title can be set as static


class CourseDetail(DetailView):
    model = models.Course
    template_name = 'courses/course_detail.html'

    def get_context_data(self, **kwargs):
        try:
            course = models.Course.objects.prefetch_related(
                'quiz_set',
                'text_set',
                'quiz_set__question_set'
            ).get(
                pk=self.kwargs.get('pk'),
                published=True)
        except models.Course.DoesNotExist:
            raise Http404
        else:
            steps = sorted(chain(
                course.text_set.all(),
                course.quiz_set.all()
            ), key=lambda step:step.order)
        return {'course': course, 'steps': steps}


class TextDetail(DetailView):
    template_name = 'courses/text_detail.html'
    context_object_name = 'step'

    def get_object(self, queryset=None):
        return get_object_or_404(models.Text,
                                 course_id=self.kwargs.get('course_pk'),
                                 pk=self.kwargs.get('step_pk'),
                                 course__published=True)


class QuizDetail(DetailView):
    template_name = 'courses/quiz_detail.html'
    context_object_name = 'step'

    def get_object(self, queryset=None):
        try:
            step = models.Quiz.objects.select_related(
                'course'
            ).prefetch_related(
                'question_set',
                'question_set__answer_set'
            ).get(
                course_id=self.kwargs.get('course_pk'),
                pk=self.kwargs.get('step_pk'),
                course__published=True
            )
        except models.Quiz.DoesNotExist:
            raise Http404
        else:
            return step


@login_required
def quiz_create(request, course_pk):
    course = get_object_or_404(models.Course,
                               pk=course_pk)
    form = forms.QuizForm()
    
    if request.method == 'POST':
        form = forms.QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Quiz added!")
            return HttpResponseRedirect(quiz.get_absolute_url())
    return render(request, 'courses/quiz_form.html', {'form': form, 'course': course})


@login_required
def quiz_edit(request, course_pk, quiz_pk):
    quiz = get_object_or_404(models.Quiz,
                             pk=quiz_pk,
                             course_id=course_pk)
    form = forms.QuizForm(instance=quiz)
    
    if request.method == 'POST':
        form = forms.QuizForm(instance=quiz, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated {}".format(form.cleaned_data['title']))
            return HttpResponseRedirect(quiz.get_absolute_url())
    return render(request, 'courses/quiz_form.html', {'form': form, 'course': quiz.course})


@login_required
def create_question(request, quiz_pk, question_type):
    quiz = get_object_or_404(models.Quiz,
                             pk=quiz_pk)
    if question_type == 'tf':
        form_class = forms.TrueFalseQuestionForm
    else:
        form_class = forms.MultipleChoiceQuestionForm
        
    form = form_class()
    answer_forms = forms.AnswerInlineFormSet(
        queryset=models.Answer.objects.none()
    )
    
    if request.method == 'POST':
        form = form_class(request.POST)
        answer_forms = forms.AnswerInlineFormSet(
            request.POST,
            queryset=models.Answer.objects.none,
        )

        if form.is_valid() and answer_forms.is_valid():
            # create and save question
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()

            answers = answer_forms.save(commit=False)
            for answer in answers:
                answer.question = question
                answer.save
            messages.success(request, "Added question")
            return HttpResponseRedirect(quiz.get_absolute_url())
    return render(request, 'courses/question_form.html', {
        'quiz': quiz,
        'form': form,
        'formset': answer_forms,
    })

@login_required
def edit_question(request, quiz_pk, question_pk):
    question = get_object_or_404(models.Question,
                                 pk=question_pk,
                                 quiz_id=quiz_pk)
    if hasattr(question, 'truefalsequestion'):
        form_class = forms.TrueFalseQuestionForm
        question = question.truefalsequestion
    else:
        form_class = forms.MultipleChoiceQuestionForm
        question = question.multiplechoicequestion
    form = form_class(instance=question)
    answer_forms = forms.AnswerInlineFormSet(
        queryset=form.instance.answer_set.all(),
    )

    if request.method == 'POST':
        form = form_class(request.POST, instance=question)
        answer_forms = forms.AnswerInlineFormSet(
            request.POST,
            queryset=form.instance.answer_set.all(),
        )

        if form.is_valid() and answer_forms.is_valid():
            form.save()
            answers = answer_forms.save(commit=False)
            for answer in answers:
                answer.question = question
                answer.save()
            for answer in answer_forms.deleted_objects:
                answer.delete()
            messages.success(request, "Updated question")
            return HttpResponseRedirect(question.quiz.get_absolute_url())
    return render(request, 'courses/question_form.html', {
        'form': form,
        'quiz': question.quiz,
        'formset': answer_forms,
    })


@login_required
def answer_form(request, question_pk):
    question = get_object_or_404(models.Question,
                                 pk=question_pk)
    formset = forms.AnswerFormSet(queryset=question.answer_set.all())

    if request.method == 'POST':
        formset = forms.AnswerFormSet(request.POST, queryset = question.answer_set.all())

    if formset.is_valid():
        answers = formset.save(commit=False)

        for answer in answers:
            answer.question = question
            answer.save()
        messages.success(request, "added answers")
        return HttpResponseRedirect(question.quiz.get_absolute_url())

    return render(request, "courses/answer_form.html", {
        'question': question,
        'formset': formset
    })


class CoursesByTeacherView(ListView):
    model = models.Course
    template_name = 'courses/course_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = self.model.objects.filter(
            teacher__username=self.kwargs.get('teacher'),
            published=True
        ).annotate(
            total_steps=Count('text', distinct=True) + Count('quiz', distinct=True)
        )
        context["courses"] = courses
        context["total"] = courses.aggregate(total=Sum('total_steps'))
        return context



class Search(ListView):
    model = models.Course
    template_name = 'courses/course_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        term = self.request.GET.get('q')
        courses = self.model.objects.filter(
            Q(title__icontains=term)|Q(description__icontains=term),
            published=True
        ).annotate(
            total_steps=Count('text', distinct=True) + Count('quiz', distinct=True)
        )
        context["courses"] = courses
        context["total"] = courses.aggregate(total=Sum('total_steps'))
        return context