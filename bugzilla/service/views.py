# Create your views here.
from bugzilla import settings
import xmlrpclib
from django.http import HttpResponse, HttpResponseServerError
import json
import datetime

class BugzillaConnector(object):
    def __init__(self,bugzilla_xmlrpc):
        self._xmlrpc = xmlrpclib.ServerProxy(bugzilla_xmlrpc)
    
    def _dispatcher(self,request,namespace,function, **kwargs):
        dthandler = lambda xbj: '%s'%xbj if isinstance(xbj,xmlrpclib.DateTime) else None  
        klass = namespace.capitalize()
        print '_dispatcher: namespace=%s, function=%s' % (klass,function)
        if request.GET:
            params = dict()
            for key in request.GET.keys():
                print '%s = %s' % (key,request.GET[key])
                params[key] = request.GET[key]
            result = getattr(self._xmlrpc,klass+'.'+function)(params)
        else:
            result = getattr(self._xmlrpc,klass+'.'+function)()
        print result
        return HttpResponse(json.dumps(result,default=dthandler))
    
