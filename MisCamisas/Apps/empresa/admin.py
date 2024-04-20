from django.contrib import admin

from Apps.empresa.models import Departamento, Empleado, Encargado, Puestotrabajo

admin.site.register(Departamento)
admin.site.register(Empleado)
admin.site.register(Puestotrabajo)
admin.site.register(Encargado)



