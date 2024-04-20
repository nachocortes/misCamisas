import os
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.models import Group
from .forms import RegisterForm, UserForm, ProfileForm, UserCreationForm
from django.views import View
from .models import Registration
from django.contrib.auth.models import User
from Apps.accounts.models import Profile
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView


# FUNCION PARA CONVERTIR EL PLURAL DE UN GRUPO A SU SINGULAR
def plural_to_singular(plural):
    # Diccionario de palabras
    plural_singular = {
        "clientes": "cliente",
        "comerciale": "comercial",
        "ventas": "venta",
        "compras": "compra",
        "rrhhs": "rrhh",
        "admins": "admin"
    }

    return plural_singular.get(plural, "error")


# OBTENER COLOR Y GRUPO DE UN USUARIO
def get_group_and_color(user):
    group = user.groups.first()
    group_id = None
    group_name = None
    group_name_singular = None
    color = None

    if group:
        if group.name == 'clientes':
            color = 'bg-primary'
        elif group.name == 'comerciales':
            color = 'bg-dark'
        elif group.name == 'ventas':
            color = 'bg-success'
        elif group.name == 'compras':
            color = 'bg-secondary'
        elif group.name == 'rrhhs':
            color = 'bg-danger'
        elif group.name == 'admins':
            color = 'bg-info'

        group_id = group.id
        group_name = group.name
        group_name_singular = plural_to_singular(group.name)

    return group_id, group_name, group_name_singular, color


# DECORADOR PERSONALIZADO
def add_group_name_to_context(view_class):
    original_dispatch = view_class.dispatch

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        group_id, group_name, group_name_singular, color = get_group_and_color(user)

        context = {
            'group_name': group_name,
            'group_name_singular': group_name_singular,
            'color': color
        }

        self.extra_context = context
        return original_dispatch(self, request, *args, **kwargs)

    view_class.dispatch = dispatch
    return view_class


# PAGINA DE INICIO
@add_group_name_to_context
class HomeView(TemplateView):
    template_name = 'home.html'


# REGISTRO DE USUARIOS
class RegisterView(View):
    def get(self, request):
        data = {
            'form': RegisterForm()
        }
        return render(request, 'registration/register.html', data)

    def post(self, request):
        user_creation_form = RegisterForm(data=request.POST)
        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(username=user_creation_form.cleaned_data['username'],
                                password=user_creation_form.cleaned_data['password1'])
            login(request, user)

            # Actualizar el campo created_by_admin del modelo Profile
            user.profile.created_by_admin = False
            user.profile.save()

            return redirect('home')
        data = {
            'form': user_creation_form
        }
        return render(request, 'registration/register.html', data)



# PAGINA DE PERFIL
@add_group_name_to_context
class ProfileView(TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_form'] = UserForm(instance=user)
        context['profile_form'] = ProfileForm(instance=user.profile)

        if user.groups.first().name == 'profesores':
            # Obtener todos los cursos asignados al profesor
            assigned_courses = Course.objects.filter(teacher=user).order_by('-id')
            inscription_courses = assigned_courses.filter(status='I')
            progress_courses = assigned_courses.filter(status='P')
            finalized_courses = assigned_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'estudiantes':
            # Obtener todos los cursos donde esta inscripto el estudiante
            student_id = user.id
            registrations = Registration.objects.filter(student=user)
            enrolled_courses = []
            inscription_courses = []
            progress_courses = []
            finalized_courses = []

            for registration in registrations:
                course = registration.course
                enrolled_courses.append(course)

                if course.status == 'I':
                    inscription_courses.append(course)
                elif course.status == 'P':
                    progress_courses.append(course)
                elif course.status == 'F':
                    finalized_courses.append(course)

            context['student_id'] = student_id
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'preceptores':
            # Obtener todos los cursos existentes
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(status='I')
            progress_courses = all_courses.filter(status='P')
            finalized_courses = all_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'administrativos':
            # Obtengo todos los usuarios que no pertenecen al grupo administrativos
            admin_group = Group.objects.get(name='administrativos')
            all_users = User.objects.exclude(groups__in=[admin_group])

            # Obtengo todos los grupos
            all_groups = Group.objects.all()

            # Obtengo cada perfil de usuario
            user_profiles = []
            for user in all_users:
                profile = user.profile
                user_groups = user.groups.all()
                processed_groups = [plural_to_singular(group.name) for group in user_groups]
                user_profiles.append({
                    'user': user,
                    'groups': processed_groups,
                    'profile': profile
                })

            context['user_profiles'] = user_profiles

            # Obtener todos los cursos existentes
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(status='I')
            progress_courses = all_courses.filter(status='P')
            finalized_courses = all_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Redireccionar a la pagina de perfil (con datos actualizados)
            return redirect('profile')

        # Si alguno de los datos no es valido
        context = self.get_context_data()
        context['user_form'] = user_form
        context['profile_form'] = profile_form
        return render(request, 'profile/profile.html', context)



# PAGINA DE ERROR DE ACCESO A PAGINA NO PERMITIDA
@add_group_name_to_context
class ErrorView(TemplateView):
    template_name = 'error.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error_image_path = os.path.join(settings.MEDIA_URL, 'error.png')
        context['error_image_path'] = error_image_path
        return context


# CAMBIAR LA CONTRASEÑA DEL USUARIO
@add_group_name_to_context
class ProfilePasswordChangeView(PasswordChangeView):
    template_name = 'profile/change_password.html'
    success_url = reverse_lazy('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_changed'] = self.request.session.get('password_changed', False)
        return context

    def form_valid(self, form):
        # Actualizar el campo created_by_admin del modelo Profile
        profile = Profile.objects.get(user=self.request.user)
        profile.created_by_admin = False
        profile.save()

        messages.success(self.request, 'Cambio de contraseña exitoso')
        update_session_auth_hash(self.request, form.user)
        self.request.session['password_changed'] = True
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Hubo un error al momento de intentar cambiar la contraseña: {}.'.format(
                form.errors.as_text()
            )
        )
        return super().form_invalid(form)


