from googleanalytics.exception import *
from googleanalytics import config
import pprint
import re
import socket
import urllib
import urllib2

DEBUG = False
socket_timeout = 10
socket.setdefaulttimeout(socket_timeout)

class GAConnection():
  default_host = 'https://www.google.com'
  user_agent = 'python-gapi-1.0'
  auth_token = None

  def __init__(self, google_email=None, google_password=None):  
    authtoken_pat = re.compile(r"Auth=(.*)")
    path = '/accounts/ClientLogin'
    
    if google_email == None or google_password == None:
      google_email, google_password = config.get_google_credentials()
      
    data = "accountType=GOOGLE&Email=%s&Passwd=%s&service=analytics&source=%s"
    data = data % (google_email, google_password, self.user_agent)
    if DEBUG:
      print "Authenticating with %s / %s" % (google_email, google_password)
    response = self.make_request('POST', path=path, data=data)
    auth_token = authtoken_pat.search(response.read())
    self.auth_token = auth_token.groups(0)[0]
    
  def get_accounts(self, start_index=1, max_results=10):
    path = '/analytics/feeds/accounts/default'
    data = { 'start-index': start_index,}
    if max_results:
      data['max-results'] = max_results
    data = urllib.urlencode(data)
    response = self.make_request('GET', path, data=data)
    raw_xml = response.read()
    parsed_body = self.parse_response_etree(raw_xml)
    pprint.pprint(parsed_body)
  
  def parse_response_etree(self, xml):
    from xml.etree import ElementTree
    tree = ElementTree.fromstring(xml)
    entries = tree.getiterator('entry')
    
    
  def make_request(self, method, path, headers=None, data=''):
    if headers == None:
      headers = {
        'User-Agent': self.user_agent,
        'Authorization': 'GoogleLogin auth=%s' % self.auth_token 
      }
    else:
      headers = headers.copy()
     
    if DEBUG:
      print "** Headers: %s" % (headers,)
         
    if method == 'GET':
      path = '%s?%s' % (path, data)

    if DEBUG:
      print "** Method: %s" % (method,)
      print "** Path: %s" % (path,)
      print "** Data: %s" % (data,)
      print "** URL: %s" % (self.default_host+path)
    
    if method == 'POST':
      request = urllib2.Request(self.default_host + path, data, headers)
    elif method == 'GET':
      request = urllib2.Request(self.default_host + path, headers=headers)

    try:
      response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
      raise GoogleAnalyticsClientError(e)
    return response