from django.contrib import admin

from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'full_name',
        'email',
        'career',
        'is_active_record',
        'created_at',
        'display_name',
    )
    list_filter = ('career', 'is_active_record', 'created_at')
    search_fields = ('code', 'full_name', 'email', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'display_name')
    list_select_related = ('user',)
    fields = (
        'user',
        'full_name',
        'code',
        'email',
        'phone',
        'career',
        'is_active_record',
        'created_at',
        'updated_at',
    )
    actions = ('activate_profiles', 'deactivate_profiles')

    @admin.display(description='Nombre normalizado')
    def display_name(self, obj):
        return obj.display_name

    @admin.action(description='Activar registros seleccionados')
    def activate_profiles(self, request, queryset):
        updated = queryset.update(is_active_record=True)
        self.message_user(request, f'{updated} registro(s) activado(s).')

    @admin.action(description='Desactivar registros seleccionados')
    def deactivate_profiles(self, request, queryset):
        updated = queryset.update(is_active_record=False)
        self.message_user(request, f'{updated} registro(s) desactivado(s).')
