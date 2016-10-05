#!/usr/bin/env python
"""A quick usage example.

Once voeventparse is installed, this should tell you most of what you need to know
in order to start doing things with VOEvent packets.

The attributes are built from the structure of the XML file,
so the best way to understand where the variable names come from is to simply
open the XML packet in your favourite web browser and dig around.

See also:
* lxml documentation at http://lxml.de/objectify.html
* VOEvent standard at http://www.ivoa.net/documents/VOEvent/
* VOEvent schema file at http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd
"""
from __future__ import print_function
import urllib
def parse(payload,root):
    """
    Payload handler that archives VOEvent messages as files in the current
    working directory. The filename is a URL-escaped version of the messages'
    IVORN.
    """
    import copy
    import voeventparse

    ivorn = root.attrib['ivorn']
    filename = urllib.quote_plus(ivorn)

    with open(filename, "w") as f:
        f.write(payload)

    with open(filename, 'rb') as f:
        v = voeventparse.load(f)
    
    filename = filename+'PARSED_TABLE'
    with open(filename,'w') as fp:
        #Basic attribute access
        fp.write("Ivorn:{}\n".format(v.attrib['ivorn']))
        fp.write("Role:{}\n".format(v.attrib['role']))
        fp.write( "AuthorIVORN:{}\n".format(v.Who.AuthorIVORN))
        fp.write( "Short name:{}\n".format(v.Who.Author.shortName))
        fp.write( "Contact:{}\n".format(v.Who.Author.contactEmail))
        
        #Copying by value, and validation:
        fp.write( "Original valid as v2.0? {}\n".format(voeventparse.valid_as_v2_0(v)))
        v_copy = copy.copy(v)
        fp.write( "Copy valid? {}\n".format(voeventparse.valid_as_v2_0(v_copy)))
        
        #Changing values:
        v_copy.Who.Author.shortName = 'BillyBob'
        v_copy.attrib['role'] = voeventparse.definitions.roles.test
        fp.write( "Changes valid? {}\n".format(voeventparse.valid_as_v2_0(v_copy)))
        
        v_copy.attrib['role'] = 'flying circus'
        fp.write( "How about now? {}\n".format(voeventparse.valid_as_v2_0(v_copy)))
        fp.write( "But the original is ok, because we copied? {}\n".format(voeventparse.valid_as_v2_0(v)))
        
        v.Who.BadPath = "This new attribute certainly won't conform with the schema."
        assert voeventparse.valid_as_v2_0(v) == False
        del v.Who.BadPath
        assert voeventparse.valid_as_v2_0(v) == True
        #######################################################
        # And now, SCIENCE
        #######################################################
        c = voeventparse.pull_astro_coords(v)
        fp.write( "Coords: {}\n".format(c))

# Command line interface
DEFAULT_HOST = '68.169.57.253'
DEFAULT_PORT = 8099
from optparse import Option, OptionParser
parser = OptionParser(description=__doc__, usage='%prog [options] [HOSTNAME[:PORT]]')
opts, args = parser.parse_args()
if len(args) == 0:
    host = DEFAULT_HOST
    port = DEFAULT_PORT
elif len(args) == 1:
    host, _, port = args[0].partition(':')
    if port:
        try:
            port = int(port)
        except ValueError:
            parser.error('invalid hostname: "{0}"'.format(args[0]))
    else:
        port = DEFAULT_PORT
else:
    parser.error('too many command line arguments')

# Imports
import gcn
#import gcn.handlers
import logging

# Set up logger
logging.basicConfig(level=logging.INFO)

# Listen for GCN notices (until interrupted or killed)
gcn.listen(host=host, port=port, handler=parse)

