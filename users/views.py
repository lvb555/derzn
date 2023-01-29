from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib import auth, messages
from django.views.generic import FormView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.views.generic.edit import ProcessFormView
import json
from drevo.models.expert_category import CategoryExpert
from users.forms import UserLoginForm, UserRegistrationForm, UserModelForm
from users.forms import ProfileModelForm, UserPasswordRecoveryForm
from users.forms import UserSetPasswordForm
from users.models import User, Profile, MenuSections
from drevo.models.settings_options import SettingsOptions
from drevo.models.user_parameters import UserParameters


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
        expert = self.object.expert.all()
        if expert:
            expert = expert[0]
            competence = expert.categories.all()
            context['competence'] = competence
        context['title'] = 'Ваш профиль'
        context['profile_form'] = ProfileModelForm(
            instance=Profile.objects.get(user=self.object)
        )
        context['sections'] = [i.name for i in self.object.sections.all()]
        return context

    def get_object(self, queryset=None):
        self.kwargs[self.pk_url_kwarg] = self.request.user.id
        return super().get_object()

    def form_valid(self, form):
        profile_form = self.get_form(ProfileModelForm)
        profile_form.instance = Profile.objects.get(user=self.object)

        if profile_form.is_valid():
            image, error = profile_form.validate_avatar_size()

            if image:
                if error:
                    messages.error(self.request, error)
                else:
                    image.name = f'{self.request.user.username}.{image.name.split(".")[-1]}'
                    profile_form.instance.avatar = image

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
            users_categories = CategoryExpert.objects.get(expert = _id)
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
            print(user.username)
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
            user.sections.clear()
            for section in sections:
                obj = get_object_or_404(MenuSections, name=section)
                user.sections.add(obj)

            return JsonResponse({}, status=200)

        raise Http404
