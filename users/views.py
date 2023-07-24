from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.shortcuts import HttpResponseRedirect, render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import auth, messages
from django.views.generic import FormView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.views.generic.edit import ProcessFormView
import json
import uuid
import base64
from django.core.files.base import ContentFile
from drevo.models import InterviewAnswerExpertProposal, Znanie, KnowledgeStatuses, QuizResult, BrowsingHistory, \
    FriendsInviteTerm, Message
from drevo.models.feed_messages import FeedMessage
from drevo.models.special_permissions import SpecialPermissions
from users.forms import UserLoginForm, UserRegistrationForm, UserModelForm
from users.forms import ProfileModelForm, UserPasswordRecoveryForm
from users.forms import UserSetPasswordForm
from users.forms.password_change_form import MyPasswordChangeForm
from users.models import User, Profile, MenuSections, Favourite
from drevo.models.settings_options import SettingsOptions
from drevo.models.user_parameters import UserParameters
from drevo.models.special_permissions import SpecialPermissions


class LoginFormView(FormView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('drevo')
    form_class = UserLoginForm

    def form_valid(self, form):
        auth.login(self.request, form.get_user())

        next_url = self.request.session.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context

    def get(self, request, *args, **kwargs):
        next_url = request.GET.get('next')
        if next_url:
            request.session['next'] = next_url

        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:myprofile'))
        return super().get(request, *args, **kwargs)


class RegistrationFormView(CreateView):
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    form_class = UserRegistrationForm
    model = User

    @staticmethod
    def email_validation(email):
        if User.objects.filter(email=email).exists():
            return False
        return True

    @staticmethod
    def username_validation(username):
        if User.objects.filter(username=username).exists():
            return False
        return True

    @staticmethod
    def password_validation(form):
        password1 = form.data.get('password1')
        password2 = form.data.get('password2')
        if password1 and password2:
            if password1 != password2:
                return False
        return True

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.method == 'POST':
            email = form.data.get('email')
            username = form.data.get('username')

            if email:
                if not self.email_validation(email):
                    messages.error(self.request, 'Пользователь с таким адресом эл. почты уже существует.')

            if username:
                if not self.username_validation(username):
                    messages.error(self.request, 'Имя пользователя уже занято.')

            if not self.password_validation(form):
                messages.error(self.request, 'Введенные пароли не совпадают.')

        return form

    def form_valid(self, form):
        if form.is_valid():
            user = form.save()
            # Создаём записи таблицы "Параметры пользователя" на основе таблицы "Параметры настроек"
            settings_options = SettingsOptions.objects.filter(admin=False)
            user_settings = [
                UserParameters(user=user, param=param, param_value=param.default_param) for param in settings_options
            ]
            UserParameters.objects.bulk_create(user_settings)

            profile = user.profile
            profile.patronymic = form.cleaned_data['patronymic']
            profile.gender = form.cleaned_data['gender']
            profile.birthday_at = form.cleaned_data['birthday_at']
            avatar = form.cleaned_data['image']

            if avatar:
                image, error = form.validate_avatar_size()

                if image:
                    if error:
                        messages.error(self.request, error)
                    else:
                        image.name = f'{user.username}.{image.name.split(".")[-1]}'
                        profile.avatar = avatar

            profile.deactivate_user()
            profile.generate_activation_key()
            profile.send_verify_mail()

            messages.success(
                self.request,
                'Вы успешно зарегистрировались! '
                'Для подтверждения учетной записи перейдите по ссылке, '
                'отправленной на адрес электронной почты, '
                'указанный Вами при регистрации.'
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('drevo'))
        return super().get(request, *args, **kwargs)


class LogoutFormView(LoginRequiredMixin, FormView):
    def get(self, request, *args, **kwargs):
        auth.logout(self.request)

        next_url = request.GET.get('next')
        if next_url:
            return HttpResponseRedirect(next_url)

        return HttpResponseRedirect(reverse('drevo'))


class UserProfileFormView(LoginRequiredMixin, UpdateView):
    template_name = 'users/myprofile.html'
    success_url = reverse_lazy('users:myprofile')
    form_class = UserModelForm
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = ProfileModelForm(
            instance=Profile.objects.get(user=self.object)
        )
        context['sections'] = [i.name for i in self.object.sections.all()]
        context['access'] = access_sections(self.object)
        context['activity'] = [i for i in context['sections'] if i.startswith('Мои') or i.startswith('Моя')]
        context['link'] = 'users:myprofile'
        context['change_password_form'] = MyPasswordChangeForm(user=self.request.user)
        context['user'] = self.request.user
        invite_count = FriendsInviteTerm.objects.filter(recipient=self.request.user.id).count()
        context['invite_count'] = invite_count if invite_count else 0
        context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient=self.request.user, was_read=False).count()
        context['new_messages'] = Message.objects.filter(recipient=self.request.user, was_read=False).count()
        context['new'] = int(context['new_knowledge_feed']) + int(
            context['invite_count'] + int(context['new_messages']))
        return context

    def get_object(self, queryset=None):
        self.kwargs[self.pk_url_kwarg] = self.request.user.id
        return super().get_object()

    def form_valid(self, form):
        profile_form = self.get_form(ProfileModelForm)
        profile_form.instance = Profile.objects.get(user=self.object)

        if profile_form.is_valid():
            image, error = profile_form.validate_avatar_size()
            avatar = self.request.POST.get('generated_image')

            if image:
                if error:
                    messages.error(self.request, error)
                else:
                    image.name = f'{self.request.user.username}.{image.name.split(".")[-1]}'
                    profile_form.instance.avatar = image
            elif avatar:
                if avatar == '/static/src/default_avatar.jpg':
                    profile_form.instance.avatar = None
                # Убираем название в начале строки и декодируем ее(base64) в бинарные данные изображения
                # Размер такого изображения не превышает 1мб при любых буквах
                else:
                    image_data = avatar.split(',')[1]
                    decoded_image_data = base64.b64decode(image_data)
                    image_file = ContentFile(decoded_image_data, name=f'{self.request.user.username}.png')
                    profile_form.instance.avatar = image_file

            profile_form.save()

        return super().form_valid(form)


