#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#       pyStaticWP.py
#       
#       Copyright 2011 Giorgio Gilestro <giorgio@gilest.ro>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
#       

__author__ = "Giorgio Gilestro <giorgio@gilest.ro>"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2011/08/16 21:57:19 $"
__copyright__ = "Copyright (c) 2011 Giorgio Gilestro"
__license__ = "Python"

from urlparse import urljoin, urlparse, urldefrag
from urllib import urlopen
import optparse, ConfigParser, os

from xml.dom.minidom import parse, parseString
from sgmllib import SGMLParser

class URLLister(SGMLParser):
    """
    http://www.grabner-online.de/div_into/html/dialect_extract.links.html
    """
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []

    def start_a(self, attrs):
        href = [v for k, v in attrs if k=='href']
        if href:
            self.urls.extend(href)

    def start_script(self, attrs):
        src = [v for k, v in attrs if k=='src']
        if src:
            self.urls.extend(src)

    def start_link(self, attrs):
        href = [v for k, v in attrs if k=='href']
        if href:
            self.urls.extend(href)


class myConfig():
    """
    Handles program configuration
    Uses ConfigParser to store and retrieve
    """
    def __init__(self, filename=None, temporary=False, defaultOptions=None):
        """
        filename    the name of the configuration file
        temporary   whether we are reading and storing values temporarily
        defaultOptions  a dict containing the defaultOptions
        """
        
        filename = filename or 'config.cfg'
        pDir = os.getcwd()
        if not os.access(pDir, os.W_OK): pDir = os.environ['HOME']

        self.filename = os.path.join (pDir, filename)
        self.filename_temp = '%s~' % self.filename
        
        self.config = None
        
        if defaultOptions == None: 
            self.defaultOptions = defaultOptions
        else:
            self.defaultOptions = {
                              'Wordpress_URL' : ['http://blog.example.com', 'The URL of your wordpress blog'],
                              'Static_URL' : ['http://www.example.com', 'Where your visitors will find the static blog'],
                              'Sitemap_file' : ['', 'The name of the sitemapfile'],
                              'root' : ['.', 'The root where files are saved']
                                    }
        
        self.Read(temporary)

    def New(self, filename):
        """
        """
        self.filename = filename
        self.Read()  

    def Read(self, temporary=False):
        """
        read the configuration file. Initiate one if does not exist
        
        temporary       True                Read the temporary file instead
                        False  (Default)     Read the actual file
        """

        if temporary: filename = self.filename_temp
        else: filename = self.filename        
        
        if os.path.exists(filename):
            self.config = ConfigParser.RawConfigParser()
            self.config.read(filename)   
            
        else:
            self.Save(temporary, newfile=True)

                               
    def Save(self, temporary=False, newfile=False):
        """
        """
        if temporary: filename = self.filename_temp
        else: filename = self.filename
            
        if newfile:
            self.config = ConfigParser.RawConfigParser()
            self.config.add_section('Options')
            
            for key in self.defaultOptions:
                self.config.set('Options', key, self.defaultOptions[key][0])

        with open(filename, 'wb') as configfile:
            self.config.write(configfile)
    
        if not temporary: self.Save(temporary=True)


    def SetValue(self, section, key, value):
        """
        """
        
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, value)
        
    def GetValue(self, section, key):
        """
        get value from config file
        Does some sanity checking to return tuple, integer and strings 
        as required.
        """
        r = self.config.get(section, key)
        
        if type(r) == type(0) or type(r) == type(1.0): #native int and float
            return r
        elif type(r) == type(True): #native boolean
            return r
        elif type(r) == type(''):
            r = r.split(',')
        
        if len(r) == 2: #tuple
            r = tuple([int(i) for i in r]) # tuple
        
        elif len(r) < 2: #string or integer
            try:
                r = int(r[0]) #int as text
            except:
                r = r[0] #string
        
        if r == 'False' or r == 'True':
            r = (r == 'True') #bool
        
        return r
                

    def GetOption(self, key):
        """
        """
        return self.GetValue('Options', key)

