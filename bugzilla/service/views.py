# Create your views here.
from bugzilla import settings
import xmlrpclib
from django.http import HttpResponse, HttpResponseServerError
import json
import datetime
import os
import sys
import socket
import re
import httplib
import errno

def create_user_agent():
    ma, mi, rel = sys.version_info[:3]
    return "xmlrpclib - Python-%s.%s.%s"%(ma, mi, rel)

class CookieAuthXMLRPCTransport(xmlrpclib.Transport):
    """
    xmlrpclib.Transport that caches authentication cookies in a
    local cookie jar and reuses them.

    Based off `this recipe
    <http://code.activestate.com/recipes/501148-xmlrpc-serverclient-which-does-cookie-handling-and/>`_

    """

    def __init__(self, use_datetime=0):
        self._use_datetime = use_datetime
        self._connection = (None, None)
        self._extra_headers = []
        self.cookiefile = "cookies.txt"
    ##
    # Send a complete request, and parse the response.
    # Retry request if a cached connection has disconnected.
    #
    # @param host Target host.
    # @param handler Target PRC handler.
    # @param request_body XML-RPC request body.
    # @param verbose Debugging flag.
    # @return Parsed response.

    def request(self, host, handler, request_body, verbose=0):
        #retry request once if cached connection has gone cold
        for i in (0, 1):
            try:
                return self.single_request(host, handler, request_body, verbose)
            except socket.error, e:
                if i or e.errno not in (errno.ECONNRESET, errno.ECONNABORTED, errno.EPIPE):
                    raise
            except httplib.BadStatusLine: #close after we sent request
                if i:
                    raise
    def setcookie(self,cookies):
        #print 'Cookies: %s' % cookies
        bugz_cookies = re.findall(r'Bugzilla[0-9a-zA-Z_]*\=[0-9a-zA-Z_]*',cookies)
        f = open(self.cookiefile,'w')
        for line in bugz_cookies:
            #print 'write line: %s' % line
            f.write('%s\n'%line)
            #f.writelines(line)
        f.close()
    
    def getcookie(self):
        if os.path.exists(self.cookiefile):
            f = open(self.cookiefile,'r')
            cookies = f.readlines()
            cookies = map(lambda s: s.strip(), cookies)
            f.close()
        else:
            cookies = None
        return cookies;
        
    ##
    # Send a complete request, and parse the response.
    #
    # @param host Target host.
    # @param handler Target PRC handler.
    # @param request_body XML-RPC request body.
    # @param verbose Debugging flag.
    # @return Parsed response.

    def single_request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request

        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        try:
            self.send_request(h, handler, request_body)
            self.send_host(h, host)
            cks = self.getcookie()
            if cks:
                h.putheader("Cookie", ";".join(cks))
            self.send_user_agent(h)
            self.send_content(h, request_body)

            response = h.getresponse(buffering=True)
            setck = response.getheader("set-cookie",None)
            if setck:
                self.setcookie(setck)
            if response.status == 200:
                self.verbose = verbose
                return self.parse_response(response)
        except xmlrpclib.Fault:
            raise
        except Exception:
            # All unexpected errors leave connection in
            # a strange state, so we clear it.
            self.close()
            raise
        
        #discard any response data and raise exception
        if (response.getheader("content-length", 0)):
            response.read()
        raise ProtocolError(
            host + handler,
            response.status, response.reason,
            response.msg,
            )



class BugzillaConnector(object):
    def __init__(self,bugzilla_xmlrpc):
        self._xmlrpc = xmlrpclib.ServerProxy(bugzilla_xmlrpc,CookieAuthXMLRPCTransport())
    
    def _dispatcher(self,request,namespace,function, **kwargs):
        dthandler = lambda xbj: '%s'%xbj if isinstance(xbj,xmlrpclib.DateTime) else None  
        klass = namespace.capitalize()
        print '_dispatcher: namespace=%s, function=%s' % (klass,function)
        if request.GET:
            params = dict()
            for key in request.GET.keys():
                print '%s = %s' % (key,request.GET[key])
                if key.endswith('ids') or key.endswith('names'):
                    params[key] = request.GET[key].split(',')
                else:
                    params[key] = request.GET[key]
            
        else:
            params = None
            
        try:
            if params:
                result = getattr(self._xmlrpc,klass+'.'+function)(params)
            else:
                result = getattr(self._xmlrpc,klass+'.'+function)()
        except xmlrpclib.Fault, f:
            return HttpResponse(json.dumps({'fault':'%s'%f}))
        except Exception, e:
            return HttpResponse(json.dumps({'fault':'%s'%e}))
        return HttpResponse(json.dumps(result,default=dthandler))
    
