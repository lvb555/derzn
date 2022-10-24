from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms.formsets import formset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.template import Context, RequestContext
from django.urls import reverse_lazy
from drevo.models.author import Author
from drevo.models.knowledge import Znanie
from drevo.models.knowledge_kind import Tz

from .forms import AnswerFormset, InterviewForm, QuestionFormset, ZnForm
from .models import Interview, Question, QuestionAnswer


def pages(request, interview_list):
    interview_in_page = settings.RECORDS_IN_PAGE
    paginator = Paginator(interview_list, interview_in_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@login_required
def interview_index(request):
    """Переспективная вьюха просмотра списка своих интервью"""
    user = request.user
    interview_list = user.survey.all()
    context = {'page_obj': pages(request, interview_list)}
    return render(request, 'drevo/interview_index.html', context)


def interview_create(request):
    zn_form = ZnForm(
            request.POST or None,
            files=request.FILES or None,
        )
    zn = Znanie()
    interview = Interview()
    if request.method == 'POST':
        i_form = InterviewForm(
            request.POST or None,
            instance=zn)
        q_formset = QuestionFormset(request.POST, instance=interview)
        if zn_form.is_valid() and i_form.is_valid() and q_formset.is_valid():
            zn.name = zn_form.cleaned_data['name']
            zn.category = zn_form.cleaned_data['category']
            zn.author = zn_form.cleaned_data['author']
            zn.user = request.user
            zn.tz = get_object_or_404(Tz, name='Интервью')
            zn.save()
            interview.date_from = i_form.cleaned_data['date_from']
            interview.date_to = i_form.cleaned_data['date_to']
            interview.name = zn
            interview.author = request.user
            interview.save()
            for position, q_form in enumerate(q_formset.forms, start=1):
                q_data = q_form.cleaned_data
                if 'question' in q_data:
                    q_form.save()
            return redirect('interview_detail', interview_id=interview.pk)
    else:
        zn_form = ZnForm()
        i_form = InterviewForm()
        q_formset = QuestionFormset(instance=interview)
        
    context = {
        'zn_form': zn_form,
        'i_form': i_form,
        'q_formset': q_formset,
    }
    return render(request, 'drevo/interview_create.html', context)


@login_required
def interview_detail(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    questions = interview.interview_question.all()
    context = {
        'interview': interview,
        'questions': questions
    }
    return render(request, 'drevo/interview_detail.html', context)


@login_required
def interview_edit(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id)
    zn = get_object_or_404(Znanie, pk=interview.name.pk)
    questions = interview.interview_question.all()
    zn_form = ZnForm(
        request.POST or None,
        files=request.FILES or None,
        instance=zn
    )
    i_form = InterviewForm(
        request.POST or None,
        files=request.FILES or None,
        instance=interview
    )
    q_formset = QuestionFormset(request.POST or None, instance=interview)
    if request.user != interview.author:
        return redirect('interview_detail', interview_id)
    if zn_form.is_valid() and i_form.is_valid() and q_formset.is_valid():
        zn.name = zn_form.cleaned_data['name']
        zn.category = zn_form.cleaned_data['category']
        zn.author = zn_form.cleaned_data['author']
        zn.user = request.user
        zn.tz = get_object_or_404(Tz, name='Интервью')
        zn.save()
        interview.date_from = i_form.cleaned_data['date_from']
        interview.date_to = i_form.cleaned_data['date_to']
        interview.author = request.user
        interview.save()
        for position, q_form in enumerate(q_formset.forms, start=1):
                q_data = q_form.cleaned_data
                if 'question' in q_data:
                    q_form.save()
        return redirect('interview_detail', interview_id)
    context = {
        'zn_form': zn_form,
        'i_form': i_form,
        'q_formset': q_formset,
    }
    return render(request, 'drevo/interview_create.html', context)
