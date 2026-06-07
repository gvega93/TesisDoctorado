from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.db import transaction
import uuid

class Beneficiario(AbstractUser):
    """Usuario vulnerable que recibe las ganancias de la plataforma."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telefono_nequi = models.CharField(max_length=20, unique=True, help_text="Número para pagos vía Nequi")
    email = models.EmailField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    groups = models.ManyToManyField('auth.Group', related_name='beneficiario_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='beneficiario_permissions', blank=True)

    class Meta:
        verbose_name = "Beneficiario"
        verbose_name_plural = "Beneficiarios"

    def __str__(self):
        return f"{self.username} - Nequi: {self.telefono_nequi}"

class Portal(models.Model):
    """La tienda digital automatizada del usuario."""
    ESTADOS_PORTAL = [('activo', 'Activo'), ('suspendido', 'Suspendido'), ('en_creacion', 'En Creación')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    beneficiario = models.ForeignKey(Beneficiario, on_delete=models.CASCADE, related_name='portales')
    nombre_sitio = models.CharField(max_length=100)
    dominio = models.URLField(unique=True)
    sub_id_afiliado = models.CharField(max_length=100, unique=True, help_text="ID único para Amazon Associates")
    nicho = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADOS_PORTAL, default='en_creacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_sitio} ({self.beneficiario.username})"

class BilleteraUsuario(models.Model):
    """Control financiero estricto para cobros de IA y ganancias de Amazon."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    beneficiario = models.OneToOneField(Beneficiario, on_delete=models.CASCADE, related_name='billetera')
    saldo_consumo_ia = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    ganancias_acumuladas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def descontar_consumo_ia(self, monto):
        with transaction.atomic():
            billetera = BilleteraUsuario.objects.select_for_update().get(pk=self.pk)
            if billetera.saldo_consumo_ia >= monto:
                billetera.saldo_consumo_ia -= monto
                billetera.save()
                self.saldo_consumo_ia = billetera.saldo_consumo_ia
                return True
            raise ValueError("Saldo de IA insuficiente para esta operación.")

    def abonar_ganancias(self, monto):
        with transaction.atomic():
            billetera = BilleteraUsuario.objects.select_for_update().get(pk=self.pk)
            billetera.ganancias_acumuladas += monto
            billetera.save()
            self.ganancias_acumuladas = billetera.ganancias_acumuladas

    def __str__(self):
        return f"Wallet de {self.beneficiario.username} | IA: ${self.saldo_consumo_ia}"

class Tendencia(models.Model):
    """Registro de lo que es popular en el mundo."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    termino_busqueda = models.CharField(max_length=200)
    fuente = models.CharField(max_length=50)
    puntuacion_viral = models.IntegerField(default=0)
    fecha_deteccion = models.DateTimeField(auto_now_add=True)
    procesado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('termino_busqueda', 'fuente')

    def __str__(self):
        return f"[{self.fuente}] {self.termino_busqueda}"

class Articulo(models.Model):
    """El producto final escrito por la IA, listo para vender."""
    CATEGORIAS = [
        ('tecnologia', 'Tecnología'),
        ('hogar', 'Hogar'),
        ('belleza', 'Belleza'),
        ('moda_femenina', 'Moda Femenina') # <--- AQUÍ ESTÁ EL CAMBIO
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portal = models.ForeignKey(Portal, on_delete=models.CASCADE, related_name='articulos')
    tendencia = models.ForeignKey(Tendencia, on_delete=models.SET_NULL, null=True, blank=True)
    
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='tecnologia')
    titulo = models.CharField(max_length=255)
    resumen = models.CharField(max_length=300, default="Descubre las mejores ofertas y análisis detallado de este producto.")
    imagen_url = models.URLField(max_length=500, default="https://loremflickr.com/800/500/tecnologia")
    
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    contenido_html = models.TextField()
    idioma = models.CharField(max_length=50, default="Español")
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    vistas = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
            original_slug = self.slug
            contador = 1
            while Articulo.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{contador}'
                contador += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} - {self.categoria}"