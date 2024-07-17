import subprocess
import psutil
import datetime

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect


from appcommon.helper import subprocess_run, remove_list_blank
from panel.module_system.views import ModuleSystemMixin


class ProcessAdminMixin(ModuleSystemMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = 'system_process'
        return context


class ProcessListView(ProcessAdminMixin, TemplateView):
    template_name = 'system_process/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '进程管理'
        if 'list_type' in self.kwargs:
            context['list_type'] = self.kwargs.get('list_type')
        else:
            context['list_type'] = 'all'

        if context['list_type'] == 'all':
            context['process'] = psutil.process_iter(
                attrs=['pid', 'name', 'username', 'status', 'cmdline', 'memory_info', 'cpu_percent']
            )
        if context['list_type'] == 'memo':
            process = psutil.process_iter(attrs=['pid', 'name', 'username', 'status', 'cmdline', 'memory_info', 'memory_percent'])
            context['process'] = sorted(process, key=lambda process:process.info['memory_info'], reverse=True)[:100]
        if context['list_type'] == 'log':
            context['process'] = []
            for p in psutil.process_iter(['pid', 'name', 'username', 'status', 'open_files', 'cmdline']):
                for file in p.info['open_files'] or []:
                    if file.path.endswith('.log'):
                        context['process'].append(
                            {
                                'pid': p.pid, 'name': p.info['name'],'username': p.info['username'],
                                'status': p.info['status'], 'logfiles': file.path
                            }
                        )
        if context['list_type'] == 'cpu':
            process = psutil.process_iter(attrs=['pid', 'name', 'username', 'status', 'cmdline', 'cpu_percent'])
            context['process'] = sorted(process, key=lambda process:process.info['cpu_percent'], reverse=True)[:100]

        return context


class DetailView(ProcessAdminMixin, TemplateView):
    template_name = 'system_process/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = '进程信息'
        context['list_type'] = self.kwargs.get('list_type')
        context['breadcrumb'] = [{
            'title': '进程',
            'href': reverse_lazy('module_system:system_process:list', kwargs={'list_type': self.kwargs.get('list_type')}),
            'active': False},
            {'title': '进程详情', 'href': '', 'active': True},
        ]
        context['process'] = {}
        if psutil.pid_exists(self.kwargs.get('pid')):
            for p in psutil.process_iter():
                if p.pid == self.kwargs.get('pid'):
                    context['process']['pid'] = p.pid
                    context['process']['name'] = p.name
                    context['process']['cmdline'] = p.cmdline()
                    context['process']['username'] = p.username()
                    context['process']['cpu_percent'] = p.cpu_percent()
                    context['process']['username'] = p.username()
                    context['process']['status'] = p.status()
                    context['process']['parent'] = p.parent()
                    context['process']['tty'] = p.terminal()
                    context['process']['memory'] = p.memory_info()
                    context['process']['create_time'] = datetime.datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")
                    context['process']['files'] = []
                    for file in p.open_files():
                        context['process']['files'].append(file.path)

        return context


class ActionView(ProcessListView, RedirectView):

    def get(self, request, *args, **kwargs):
        list_type = self.kwargs.get('list_type')
        pid = self.kwargs.get('pid')
        action = self.kwargs.get('action')
        if psutil.pid_exists(pid):
            if action == 'kill':
                psutil.Process(pid=pid).kill()
                messages.success(self.request, ' 标识为：' + str(pid) + ' 的进程已关闭！')
                self.url = reverse('module_system:system_process:list', kwargs={'list_type': list_type})
            if action == 'pause':
                print('pause')
                psutil.Process(pid=pid).suspend()
                messages.success(self.request, ' 标识为：' + str(pid) + ' 的进程已执行暂停！')
                self.url = reverse('module_system:system_process:detail', kwargs={'list_type': list_type, 'pid': pid})
            if action == 'resume':
                psutil.Process(pid=pid).resume()
                messages.success(self.request, ' 标识为：' + str(pid) + ' 的进程已执行恢复！')
                self.url = reverse('module_system:system_process:detail', kwargs={'list_type': list_type, 'pid': pid})
        else:
            messages.warning(self.request, ' 标识为：' + str(pid) + ' 的进程未运行或者标识ID已经变化！不能执行！')
            self.url = reverse('module_system:system_process:list', kwargs={'list_type': list_type})

        return super().get(request, *args, **kwargs)


