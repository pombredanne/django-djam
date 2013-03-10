from __future__ import unicode_literals

from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import capfirst

from djam.riffs.base import Riff
from djam.views.models import ModelListView, ModelCreateView, ModelUpdateView, ModelDeleteView


class ModelRiff(Riff):
    model = None
    list_view = ModelListView
    create_view = ModelCreateView
    update_view = ModelUpdateView
    delete_view = ModelDeleteView

    # create and update kwargs can contain:
    # - form_class
    # - fieldsets
    # - readonly
    update_kwargs = {}
    create_kwargs = {}

    def __init__(self, *args, **kwargs):
        if not self.model:
            raise ImproperlyConfigured('Please specify a model')
        if self.display_name is None:
            self.display_name = capfirst(self.model._meta.verbose_name_plural)
        if self.slug is None:
            self.slug = self.model._meta.module_name
        if self.namespace is None:
            self.namespace = '{appname}_{modelname}'.format(
                appname=self.model._meta.app_label,
                modelname=self.model._meta.module_name)
        super(ModelRiff, self).__init__(*args, **kwargs)

    def get_extra_urls(self):
        return patterns('',
            url(r'^$',
                self.wrap_view(self.list_view.as_view(**self.get_list_kwargs())),
                name='list'),
            url(r'^add/$',
                self.wrap_view(self.create_view.as_view(**self.get_create_kwargs())),
                name='create'),
            url(r'^(?P<pk>\w+)/$',
                self.wrap_view(self.update_view.as_view(**self.get_update_kwargs())),
                name='update'),
            url(r'^(?P<pk>\w+)/delete/$',
                self.wrap_view(self.delete_view.as_view(**self.get_view_kwargs())),
                name='delete'),
        )

    def get_default_url(self):
        return self.reverse('list'.format(appname=self.model._meta.app_label, modelname=self.slug))

    def get_view_kwargs(self):
        kwargs = super(ModelRiff, self).get_view_kwargs()
        kwargs['model'] = self.model
        return kwargs

    def get_list_kwargs(self):
        kwargs = self.get_view_kwargs()
        return kwargs

    def get_update_kwargs(self):
        kwargs = self.get_view_kwargs()
        kwargs.update(self.update_kwargs)
        return kwargs

    def get_create_kwargs(self):
        kwargs = self.get_view_kwargs()
        kwargs.update(self.create_kwargs)
        return kwargs