class UserProfileTemplateView(LoginRequiredMixin, TemplateView):
    template_name = 'users/usersprofile.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['object'] = None

        _id = self.kwargs.get(self.pk_url_kwarg)
        if _id:
            _object = get_object_or_404(User, id=_id)

            if _object:
                context['object'] = _object

        try:
            users_categories = SpecialPermissions.objects.get(expert = _id)
            context['users_categories'] = users_categories
        except:
            context['users_categories'] = False

        context['title'] = f'Профиль пользователя {_object.username}'
        return context


class UserVerifyView(TemplateView):
    template_name = 'users/verification.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response.context_data['user'] = None

        username = kwargs.get('username')
        activation_key = kwargs.get('activation_key')

        if username and activation_key:
            user = User.objects.get(username=username)

            if user:
                if user.profile.verify(username, activation_key):
                    auth.login(request, user)
                    response.context_data['user'] = user

        return response


class UserPasswordRecoveryFormView(FormView):
    template_name = 'users/password_recovery.html'
    success_url = reverse_lazy('users:login')
    form_class = UserPasswordRecoveryForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.method == 'POST':
            email = form.data.get('email')
            if email:
                users_set = User.objects.filter(email=email)

                if not users_set.exists():
                    form.add_error(None, 'Пользователя с таким адресом эл. почты не существует.')

        return form

    def form_valid(self, form):
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.get(email=email)
            profile = user.profile
            profile.generate_password_recovery_key()
            profile.send_password_recovery_mail()
            messages.success(
                self.request,
                'Письмо со ссылкой для восстановления пароля '
                'отправлено на указанный адрес эл. почты.')

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('users:myprofile'))
        return super().get(request, *args, **kwargs)


class UserSetPasswordFormView(FormView):
    template_name = 'users/password_recovery_update.html'
    success_url = reverse_lazy('users:login')
    form_class = UserSetPasswordForm

    def form_valid(self, form):
        if form.is_valid():
            email = self.kwargs.get('email')
            key = self.kwargs.get('password_recovery_key')

            if email and key:
                user = User.objects.get(email=email)
                profile = user.profile

                if profile.recovery_valid(email, key):
                    form.save()

                    profile.password_recovery_key = ''
                    profile.password_recovery_key_expires = None
                    profile.save()

                    messages.success(self.request, 'Ваш пароль успешно изменён.')
                    return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        context['full_url'] = self.request.get_full_path()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        email = self.kwargs.get('email')

        user = User.objects.get(email=email)
        kwargs['user'] = user

        return kwargs

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            raise Http404

        email = self.kwargs.get('email')
        key = self.kwargs.get('password_recovery_key')

        if not email or not key:
            raise Http404

        user = get_object_or_404(User, email=email)
        self.kwargs['user'] = user

        if not user.profile.recovery_valid(email, key):
            raise Http404

        return super().get(request, *args, **kwargs)


