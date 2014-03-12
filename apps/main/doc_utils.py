from __future__ import unicode_literals
from rest_framework.compat import six
from rest_framework.views import APIView
from rest_framework.serializers import Serializer
import types
    
def api_doc_view(http_method_names):

    """
    Decorator that converts a function-based view into an APIView subclass.
    Takes a list of allowed methods for the view as an argument.
    """

    def decorator(func):

        WrappedAPIView = type(
            six.PY3 and 'WrappedAPIView' or b'WrappedAPIView',
            (APIView,),
            {'__doc__': func.__doc__}
        )

        # Note, the above allows us to set the docstring.
        # It is the equivalent of:
        #
        #     class WrappedAPIView(APIView):
        #         pass
        #     WrappedAPIView.__doc__ = func.doc    <--- Not possible to do this

        # api_doc_view applied without (method_names)
        assert not(isinstance(http_method_names, types.FunctionType)), \
            '@api_doc_view missing list of allowed HTTP methods'

        # api_doc_view applied with eg. string instead of list of strings
        assert isinstance(http_method_names, (list, tuple)), \
            '@api_doc_view expected a list of strings, received %s' % type(http_method_names).__name__

        allowed_methods = set(http_method_names) | set(('options',))
        WrappedAPIView.http_method_names = [method.lower() for method in allowed_methods]

        def handler(self, *args, **kwargs):
            return func(*args, **kwargs)

        for method in http_method_names:
            setattr(WrappedAPIView, method.lower(), handler)
        
        class Body(Serializer):
            
            def __init__(self, **kwargs):
                super(Body, self).__init__(**kwargs) 
        
        def get_serializer_class(self):
            return Body
        
        setattr(WrappedAPIView, 'get_serializer_class', get_serializer_class)
        
        WrappedAPIView.__name__ = func.__name__

        WrappedAPIView.renderer_classes = getattr(func, 'renderer_classes',
                                                  APIView.renderer_classes)

        WrappedAPIView.parser_classes = getattr(func, 'parser_classes',
                                                APIView.parser_classes)

        WrappedAPIView.authentication_classes = getattr(func, 'authentication_classes',
                                                        APIView.authentication_classes)

        WrappedAPIView.throttle_classes = getattr(func, 'throttle_classes',
                                                  APIView.throttle_classes)

        WrappedAPIView.permission_classes = getattr(func, 'permission_classes',
                                                    APIView.permission_classes)
        
        return WrappedAPIView.as_view()
    return decorator