from django.http.multipartparser import MultiPartParser, MultiPartParserError
from django.template.loader import render_to_string
from io import BytesIO
import json

#CONSIDER MultiValueDict vs reqular Dict

class MultipartFormSerializer(object):
    def deserialize(self, data):
        #TODO restless should pass in headers?
        parser = MultiPartParser(self.request.META, BytesIO(data), [], encoding=self.request.encoding)
        #TODO merge in files?
        post, files = parser.parse()
        return post

#TODO
class UrlSerializer(object):
    def deserialize(self, data):
        return self.request.GET

    def serialize(self, data):
        pass


class HTMLSerializer(object):
    def serialize(self, data):
        return render_to_string('restmore/response.html', {'data': data, 'jsondata': json.dumps(data)})
