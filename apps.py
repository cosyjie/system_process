from django.apps import AppConfig


class SystemProcessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.system_process'
    dependent_modules = ['module_system']
    version = '0.0.1-Alpha'
    description = '查阅并管理操作系统当前进程'
