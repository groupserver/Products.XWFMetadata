import types

from OFS.SimpleItem import SimpleItem
from types import StringType
import DateTime

from Products.XWFCore.XWFUtils import getToolByName

class Record:
    pass
    
class XWFMetadataValidation:
    def validate(self, context, val):
        required = getattr(self, 'required', None)
        if required and not val:
            return (None, getattr(self, 'requiredError', 'no error message specified'))
        
        validator = getattr(self, 'validator', lambda y, x: (x, None))
        val, message = validator(context, val)
        
        return val, message
        
class XWFMetadataForm:
    def xform_data(self, context, form):
        if form.get('__populate__', True):
            xf_value = self.current_xform_value(context, form)
        else:
            xf_value = None
            
        if xf_value:
            f = '''<%s>%s</%s>''' % (self.indexName, str(xf_value), self.indexName)
        else:
            f = '''<%s/>''' % self.indexName
        
        return f
    
    def current_xform_value(self, context, form):
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
        
        index_id = getattr(self, 'indexName', None)
        index_type = getattr(self, 'indexType', None)
        if not index_id or not index_type:
            return
            
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
    def xform_control(self, context, model_id, cssclass='text'):
        f = '''<xf:textarea model="%s" %s="%s" class="%s">
                   <xf:label>%s</xf:label>
                   <xf:hint>%s</xf:hint>
               </xf:textarea>''' % (model_id, self.required and 'bind' or 'ref',
                                    self.indexName, cssclass,
                                    self.label, self.hint)    
        return f

class XWFMetadataSelection(XWFMetadataBase):
    def __init__( self, required=False, automatic=False, setDefault=None,
                        selections=() ):
        XWFMetadataBase.__init__(self, required, automatic, setDefault)
        self.selections = selections

    def xform_control(self, context, model_id, cssclass='text'):
        item = """<xf:item>
                        <xf:label>%s</xf:label>
                        <xf:value>%s</xf:value>
                  </xf:item>"""
        items = []
        # if selections is a string, get the method it corresponds to
        if isinstance(self.selections, StringType):
            selections = getattr(context, self.selections)()
        else:
            selections = self.selections
        
        for selection in selections:
            items.append(item % selection)
            
        f = '''<xf:select1 model="%s" %s="%s"
                    appearance="minimal" class="%s">
                    <xf:label>%s</xf:label>
                    <xf:hint>%s</xf:hint>
                    <xf:item>
                        <xf:label>----Select----</xf:label>
                        <xf:value></xf:value>
                    </xf:item>
                    %s
               </xf:select1>''' % (model_id, self.required and 'bind' or 'ref',
                                   self.indexName, cssclass, self.label,
                                   self.hint, '\n'.join(items))
                                   
        return f

class XWFMetadataStringSelection(XWFMetadataSelection):
    indexType = 'KeywordIndex'
    
    xsdDataType = 'string'
    propertyDataType = 'ustring'

class XWFMetadataString(XWFMetadataBase):
    indexType = 'KeywordIndex'
    
    xsdDataType = 'string'
    propertyDataType = 'ustring'
    
    def xform_control(self, context, model_id, cssclass='text'):
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
    
    def xform_control(self, context, model_id, cssclass='text'):
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
    
    requiredError = 'You must specify a date'
    
    validationError = ('Date was specified, but should be in the format '
                       'eg. 10 Jun 2005 12:00pm')
    
    def validator(self, context, val):
        try:
            DateTime.DateTime(val)
        except DateTime.DateTime.SyntaxError:
            return None, self.validationError
        
        return val, None
        
    def xform_control(self, context, model_id, cssclass='text'):
        f = '''<xf:date model="%s" %s="%s" class="%s">
                   <xf:label>%s</xf:label>
                   <xf:hint>%s</xf:hint>
               </xf:date>''' % (model_id, self.required and 'bind' or 'ref',
                                self.indexName, cssclass, self.label, self.hint)
        return f

    default = DateTime.DateTime

class File(XWFMetadataString):
    indexName = 'file'
    
    xsdDataType = 'string'
    propertyDataType = 'file'
    
    label = 'File'
    hint = 'Select the file you wish to upload'
    
    requiredError = 'You must specify a file to upload'
    
    def xform_control(self, context, model_id, cssclass='text'):
        f = '''<xf:upload model="%s" %s="%s" class="%s">
                   <xf:label>%s</xf:label>
                   <xf:hint>%s</xf:hint>
               </xf:upload>''' % (model_id, self.required and 'bind' or 'ref',
                                self.indexName, cssclass, self.label, self.hint)
        return f

class Tags(XWFMetadataString):
    indexType = 'KeywordIndex'
    indexName = 'tags'
    
    xsdDataType = 'string'
    propertyDataType = 'utokens'
    
    requiredError = 'You must specify one or more tags'
    
    label = 'Tags'
    hint = 'One or more space separated keywords, which best represent this item'
    