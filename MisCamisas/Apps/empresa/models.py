from django.db import models


class Departamento(models.Model):
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefono')
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de edición")

    def __str__(self):
        return f"{self.nombre} ({self.telefono})"

    class Meta:
        verbose_name = "departamento"
        verbose_name_plural = "departamentos"
        ordering = ["-id"]


class Puestotrabajo(models.Model):
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de edición")

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        verbose_name = "Puesto trabajo"
        verbose_name_plural = "Puestos Trabajos"
        ordering = ["-id"]


class Empleado(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=True, null=True,
                                     verbose_name="Departamento")
    Puestotrabajo = models.ForeignKey(Puestotrabajo, on_delete=models.CASCADE, blank=True, null=True,
                                      verbose_name="Puesto Trabajo")
    nombre = models.CharField(max_length=40, verbose_name='Nombre')
    apellidos = models.CharField(max_length=50, blank=True, null=True, verbose_name='Apellidos')
    direccion = models.CharField(max_length=50, blank=True, null=True, verbose_name='Direccion')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Telefono')
    imagen = models.ImageField(blank=True, null=True, verbose_name='Imagen')
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de edición")

    def __str__(self):
        return f"{self.nombre} {(self.apellidos)}"

    class Meta:
        verbose_name = "empleado"
        verbose_name_plural = "empleados"
        ordering = ["-id"]

class Encargado(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, blank=True, null=True,)
    Departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, blank=True, null=True,)

