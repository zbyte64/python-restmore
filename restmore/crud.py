from django.db import transaction
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms.models import modelform_factory

from restless.dj import DjangoResource

from .forms import DjangoFormMixin
from .permissions import ModelAuthorizationMixin
from .normalizer import NormalizedResourceMixin


class DjangoModelResource(ModelAuthorizationMixin, DjangoFormMixin, NormalizedResourceMixin, DjangoResource):
    '''
    A restless DjangoResource with ponies
    '''
    model = None
    paginate_by = 50
    #TODO filter_by
    #TODO fields, exclude_fields

    def get_queryset(self):
        queryset = self.model.objects.all()
        return self.authorization.process_queryset(queryset)

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        #TODO authorization may want to modify our form
        return modelform_factory(model=self.model)

    def url_for(self, obj):
        #TODO i'm sure we can come up with a smarter default
        return obj.get_absolute_url()

    def get_paginator(self):
        queryset = self.get_queryset()
        return Paginator(queryset, self.request.GET.get('paginate_by', self.paginate_by))

    def get_page(self):
        paginator = self.paginator()
        return paginator.page(self.request.GET.get('page'))

    def wrap_list_response(self, page):
        #TODO runthrough HATEOAS layer, just kidding... ?
        return {
            objects: page.object_list,
            page: page.number,
            pages: page.paginator.num_pages,
            count: page.paginator.count,
        }

    def list(self):
        try:
            return self.get_page()
        except PageNotInteger as exception:
            #TODO proper status code?
            return self.build_status_response({'message': str(exception)}, status=400)
        except EmptyPage as exception:
            #TODO proper status code?
            return self.build_status_response({'message': str(exception)}, status=410)

    def detail(self, pk):
        try:
            return self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist as exception:
            return self.build_status_response({'message': str(exception)}, status=404)

    @transaction.atomic
    def create(self):
        form = self.make_form()
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect(self.url_for(obj), status=303)
        else:
            return self.build_validation_error(form.errors)

    @transaction.atomic
    def update(self, pk):
        try:
            obj = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            obj = self.model()
        form = self.make_form(obj=obj)
        if form.is_valid():
            obj = form.save()
            return HttpResponseRedirect(self.url_for(obj), status=303)
        else:
            return self.build_validation_error(form.errors)

    @transaction.atomic
    def delete(self, pk):
        self.get_queryset().get(pk=pk).delete()
        return self.build_status_response(None, status=204)#or 410?

    @transaction.atomic
    def delete_list(self):
        pks = self.request.GET.getlist('pk')
        self.get_queryset().filter(pk__in=pks).delete()
        return HttpResponseRedirect('./', status=303)

    #TODO
    '''
    @transaction.atomic
    def update_list(self):
        pass
    '''
