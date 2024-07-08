from django.urls import reverse

menu = {
    'module_system': {
        'child': [
            {
                'name': 'system_process',
                'title': '进程管理',
                'href': reverse('module_system:system_process:list', kwargs={'list_type': 'all'}),
            },
        ]
    }
}
