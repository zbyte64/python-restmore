Restmore
========

Not yet ready, I have a few late nights ahead of me.

The missing django batteries for restless to help you get more sleep.

Usage
=====

Define a resource::

    from restmore.crud import DjangoModelResource

    class MyResource(DjangoModelResource):
        model = MyModel

Include in urls::

    urlpatterns = patterns('',
        # The usual fare, then...

        # Add this!
        url(r'api/posts/', include(MyResource.urls())),
    )

Get some sleep.
