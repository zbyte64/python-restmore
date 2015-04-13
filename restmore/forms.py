from django.utils.datastructures import MultiValueDict

class DjangoFormMixin(object):
    '''
    Django form helper
    '''
    form_class = None

    def get_form_class(self):
        return self.form_class

    def make_form(self, **kwargs):
        #TODO is this correct?
        if 'data' not in kwargs:
            #MultiValeuDict to please django forms
            data = MultiValueDict()
            data.update(self.data)
            kwargs['data'] = data
        if 'files' not in kwargs:
            kwargs['files'] = self.request.FILES
        return self.get_form_class()(**kwargs)

    def wrap_validation_error_response(self, validation_errors):
        return validation_errors

    def build_validation_error(self, validation_errors):
        '''
        Build a response from form validation errors
        '''
        data = self.wrap_validation_error_response(validation_errors)
        payload = self.prepare(data)
        #412 validation = client precondition; 400 = bad request
        return self.build_response(data, status=400)
