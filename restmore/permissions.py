#CONSIDER: composable authorizations
class Authorization(object):
    '''
    Base authorization class, defaults to full authorization
    '''
    #CONSIDER: how is this notified about filtering, ids, etc
    def __init__(self, identity, endpoint):
        self.identity = identity
        self.endpoint = endpoint

    def process_queryset(self, queryset):
        return queryset

    def is_authorized(self):
        return True


class AuthorizationMixin(object):
    def make_authorization(self, identity, endpoint):
        return Authorization(identity, endpoint)

    def get_identity(self):
        #TODO delegate
        return self.request.user

    def is_authenticated(self):
        return self.authorization.is_authorized()

    def handle(self, endpoint, *args, **kwargs):
        self.identity = self.get_identity()
        self.authorization = self.make_authorization(self.identity, endpoint)
        return super(AuthorizationMixin, self).handle(endpoint, *args, **kwargs)


class DjangoModelAuthorization(Authorization):
    '''
    Your basic django core permission based authorization
    '''
    def __init__(self, identity, model, endpoint):
        super(DjangoModelAuthorization, self).__init__(identity, endpoint)
        self.model = model

    def is_authorized(self):
        #print("auth identity:", self.identity)
        if self.identity.is_superuser:
            return True
        #TODO proper lookup of label?
        if self.endpoint == 'list':
            return True
            #TODO in django fashion, you have list if you have add, change, or delete
            return self.identity.has_perm
        perm_name = self.model._meta.app_label + '.'
        if self.endpoint == 'create':
            perm_name += 'add'
        elif self.endpoint == 'update':
            perm_name += 'change'
        else:
            #TODO delete_list? update_list? others?
            perm_name += self.endpoint

        perm_name += '_' + self.model.__name__
        return self.identity.has_perm(perm_name)


class ModelAuthorizationMixin(AuthorizationMixin):
    def make_authorization(self, identity, endpoint):
        return DjangoModelAuthorization(identity, self.model, endpoint)
