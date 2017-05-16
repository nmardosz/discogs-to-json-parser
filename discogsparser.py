import sys
import xml.sax.handler
import xml.sax
import codecs
import re
import time
import json

reload(sys)  
sys.setdefaultencoding('utf8')

releaseCounter = 0
		
class ReleaseHandler( xml.sax.handler.ContentHandler ):
	def __init__(self):
		self.CurrentData = ""
		self.artists = []
		self.artist = ""
		self.title = ""
		self.format = ""
		self.formats = []
		self.formatdescriptions = []
		self.genres = []
		self.styles = []
		self.country = ""
		self.released = ""
		self.tracklist = []
		self.track = ""
		self.tagstack = []
		self.childlist = []
		self.buffer = ''
		self.concisetrack = []
		self.trackstring = ''
		self.variousartist = 0
		self.various = []
		self.varioustracktitle = ''
		self.thisisnotatrack = 0
		
	def startElement(self, tag, attributes):
		self.tagstack.append(tag)
		self.CurrentData = tag
		
		if tag == 'release':
			releaseid = attributes["id"]
			fo.write('{ "releaseid": ' + json.dumps(releaseid) + ', ')
			
		if tag == 'genres':
			fo.write('"genres": [')
			
		if tag == 'styles':
			fo.write('"styles": [')
			
		if tag == 'tracklist':
			fo.write('"tracklist": [')
			
		if tag == 'format':
			formatname = attributes["name"]
			self.formats.append(json.dumps(formatname))
			#fo.write('"format_type": ' + json.dumps(formatname) + ', ')
			
		#if tag == 'descriptions':
			#fo.write('"format_descriptions": [')
			

			
			
	def characters(self, content):
		self.buffer += content
			
			
	def endElement(self, tag):
		#print(tag)
		self.buffer = self.buffer.strip()
		# Release Title
		if tag == 'title' and self.tagstack[-2] == 'release':
			if len(self.buffer) != 0:
				fixtitle = re.sub(' | ',' ', self.buffer)
				fixtitle = re.sub('\s+',' ', fixtitle)
				#fixtitle = fixtitle.replace('"', '\"')
				#fixtitle = fixtitle.replace('\\', '\\\\')
				fo.write('"l_title": ' + json.dumps(fixtitle.lower().rstrip()) + ', ')
				fo.write('"title": ' + json.dumps(fixtitle.rstrip()) + ', ')
		# Track Position Add to Array
		elif tag == 'position' and 'sub_track' not in self.tagstack:
			if len(self.buffer) != 0:
				self.thisisnotatrack = 0
				self.concisetrack.append('"track_position": ' + json.dumps(self.buffer))
				#fo.write("track_position " + self.buffer + " ")
			if len(self.buffer) == 0:
				self.thisisnotatrack = 1
		# Track Title Add to Array
		if tag == 'title' and self.tagstack[-2] == 'track' and 'sub_track' not in self.tagstack and self.thisisnotatrack == 0:
			if self.variousartist == 0:
				if len(self.buffer) != 0:
					fixtracktitle = self.buffer
					#fixtracktitle = fixtracktitle.replace('"', '\"')
					#fixtracktitle = fixtracktitle.replace('\\', '\\\\')
					self.concisetrack.append('"track_title": ' + json.dumps(fixtracktitle))
					#fo.write("track_title: " + self.buffer + " ")
			if self.variousartist == 1:
				if len(self.buffer) != 0:
					fixtracktitle = self.buffer
					#fixtracktitle = fixtracktitle.replace('"', '\"')
					#fixtracktitle = fixtracktitle.replace('\\', '\\\\')
					self.varioustracktitle = fixtracktitle
					#fo.write("track_title: " + self.buffer + " ")
		# Various Artist Array
		if tag == 'name' and self.tagstack[-2] == 'artist' and self.tagstack[-3] == 'artists' and self.tagstack[-4] == 'track' and 'sub_track' not in self.tagstack and self.thisisnotatrack == 0:
			if self.variousartist == 1:
					if len(self.buffer) != 0:
						variousartistfix = re.sub('\(.*?\)','', self.buffer)
						variousartistfix = re.sub(' | ',' ', variousartistfix)
						variousartistfix = re.sub('\*','', variousartistfix)
						variousartistfix = re.sub('\s+',' ', variousartistfix)
						#fixtracktitle = fixtracktitle.replace('"', '\"')
						#fixtracktitle = fixtracktitle.replace('\\', '\\\\')
						self.concisetrack.append('"track_title": ' + json.dumps(variousartistfix.decode('iso-8859-1').encode("utf-8").rstrip() + ' - ' + self.varioustracktitle.decode('iso-8859-1').encode("utf-8").rstrip()))
						#fo.write("track_title: " + self.buffer + " ")
		# Track Duration Add to Array
		elif tag == 'duration' and 'sub_track' not in self.tagstack and self.thisisnotatrack == 0:
			if len(self.buffer) != 0:
				self.concisetrack.append('"track_duration": ' + json.dumps(self.buffer))
				#fo.write("track_duration: " + self.buffer + " ")
		# Release artist name
		elif tag == 'name' and 'artist' in self.tagstack and 'track' not in self.tagstack and 'extraartists' not in self.tagstack:
			if len(self.buffer) != 0:
				if(self.buffer == "Various" or self.buffer == "various"):
					self.variousartist = 1
				fixartist = re.sub('\(.*?\)','', self.buffer)
				fixartist = re.sub(' | ',' ', fixartist)
				fixartist = re.sub('\*','', fixartist)
				fixartist = re.sub('\s+',' ', fixartist)
				#fixartist = fixartist.replace('"', '\"')
				#fixartist = fixartist.replace('\\', '\\\\')
				fo.write('"l_artist_name": ' + json.dumps(fixartist.lower().rstrip()) + ', ')
				fo.write('"artist_name": ' + json.dumps(fixartist.rstrip()) + ', ')
		# Format Description Array Create
		elif tag == 'description' and self.tagstack[-2] == 'descriptions' and self.tagstack[-3] == 'format':
			if len(self.buffer) != 0:
				self.formatdescriptions.append(json.dumps(self.buffer))
		# Country
		elif tag == 'country':
			if len(self.buffer) != 0:
				fo.write('"country": ' + json.dumps(self.buffer) + ', ')	
		# Release Date
		elif tag == 'released':
			if len(self.buffer) != 0:
				fo.write('"released": ' + json.dumps(self.buffer) + ', ')
				yearmatch = re.match(r"\d{4}", self.buffer)
				if yearmatch is not None:
					if yearmatch.group()[0] != '0' and not yearmatch.group()[0].isalpha():
						fo.write('"year": ' + yearmatch.group() + ', ')
		# Release Genre	Array Create
		elif tag == 'genre':
			if len(self.buffer) != 0:
				self.genres.append(json.dumps(self.buffer))
		# Release Style Array Create
		elif tag == 'style':
			if len(self.buffer) != 0:
				self.styles.append(json.dumps(self.buffer))
		# Release Formats and descriptions Array Parse
		elif self.tagstack[-1] == 'formats':
			if len(self.formats) != 0:
				fo.write('"formats": [')
				if len(self.formats) > 1:
					for item in self.formats[:-1]:
						fo.write('{"format_type": ' + item + '}, ')
					fo.write('{"format_type": ' + self.formats[-1] + '}')
				if len(self.formats) == 1:
					fo.write('{"format_type": ' + self.formats[-1] + '}')
				fo.write('], ')
			if len(self.formatdescriptions) != 0:
				fo.write('"format_descriptions": [')
				if len(self.formatdescriptions) > 1:
					for item in self.formatdescriptions[:-1]:
						fo.write('{"format_description": ' + item + '}, ')
					fo.write('{"format_description": ' + self.formatdescriptions[-1] + '}')
				if len(self.formatdescriptions) == 1:
					fo.write('{"format_description": ' + self.formatdescriptions[-1] + '}')
				fo.write('], ')
			self.formats = []
			self.formatdescriptions = []
		# Release Styles Array Parse
		elif self.tagstack[-1] == 'styles':
			for item in self.styles[:-1]:
				fo.write('{"style": ' + item + '}, ')
			fo.write('{"style": ' + self.styles[-1] + '}')
			fo.write('], ')
			self.styles = []
		# Release Genres Array Parse
		elif self.tagstack[-1] == 'genres':
			for item in self.genres[:-1]:
				fo.write('{"genre": ' + item + '}, ')
			fo.write('{"genre": ' + self.genres[-1] + '}')
			fo.write('], ')
			self.genres = []
		# Track Array Parse
		elif self.tagstack[-1] == 'track':
			if len(self.concisetrack) != 0:
				for item in self.concisetrack[:-1]:
					self.trackstring += ''.join(item + ', ')
				self.tracklist.append('{' + self.trackstring + ""  + self.concisetrack[-1] + '}')
				self.trackstring = ''
				self.concisetrack = []
		# Tracklist Array Parse
		if tag == "tracklist":
			if len(self.tracklist) != 0:
				for item in self.tracklist[:-1]:
					fo.write(item + ',')
				fo.write(self.tracklist[-1])
				fo.write('] ')
			if len(self.tracklist) == 0:
				fo.write('] ')
			self.tracklist = []
		if self.tagstack[-1] == tag:
			self.tagstack.pop()
		if tag == "release":
			fo.write('}\n')
			self.variousartist = 0
			global releaseCounter
			releaseCounter += 1
			#if releaseCounter == 6000:
				#fo.close()
				#print('Processed: {} releases').format(releaseCounter)
				#return
		if tag == 'releases':
			fo.close()
			print('Processed: {} releases').format(releaseCounter)
			return
		self.buffer = ''
	
	def fatalError(exception):
		print("%s\n" % exception)
			
			
if ( __name__ == "__main__"):
	
	fo = codecs.open('releases.json','w',encoding='utf8')

	parser = xml.sax.make_parser()
	parser.setFeature(xml.sax.handler.feature_namespaces, 0)
	
	Handler = ReleaseHandler()
	parser.setContentHandler(Handler)
	
	
	#parser.parse("discogs_20160401_releases.xml")
	try:
		#parser.parse("discogsample.xml")
		parser.parse("discogs_20160601_releases.xml")
	except:
		print "Done"
		
