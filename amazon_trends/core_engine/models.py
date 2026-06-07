from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import transaction
import uuid
from django.utils.text import slugify

# Reemplazamos el usuario por defecto de Django por nuestro Beneficiario
class Beneficiario(AbstractUser):
    # Usamos UUID para mayor seguridad al escalar
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telefono_nequi = models.CharField(max_length=15, unique=True, help_text="Número para pagos vía Nequi/Daviplata")
    # Hacemos que email sea opcional para la población vulnerable
    email = models.EmailField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    # Resolviendo conflictos de AbstractUser para los related_name
    groups = models.ManyToManyField('auth.Group', related_name='beneficiario_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='beneficiario_permissions', blank=True)

    class Meta:
        verbose_name = "Beneficiario"
        verbose_name_plural = "Beneficiarios"

    def __str__(self):
        return f"{self.username} - Nequi: {self.telefono_nequi}"

class Portal(models.Model):
    ESTADOS_PORTAL = [
        ('activo', 'Activo'),
        ('suspendido', 'Suspendido'),
        ('en_creacion', 'En Creación')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # FK referenciando dinámicamente sin quemar IDs
    beneficiario = models.ForeignKey(Beneficiario, on_delete=models.CASCADE, related_name='portales')
    nombre_sitio = models.CharField(max_length=100)
    dominio = models.URLField(unique=True)
    sub_id_afiliado = models.CharField(max_length=100, unique=True, help_text="ID único para Amazon Associates")
    nicho = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADOS_PORTAL, default='en_creacion')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Portal"
        verbose_name_plural = "Portales"

    def __str__(self):
        return f"{self.nombre_sitio} ({self.dominio})"

class BilleteraUsuario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # OneToOne para que cada usuario tenga exactamente una billetera
    beneficiario = models.OneToOneField(Beneficiario, on_delete=models.CASCADE, related_name='billetera')
    
    # Dinero para que los agentes operen
    saldo_consumo_ia = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    # Dinero generado para pago a Nequi
    ganancias_acumuladas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Billetera de Usuario"
        verbose_name_plural = "Billeteras de Usuarios"

    def descontar_consumo_ia(self, monto):
        """Descuenta el costo de la operación de IA de forma segura."""
        with transaction.atomic():
            # Bloqueamos la fila para evitar condiciones de carrera (dos agentes cobrando al mismo tiempo)
            billetera = BilleteraUsuario.objects.select_for_update().get(pk=self.pk)
            if billetera.saldo_consumo_ia >= monto:
                billetera.saldo_consumo_ia -= monto
                billetera.save()
                # Actualizamos la instancia en memoria
                self.saldo_consumo_ia = billetera.saldo_consumo_ia
                return True
            else:
                raise ValueError("Saldo de IA insuficiente para esta operación.")

    def abonar_ganancias(self, monto):
        """Suma las comisiones de Amazon a la billetera."""
        with transaction.atomic():
            billetera = BilleteraUsuario.objects.select_for_update().get(pk=self.pk)
            billetera.ganancias_acumuladas += monto
            billetera.save()
            self.ganancias_acumuladas = billetera.ganancias_acumuladas

    def __str__(self):
        return f"Billetera de {self.beneficiario.username} | Saldo IA: {self.saldo_consumo_ia} | Ganancias: {self.ganancias_acumuladas}"
    
class Tendencia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    termino_busqueda = models.CharField(max_length=200, help_text="Ej: Zapatillas running")
    fuente = models.CharField(max_length=50, help_text="Ej: Google Trends, TikTok")
    puntuacion_viral = models.IntegerField(default=0, help_text="Score de 1 a 100")
    fecha_deteccion = models.DateTimeField(auto_now_add=True)
    procesado = models.BooleanField(default=False, help_text="¿Ya se generó contenido de esto?")

    class Meta:
        verbose_name = "Tendencia"
        verbose_name_plural = "Tendencias"
        # Prevenir que la misma tendencia se registre dos veces desde la misma fuente
        unique_together = ('termino_busqueda', 'fuente')

    def __str__(self):
        estado = "Procesado" if self.procesado else "Pendiente"
        return f"[{self.fuente}] {self.termino_busqueda} ({estado})"
    

class Articulo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portal = models.ForeignKey(Portal, on_delete=models.CASCADE, related_name='articulos')
    tendencia = models.ForeignKey('Tendencia', on_delete=models.SET_NULL, null=True, blank=True)
    
    titulo = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    contenido_html = models.TextField()
    idioma = models.CharField(max_length=50, default="Español")
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    vistas = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
            # Para evitar slugs duplicados
            original_slug = self.slug
            contador = 1
            while Articulo.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{contador}'
                contador += 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"

    def __str__(self):
        return f"{self.titulo} ({self.idioma})"
