from django.urls import path, re_path

from . import views


urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('create_course/', views.CourseCreate.as_view(), name='course_create'),
    path('<int:course_pk>/t<int:step_pk>/', views.TextDetail.as_view(), name='text'),
    path('<int:course_pk>/q<int:step_pk>/', views.QuizDetail.as_view(), name='quiz'),
    path('<int:course_pk>/create_quiz/', views.quiz_create, name='create_quiz'),
    path('<int:course_pk>/edit_quiz/<int:quiz_pk>', views.quiz_edit, name='edit_quiz'),
    re_path(r'(?P<quiz_pk>\d+)/create_question/(?P<question_type>mc|tf)/$', views.create_question, name='create_question'),
    path('<int:quiz_pk>/edit_question/<int:question_pk>/', views.edit_question, name='edit_question'),
    path('<int:question_pk>/create_answer/', views.answer_form, name='create_answer'),
    path('by/<str:teacher>/', views.CoursesByTeacherView.as_view(), name='by_teacher'),
    path('search/', views.Search.as_view(), name='search'),
    path('<int:pk>/', views.CourseDetail.as_view(), name='detail'),
]
