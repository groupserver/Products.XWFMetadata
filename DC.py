from AccessControl import getSecurityManager

from Products.XWFMetadata.XWFMetadata import *

import types

class LinkedResources(XWFMetadataURLs):
    indexName = 'linked_resources'
    
    label = 'Resource URLs'
    hint = 'A list of URLs linked to this news item'
    
    requiredError = 'One or more Resource URLs must be specified'
    
    def tidy(self, val):
        if not val:
            return val
        
        val = val.split()
        val = filter(None, map(lambda x: x.strip(), val))
        
        return val
        
class DCCreator(XWFMetadataString):
    namespace = 'http://purl.org/dc/elements/1.1/creator'

    indexName = 'dc_creator'
    
    label = 'Creator Name'
    hint = 'Please enter the creators name'
    
    requiredError = 'The creator must be specified'
    
    def default(self):
        return getSecurityManager().getUser().getId()
    
class DCTitle(XWFMetadataString):
    namespace = 'http://purl.org/dc/elements/1.1/title'

    indexName = 'dc_title'
    alternativeIndexNames = ['title']
    
    label = 'Title'
    hint = 'Please enter the title'
    
    requiredError = 'A title must be specified'
    
class DCCreated(XWFMetadataDateTime):
    namespace = 'http://purl.org/dc/terms/valid'
    
    indexName = 'dc_created'
    label = 'Creation date'
    hint = ''
    
    requiredError = 'A creation date must be specified'
    
class DCValid(XWFMetadataDateTime):
    namespace = 'http://purl.org/dc/terms/valid'
    
    indexName = 'dc_valid'
    
    label = 'Publication Date/Time'
    hint = 'Date and Time from which this news item should be published'
    
    requiredError = 'A publication date must be specified'
    
class DCDescription(XWFMetadataText):
    namespace = 'http://purl.org/dc/elements/1.1/description'
    
    indexName = 'dc_description'
    
    label = 'Description'
    hint = 'A description of the news item, XHTML elements may be used'
    
    requiredError = 'A description must be specified'