class WPStatic():
    def __init__(self, wp_url, static_url, root=None, sitemap='sitemap.xml'):
        """
        """
        
        self.wp_url = wp_url
        self.sitename = urlparse(wp_url).netloc
        self.static_url = static_url
        self.sitemap = sitemap
        
        if not root:
            root = os.path.curdir
        self.root = root
        
        self.done = set()

    def getPath(self, path, filename=None):
        """
        """

        if os.path.isabs(path):
            path = path[1:]

        if self.root == '.':
            fullpath = self.root + '/' + path
        else:
            fullpath = os.path.join (self.root, path)
        
        if filename:
            fullpath = os.path.join (fullpath, filename)

        return fullpath
        
    def getPageName(self, url):
        """
        """
        path, ext = os.path.splitext( url )
        
        if ext:
            pagename = url.split('/')[-1]
        else:
            pagename = 'index.html'
        
        return pagename
        
    def spider(self, verbose=False):
        """
        """

        if wp.parseSiteMap():
        
            for url in wp.url_list:

                if url not in self.done:

                    if verbose: print ("Fetching page %s" % url)
                    page = wp.getPage(url, write=True)
                    self.done.add(url)

                    in_urls = wp.parseURLS( page )
                    
                    for url2 in in_urls:
                        if url2 not in self.done:

                            if verbose: print ("Fetching page %s" % url)
                            page = wp.getPage(url2, write=True)
                            self.done.add(url)
    
    def getSiteMap(self):
        """
        """

        url = urljoin(self.wp_url, self.sitemap)
        content = urlopen(url).read()
        return content

    def parseSiteMap(self):
        """
        """
        self.url_list = []
        
        xml = parseString( self.getSiteMap() )

        for url in xml.getElementsByTagName("url"):
            l = url.getElementsByTagName("loc")[0].childNodes[0].nodeValue
            self.url_list.append (l)

        return len(self.url_list) > 0
    
    def makeDir(self, path):
        """
        """
        
        if not os.path.exists(path):
            os.makedirs(path)

    def replace(self, page):
        """
        """
        blog = urlparse(self.wp_url).netloc
        static = urlparse(self.static_url).netloc
        
        while blog in page:
            page = page.replace(blog, static)
            
        return page

    def getPage(self, url, write=True, replace=True):
        """
        """
        page = ''

        
        if os.path.isabs( url ):
            url = urljoin ( self.wp_url , url )

        url,_ = urldefrag(url)
       
        pagename = self.getPageName(url)
        path = self.getPath( urlparse(url).path )
        fullpath = self.getPath( urlparse(url).path , pagename )
        
        page = urlopen(url).read()
        
        if replace: page = self.replace(page)
        
        if write:
            self.makeDir( path )
            with open(fullpath, 'w') as fh:
                fh.write(page)
        
    
        return page

    def parseURLS(self, html):
        """
        """
        local_urls = []
        parser = URLLister()
        parser.feed(html)
        parser.close()
        for url in parser.urls:
            u = urlparse(url)
            loc, path = u.netloc, u.path
            if loc in self.wp_url:
                local_urls.append(url)
                
        return local_urls

    

if __name__ == '__main__':

    fetch = False
    parser = optparse.OptionParser(usage='%prog [options] [argument]', version='%prog version 0.1')
    parser.add_option('-b', '--blog', dest='blog', metavar="BLOG_URL", help="The URL of your wordpress blog")
    parser.add_option('-s', '--static', dest='static', metavar="STATIC_URL", help="Where your visitors will find the static blog")
    parser.add_option('-r', '--root', dest='root', metavar="root", help="path to the root dir of the static files")
    parser.add_option('--useconfig', action="store_true", default=False, dest='useconfig', help="Use configuration file")
    parser.add_option('--verbose', action="store_true", default=False, dest='verbose', help="Tell me what you are doing")

    (options, args) = parser.parse_args()
    
    if options.blog and options.static:
        blog = options.blog
        static = options.static
        root = options.root
        fetch = True

    elif options.useconfig:
        config = myConfig()
        blog = config.GetOption('Wordpress_URL')
        static = config.GetOption('Static_URL')
        root = config.GetOption('root')
        fetch = True
        
    else:
        parser.print_help()
    
    if fetch:
        wp = WPStatic(blog, static, root)
        wp.spider(verbose=options.verbose)

