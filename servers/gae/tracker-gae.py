import os
import re
import json
import webapp2
import jinja2
from google.appengine.ext import db
from google.appengine.api import memcache

jinjaEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
			      extensions=['jinja2.ext.autoescape'],
			      autoescape=True)

class GpsData():
  regexp = re.compile("(.*)-(.*)-(.*)-(.*)")
  
  @staticmethod
  def encode(tm, lt, ln, sp):
    s = str(tm) + "-" + str(lt) + "-" + str(ln) + "-" + str(sp)
    return str(s)
    
  @staticmethod
  def decode(packedData):
    return GpsData.regexp.match(packedData)
   
  def __init__(self):
    self.time = None
    self.lattitude = None
    self.longtitude = None
    self.speed = None
      
  def setPackedData(self, packedData):
    rd = GpsData.decode(str(packedData))
    if rd:
      self.time = str(rd.group(1))
      self.lattitude = float(rd.group(2))
      self.longtitude = float(rd.group(3))
      self.speed = float(rd.group(4))
  
  def isValid(self):
    return time is not None
  
  def encoded(self):
    return GpsData.encode(self.time, self.lattitude, self.longtitude, self.speed)
  
class PackedData(db.Model):
  packedData = db.StringProperty(indexed=False,required=True)
  
  @staticmethod
  def cacheLife():
    return 86400 * 7 # week
 
  @staticmethod
  def getCached(datakey):
    data = memcache.get(datakey)
    if data is not None:
      return data
    else:
      data = PackedData.get_by_key_name(datakey)
      memcache.add(datakey, data, PackedData.cacheLife())
      return data
  
  @staticmethod
  def putCached(datakey, data):
    if type(datakey) is str and type(data) is str:
      d = PackedData(key_name=datakey, packedData=data)
      d.put()
      memcache.add(datakey, data, PackedData.cacheLife())
  
  @staticmethod
  def clear():
    q = db.Query(PackedData, keys_only=True)
    db.delete(q)
    memcache.flush_all()

class GpReset(webapp2.RequestHandler):
  def get(self):
    PackedData.clear()
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('ALL DATA CLEARED!')   

class GpsRecord(webapp2.RequestHandler): 
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write('This is a test page! :)')
    
  def post(self):    
    recvData = self.request.get('gpcoord-data')
    if recvData is not None:
      recvData = json.loads(recvData)
      
      for d in recvData:
	k = d.get('time')
	pd = GpsData.encode(str(k), d.get('lat'), d.get('lon'), d.get('speed'))
	PackedData.putCached(str(k), pd)
           
class GpCurrent(webapp2.RequestHandler):
  def get(self):
    zoom = 12
    if type(self.request.get('zoom')) is int:
      zoom = self.request.get('zoom')
    
    q = db.Query(PackedData)
    q.order('__key__')
    d = q.get()
        
    gpsd = GpsData()
    gpsd.setPackedData(d.packedData)
    
    template_args = {'_gptime_' : gpsd.time, '_gplat_' : str(gpsd.lattitude), '_gplon_' : str(gpsd.longtitude), '_gpzoom_' : zoom}    
   
    template = jinjaEnv.get_template('html/current.html')
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(template.render(template_args))

class GpPath(webapp2.RequestHandler):
  def get(self):
    zoom = 12
    z = self.request.get('zoom')
    if  type(z) is int:
      zoom = int(z)
    
    q = db.Query(PackedData, keys_only=True)
    q.order('__key__')
    
    #Create path array
    coords = '[ '
    for k in q:
      d = PackedData.getCached(str(k.name()))
      gpsd = GpsData()
      gpsd.setPackedData(d)
      coords = coords + str('new google.maps.LatLng(%f, %f),' % (gpsd.lattitude, gpsd.longtitude))
    #remove last comma
    coords = coords[:-1]
    #close array
    coords = coords + ' ]'

    template_args = {'_gppath_' : coords, '_gpzoom_' : str(zoom)}    

    
    template = jinjaEnv.get_template('html/path.html')
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(template.render(template_args))
    
class GpSpeedStats(webapp2.RequestHandler):
  def get(self):  
    
    try:
      emptylabels = int(self.request.get('nolabels'))
    except ValueError:
      emptylabels = 0
    
    try:
      fetch = int(self.request.get('items')) 
    except ValueError:
      fetch = 10
    
    q = db.Query(PackedData, keys_only=True)
    q.order('__key__')
    
    path = q.fetch(fetch)
    
    #create array
    labels = '[ '
    data = '[ '
    for k in path:
      d = PackedData.getCached(k.name())
      gpsd = GpsData()
      gpsd.setPackedData(d)
      data = data + str('%f,' % gpsd.speed) 
      if emptylabels != 0:
	labels = labels + str('\'%s\',' % " ")
      else:
	labels = labels + str('\'%s\',' % gpsd.time)
    #remove last comma
    data = data[:-1]
    labels = labels[:-1]
    #close array
    data = data + ' ]'
    labels = labels + ' ]'
       
    template_args = {"_gplabels_" : str(labels), "_gpdata_" : data, "_title_" : "SPEED STATS \_----->>>"}
    template = jinjaEnv.get_template('html/speedstats.html')
    self.response.headers['Content-Type'] = 'text/html'
    self.response.write(template.render(template_args))
    
app = webapp2.WSGIApplication([('/record', GpsRecord),
			       ('/current', GpCurrent),
			       ('/reset', GpReset),
			       ('/path', GpPath),
			       ('/speedstats', GpSpeedStats)], debug=True)
