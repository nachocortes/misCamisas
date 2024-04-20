from django.urls import path
from .views import HomeView, RegisterView, ProfileView, ErrorView, ProfilePasswordChangeView, AddUserView, CustomLoginView, UserDetailsView, superuser_edit
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # PAGINA DE INICIO
    path('', HomeView.as_view(), name='home'),

    # PAGINAS DE LOGIN Y REGISTRO (VIDEO 5)


    # PAGINAS DE PERFIL: VISTA DE PERFIL - EDICION DEL PERFIL (VIDEO 8)
    path('profile/', login_required(ProfileView.as_view()), name='profile'),

    # PAGINAS QUE ADMINISTRAN LOS CURSOS: LA LISTA DE CURSOS - (LA CREACION DE CURSOS - LA EDICION DE CURSOS - LA ELIMINACION DE CURSOS) (VIDEO 10)

    # INSCRIPCION DE UN ALUMNO EN UN CURSO
    path('error/', login_required(ErrorView.as_view()), name='error'),

    # PAGINA DE VISTA DE INSCRIPCION

    # PAGINAS ADMINISTRACION DE NOTAS: (LISTA DE ESTUDIANTES POR CURSO - EDICION DE NOTAS)

    # PAGINAS DE ASISTENCIAS: (LISTA DE ESTUDIANTES POR CURSO - AGREGAR ASISTENCIAS)

    # EVOLUCION DEL ESTUDIANTE

    # CAMBIO DE CONTRASEÑA
    path('password_change/', login_required(ProfilePasswordChangeView.as_view()), name='profile_password_change'),

    # AGREGAR NUEVO USUARIO
    path('add_user/', AddUserView.as_view(), name='add_user'),

    # NUEVO LOGIN
    path('login/', CustomLoginView.as_view(), name='custom_login'),

    # VISUALIZAR EL PERFIL DE UN USUARIO
    path('user_details/<int:pk>/', UserDetailsView.as_view(), name='user_details'),

    # EDITAR DATOS DEL USUARIO
    path('superuser_edit/<int:user_id>/', login_required(superuser_edit), name='superuser_edit'),
]