from django.contrib import admin

from .models import AthleteProfile


admin.site.site_header = 'Punto de Juego | Administración'
admin.site.site_title = 'Punto de Juego'
admin.site.index_title = 'Gestión de la academia deportiva'


@admin.register(AthleteProfile)
class AthleteProfileAdmin(admin.ModelAdmin):
    list_display = (
        'membership_code',
        'full_name',
        'sport',
        'skill_level',
        'email',
        'is_active',
        'created_at',
        'display_name',
    )
    list_filter = ('sport', 'skill_level', 'is_active', 'created_at')
    search_fields = (
        'membership_code',
        'full_name',
        'email',
        'user__username',
    )
    readonly_fields = ('created_at', 'updated_at', 'display_name')
    list_select_related = ('user',)
    fields = (
        'user',
        'full_name',
        'membership_code',
        'email',
        'phone',
        'sport',
        'skill_level',
        'birth_date',
        'is_active',
        'created_at',
        'updated_at',
    )
    actions = ('activate_athletes', 'deactivate_athletes')

    @admin.display(description='Nombre normalizado')
    def display_name(self, obj):
        return obj.display_name

    @admin.action(description='Activar membresías seleccionadas')
    def activate_athletes(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} membresía(s) activada(s).')

    @admin.action(description='Pausar membresías seleccionadas')
    def deactivate_athletes(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} membresía(s) desactivada(s).')
