from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelform_factory

from functools import lru_cache

from restless.dj import DjangoResource

from .forms import DjangoFormMixin
from .permissions import ModelAuthorizationMixin
from .presentors import PresentorResourceMixin


class DjangoModelResource(ModelAuthorizationMixin, DjangoFormMixin, PresentorResourceMixin, DjangoResource):
    '''
    A restless DjangoResource with ponies
    '''
    model = None
    paginate_by = 50
    #TODO filter_by
    #these modify autoform
    fields = None
    exclude_fields = None
    #TODO fields, exclude_fields to shape preparer

    def get_queryset(self):
        queryset = self.model.objects.all()
        return self.authorization.process_queryset(queryset)

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        #TODO authorization may want to modify our form
        return modelform_factory(model=self.model, fields=self.fields, exclude=self.exclude_fields)

    def url_for(self, obj):
        #TODO i'm sure we can come up with a smarter default
        return obj.get_absolute_url()

    #@lru_cache
    def get_paginator(self):
        queryset = self.get_queryset()
        return Paginator(queryset, self.request.GET.get('paginate_by', self.paginate_by))

    def get_page(self):
        paginator = self.get_paginator()
        return paginator.page(self.request.GET.get('page', 1))

    def list(self):
        try:
            return self.get_page()
        except PageNotAnInteger as exception:
            #TODO proper status code?
            return self.build_status_response(str(exception), status=400)
        except EmptyPage as exception:
            #TODO proper status code?
            return self.build_status_response(str(exception), status=410)

    def detail(self, pk):
        try:
            return self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist as exception:
            return self.build_status_response(str(exception), status=404)

    @transaction.atomic
    def create(self):
        form = self.make_form()
        if form.is_valid():
            obj = form.save()
            return obj
            #return HttpResponseRedirect(self.url_for(obj), status=303)
        else:
            return self.build_validation_error(form.errors)

    @transaction.atomic
    def update(self, pk):
        try:
            obj = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            obj = self.model()
        form = self.make_form(instance=obj)
        if form.is_valid():
            obj = form.save()
            return obj
            #return HttpResponseRedirect(self.url_for(obj), status=303)
        else:
            return self.build_validation_error(form.errors)

    @transaction.atomic
    def delete(self, pk):
        self.get_queryset().get(pk=pk).delete()
        return None
        #return self.build_status_response(None, status=204)#or 410?

    @transaction.atomic
    def delete_list(self):
        pks = self.request.GET.getlist('pk')
        return self.get_queryset().filter(pk__in=pks).delete()
        #return HttpResponseRedirect('./', status=303)

    #TODO
    '''
    @transaction.atomic
    def update_list(self):
        pass
    '''