class MenuSectionsAdd(ProcessFormView):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            user = request.user
            sections = json.loads(request.GET.get('sections'))
            publicity = request.GET.get('publicity')
            if publicity == 'false':
                user.is_public = False
            elif publicity == 'true':
                user.is_public = True
            user.sections.clear()
            for section in sections:
                obj = get_object_or_404(MenuSections, name=section)
                user.sections.add(obj)
            user.save()
            return JsonResponse({}, status=200)

        raise Http404


@login_required
def my_profile(request):
    if request.method == 'GET':
        success_url = reverse_lazy('users:my_profile')
        context = {}
        user = User.objects.get(id=request.user.id)
        context['user'] = user
        context['sections'] = access_sections(user)
        invite_count = FriendsInviteTerm.objects.filter(recipient=request.user.id).count()
        context['invite_count'] = invite_count if invite_count else 0
        context['new_knowledge_feed'] = FeedMessage.objects.filter(recipient=user, was_read=False).count()
        context['new_messages'] = Message.objects.filter(recipient=user, was_read=False).count()
        context['new'] = int(context['new_knowledge_feed']) + int(
            context['invite_count'] + int(context['new_messages']))
    return render(request, 'users/profile_header.html', context)

def access_sections(user):
    #Проверяем какие опции меню будут отображаться
    sections = ['Мои оценки знаний','По категориям','По авторам','По тегам']
    interview = InterviewAnswerExpertProposal.objects.filter(expert=user)
    if interview:
        if interview.exclude(Q(new_answer_text=None) | Q(new_answer_text='')).exists():
            sections.extend(['Мои предложения','Интервью'])
        if interview.filter(Q(new_answer_text=None) | Q(new_answer_text='')).exists():
            sections.extend(['Мои интервью','Интервью'])
    knowledges = KnowledgeStatuses.objects.filter(user=user)
    if knowledges:
        if knowledges.filter(status='PUB_PRE').exists():
            sections.append('Мои знания (пользовательский вклад)')
        if knowledges.filter(status='PUB').exists():
            sections.append('Мои знания')
    if Znanie.published.filter(expert=user).exists():
        sections.append('Мои экспертизы')
    if Favourite.objects.filter(user=user).exists():
        sections.append('Избранные знания')
    if BrowsingHistory.objects.filter(user=user).exists():
        sections.append('История просмотров')
    if QuizResult.objects.filter(user=user).exists():
        sections.append('Результаты тестов')
    if user.is_expert is True or user.is_redactor is True or user.is_director is True:
        sections.append('Компетенции')
    return sections

@login_required
def change_username(request):
    if request.method == 'POST':
        if 'new_username' in request.POST:
            new_username = request.POST['new_username']
            # Проверяем, что новый логин уникален
            if User.objects.filter(username=new_username).exists():
                messages.error(request, 'Этот логин уже занят.')
            else:
                user = request.user
                user.username = new_username
                user.save()
                messages.success(request, 'Логин успешно изменен.')

        elif 'old_password' in request.POST:
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, 'Пароль успешно изменен.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{error}')

        elif 'new_email' in request.POST:
            user = request.user
            user.email = request.POST['new_email']
            profile = user.profile
            profile.deactivate_user()
            profile.generate_activation_key()
            profile.send_verify_mail()
            messages.success(
                request,
                'Вы успешно сменили адрес почты! '
                'Для подтверждения учетной записи перейдите по ссылке, '
                'отправленной на адрес электронной почты, '
                'указанный Вами при смене данных.'
            )

        elif 'delete-account' in request.POST:
            user = request.user
            user.username = str(uuid.uuid4())
            user.first_name = '***********'
            user.last_name = '***********'
            user.email = None
            user.is_public = False
            user.save()
            logout(request)

    return redirect('users:myprofile')
