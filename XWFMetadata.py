import types

from OFS.OrderedFolder import OrderedFolder
from OFS.ObjectManager import ObjectManager
from AccessControl import Role, getSecurityManager, ClassSecurityInfo
from AccessControl.Role import RoleManager
from AccessControl.Owned import Owned
from OFS.SimpleItem import SimpleItem
from zExceptions import BadRequest
import DateTime

from Products.XWFCore.XWFUtils import getToolByName

class Record:
    pass
    
class XWFMetadataValidation:
    def validate(self, val):
        #tidy = getattr(self, 'tidy', lambda x: x)
        #val = tidy(val)
        
        required = getattr(self, 'required', None)
        if required and not val:
            return (None, self.requiredError)
        
        validator = getattr(self, 'validator', lambda x: (x, None))
        val, message = validator(val)
        
        return val, message
        
class XWFMetadataForm:
    def xform_data(self, form):
        if form.get('__populate__', True):
            xf_value = self.current_xform_value(form)
        else:
            xf_value = None
            
        if xf_value:
            f = '''<%s>%s</%s>''' % (self.indexName, str(xf_value), self.indexName)
        else:
            f = '''<%s/>''' % self.indexName
        
        return f
    
    def current_xform_value(self, form):
        val = form.get(getattr(self, 'indexName', self.id), None)
        
        if not val:
            return None
        elif type(val) == types.ListType or type(val) == types.TupleType:
            if self.propertyDataType in ('utokens', 'tokens'):
                val = ' '.join(val)
            else:
                val = '\n'.join(val)
        
        #tidy = getattr(self, 'tidy', lambda x: x)
        #val = tidy(val)
        
        return val    
        
class XWFMetadataBase(SimpleItem, XWFMetadataValidation, XWFMetadataForm):
    meta_type = 'XWF Metadata'
    version = 0.1
    
    indexName = None # index name, eg. dc_title
    alternativeIndexNames = [] # list of alternative names, eg. title
    indexType = None # eg. KeywordIndex
    
    xsdDataType = None # the XML Schema data type eg. string
    propertyDataType = None # the Zope data type eg. ustring
    
    def __init__(self, required=False, automatic=False, setDefault=None):
        self._catalogInit = False
        self.required = required
        self.automatic = automatic
        self.setDefault = setDefault
        
    def setup_catalog(self, context, force=True):
        """ Setup this metadata in the catalog.
        
        """
        # check to see if we've already setup the catalog.
        if self._catalogInit and not force:
            return
            
        catalog = getToolByName(context, 'Catalog')
        indexes = catalog.indexes()
        
        index_id = self.indexName
        index_type = self.indexType
        # skip it if it's already there
        if index_id not in indexes:
            if index_type == 'ZCTextIndex':
                zctextindex_extras = Record()
                zctextindex_extras.index_type = 'Okapi BM25 Rank'
                zctextindex_extras.lexicon_id = 'Lexicon'
                zctextindex_extras.doc_attr = index_id
                catalog.addIndex(index_id, index_type, zctextindex_extras)
            else:
                catalog.addIndex(index_id, index_type)
        
        self._catalogInit = True
        
        return True
    
class XWFMetadataCollection(XWFMetadataBase):
    indexType = 'KeywordIndex'
    
    propertyDataType = 'ulines'
    
class XWFMetadataURLs(XWFMetadataCollection):
    def xform_control(self, model_id, cssclass='text'):
        f = '''<xf:textarea model="%s" %s="%s" class="%s">
                   <xf:label>%s</xf:label>
                   <xf:hint>%s</xf:hint>
               </xf:textarea>''' % (model_id, self.required and 'bind' or 'ref',
                                    self.indexName, cssclass,
                                    self.label, self.hint)    
        return f
       
class XWFMetadataString(XWFMetadataBase):
    indexType = 'KeywordIndex'
    
    xsdDataType = 'string'
    propertyDataType = 'ustring'
    
    def xform_control(self, model_id, cssclass='text'):
        f = '''<xf:input model="%s" %s="%s" class="%s">
                   <xf:label>%s</xf:label>
                   <xf:hint>%s</xf:hint>
               </xf:input>''' % (model_id, self.required and 'bind' or 'ref',
                                 self.indexName, cssclass,
                                 self.label, self.hint)
        return f
        
class XWFMetadataText(XWFMetadataBase):
    indexType = 'ZCTextIndex'
    
    xsdDataType = 'string'
    propertyDataType = 'utext'
    
    def xform_control(self, model_id, cssclass='text'):
        f = '''<xf:textarea model="%s" %s="%s" class="%s">
                   <xf:label>%s</xf:label>
                   <xf:hint>%s</xf:hint>
               </xf:textarea>''' % (model_id, self.required and 'bind' or 'ref',
                                    self.indexName, cssclass,
                                   self.label, self.hint)
        return f
        
class XWFMetadataDateTime(XWFMetadataBase):
    indexType = 'DateIndex'
    
    xsdDataType = 'dateTime'
    propertyDataType = 'date'
    
    validationError = ('Date was specified, but should be in the format '
                       'eg. 10 Jun 2005 12:00pm')
    
    def validator(self, val):
        try:
            DateTime.DateTime(val)
        except DateTime.DateTime.SyntaxError:
            return None, self.validationError
        
        return val, None
        
    def xform_control(self, model_id, cssclass='text'):
        f = '''<xf:date model="%s" %s="%s" class="%s">
                   <xf:label>%s</xf:label>
                   <xf:hint>%s</xf:hint>
               </xf:date>''' % (model_id, self.required and 'bind' or 'ref',
                                self.indexName, cssclass, self.label, self.hint)
        return f

    default = DateTime.DateTime

class Tags(XWFMetadataString):
    indexType = 'KeywordIndex'
    indexName = 'tags'
    
    xsdDataType = 'string'
    propertyDataType = 'utokens'
    
    label = 'Tags'
    hint = 'One or more space separated keywords, which best represent this item'
    