# AGREGAR UN NUEVO USUARIO
@add_group_name_to_context
class AddUserView(UserPassesTestMixin, LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'add_user.html'
    success_url = '/profile/'

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('error')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups = Group.objects.all()
        singular_groups = [plural_to_singular(group.name).capitalize() for group in groups]
        context['groups'] = zip(groups, singular_groups)
        return context

    def form_valid(self, form):
        # Obtener el grupo que seleccionó
        group_id = self.request.POST['group']
        group = Group.objects.get(id=group_id)

        # Crear usuario sin guardarlo aún
        user = form.save(commit=False)

        # Colocamos una contraseña por defecto -Aca podría ir la lógica para crear una contraseña aleatoria-
        user.set_password('contraseña')

        # Convertir a un usuario al staff
        if group_id != '1':
            user.is_staff = True

        # Creamos el usuario
        user.save()

        # Agregamos el usuario al grupo seleccionado
        user.groups.clear()
        user.groups.add(group)

        return super().form_valid(form)


# LOGIN PERSONALIZADO
@add_group_name_to_context
class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)

        # Acceder al perfil del usuario
        profile = self.request.user.profile

        # Verificamos el valor del campo created_by_admin
        if profile.created_by_admin:
            messages.info(self.request, 'BIENVENIDO, Cambie su contraseña ahora !!!')
            response['Location'] = reverse_lazy('profile_password_change')
            response.status_code = 302

        return response

    def get_success_url(self):
        return super().get_success_url()


# VISUALIZACION DEL PERFIL DE UN USUARIO
@add_group_name_to_context
class UserDetailsView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user_details.html'
    context_object_name = 'user_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        group_id, group_name, group_name_singular, color = get_group_and_color(user)

        # Obtengo todos los grupos
        groups = Group.objects.all()
        singular_names = [plural_to_singular(group.name).capitalize() for group in groups]
        groups_ids = [group.id for group in groups]
        singular_groups = zip(singular_names, groups_ids)
        context['group_id_user'] = group_id
        context['group_name_user'] = group_name
        context['group_name_singular_user'] = group_name_singular
        context['color_user'] = color
        context['singular_groups'] = singular_groups

        if user.groups.first().name == 'profesores':
            # Obtener todos los cursos asignados al profesor
            assigned_courses = Course.objects.filter(teacher=user).order_by('-id')
            inscription_courses = assigned_courses.filter(status='I')
            progress_courses = assigned_courses.filter(status='P')
            finalized_courses = assigned_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'estudiantes':
            # Obtener todos los cursos donde esta inscripto el estudiante
            student_id = user.id
            registrations = Registration.objects.filter(student=user)
            enrolled_courses = []
            inscription_courses = []
            progress_courses = []
            finalized_courses = []

            for registration in registrations:
                course = registration.course
                enrolled_courses.append(course)

                if course.status == 'I':
                    inscription_courses.append(course)
                elif course.status == 'P':
                    progress_courses.append(course)
                elif course.status == 'F':
                    finalized_courses.append(course)

            context['student_id'] = student_id
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses

        elif user.groups.first().name == 'preceptores':
            # Obtener todos los cursos existentes
            all_courses = Course.objects.all()
            inscription_courses = all_courses.filter(status='I')
            progress_courses = all_courses.filter(status='P')
            finalized_courses = all_courses.filter(status='F')
            context['inscription_courses'] = inscription_courses
            context['progress_courses'] = progress_courses
            context['finalized_courses'] = finalized_courses
        return context


# GRABACION DE LOS DATOS DE UN USUARIO
def superuser_edit(request, user_id):
    if not request.user.is_superuser:
        return redirect('error')

    user = User.objects.get(pk=user_id)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)
        group = request.POST.get('group')

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            user.groups.clear()
            user.groups.add(group)
            return redirect('user_details', pk=user.id)
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profile/user_details.html', context)
