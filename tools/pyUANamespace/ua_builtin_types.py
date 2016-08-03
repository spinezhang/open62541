#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
###
### Author:  Chris Iatrou (ichrispa@core-vector.net)
### Version: rev 13
###
### This program was created for educational purposes and has been
### contributed to the open62541 project by the author. All licensing
### terms for this source is inherited by the terms and conditions
### specified for by the open62541 project (see the projects readme
### file for more information on the MPLv2 terms and restrictions).
###
### This program is not meant to be used in a production environment. The
### author is not liable for any complications arising due to the use of
### this program.
###

import sys
import xml.dom.minidom as dom
from ua_constants import *
import logging
from time import strftime, strptime

logger = logging.getLogger(__name__)

def getNextElementNode(xmlvalue):
  if xmlvalue == None:
    return None
  xmlvalue = xmlvalue.nextSibling
  while not xmlvalue == None and not xmlvalue.nodeType == xmlvalue.ELEMENT_NODE:
    xmlvalue = xmlvalue.nextSibling
  return xmlvalue

if sys.version_info[0] >= 3:
  # strings are already parsed to unicode
  def unicode(s):
    return s

class opcua_value_t():
  value = None
  name = None
  __alias__ = None
  __binTypeId__ = 0
  stringRepresentation = ""
  knownTypes = []
  parent = None

  def __init__(self, parent):
    self.value = None
    self.parent = parent
    self.stringRepresentation = ""
    self.setStringRepresentation()
    self.__binTypeId__ = 0
    self.setNumericRepresentation()
    self.__alias__ = None
    self.knownTypes = ['boolean', 'int32', 'uint32', 'int16', 'uint16', \
                       'int64', 'uint64', 'byte', 'sbyte', 'float', 'double', \
                       'string', 'bytestring', 'localizedtext', 'statuscode', \
                       'diagnosticinfo', 'nodeid', 'guid', 'datetime', \
                       'qualifiedname', 'expandednodeid', 'xmlelement']
    self.dataType = None
    self.encodingRule = []

  def getValueFieldByAlias(self, fieldname):
    if not isinstance(self.value, list):
        return None
    if not isinstance(self.value[0], opcua_value_t):
        return None
    for val in self.value:
        if val.alias() == fieldname:
            return val.value
    return None

  def setEncodingRule(self, encoding):
    self.encodingRule = encoding

  def getEncodingRule(self):
    return self.encodingRule

  def alias(self, data=None):
    if not data == None:
      self.__alias__ = data
    return self.__alias__

  def isBuiltinByString(self, string):
    if str(string).lower() in self.knownTypes:
      return True
    return False

  def value(self, data=None):
    if not data==None:
      self.__value__ = data
    return self.__value__

  def getTypeByString(self, stringName, encodingRule):
    stringName = str(stringName.lower())
    if stringName == 'boolean':
      t = opcua_BuiltinType_boolean_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'int32':
      t = opcua_BuiltinType_int32_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'uint32':
      t = opcua_BuiltinType_uint32_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'int16':
      t = opcua_BuiltinType_int16_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'uint16':
      t = opcua_BuiltinType_uint16_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'int64':
      t = opcua_BuiltinType_int64_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'uint64':
      t = opcua_BuiltinType_uint64_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'byte':
      t = opcua_BuiltinType_byte_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'sbyte':
      t = opcua_BuiltinType_sbyte_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'float':
      t = opcua_BuiltinType_float_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'double':
      t = opcua_BuiltinType_double_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'string':
      t = opcua_BuiltinType_string_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'bytestring':
      t = opcua_BuiltinType_bytestring_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'localizedtext':
      t = opcua_BuiltinType_localizedtext_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'statuscode':
      t = opcua_BuiltinType_statuscode_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'diagnosticinfo':
      t = opcua_BuiltinType_diagnosticinfo_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'nodeid':
      t = opcua_BuiltinType_nodeid_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'guid':
      t = opcua_BuiltinType_guid_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'datetime':
      t = opcua_BuiltinType_datetime_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'qualifiedname':
      t = opcua_BuiltinType_qualifiedname_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'expandednodeid':
      t = opcua_BuiltinType_expandednodeid_t(self.parent)
      t.setEncodingRule(encodingRule)
    elif stringName == 'xmlelement':
      t = opcua_BuiltinType_xmlelement_t(self.parent)
      t.setEncodingRule(encodingRule)
    else:
      logger.debug("No class representing stringName " + stringName + " was found. Cannot create builtinType.")
      return None
    return t

  def parseXML(self, xmlvalue):
    logger.debug("parsing xmlvalue for " + self.parent.browseName() + " (" + str(self.parent.id()) + ") according to " + str(self.parent.dataType().target().getEncoding()))

    if not "value" in xmlvalue.tagName.lower():
      logger.error("Expected <Value> , but found " + xmlvalue.tagName + " instead. Value will not be parsed.")
      return

    if len(xmlvalue.childNodes) == 0:
      logger.error("Expected childnodes for value, but none where found... Value will not be parsed.")
      return

    for n in xmlvalue.childNodes:
      if n.nodeType == n.ELEMENT_NODE:
        xmlvalue = n
        break

    if "ListOf" in xmlvalue.tagName:
      self.value = []
      for el in xmlvalue.childNodes:
        if not el.nodeType == el.ELEMENT_NODE:
          continue
        self.value.append(self.__parseXMLSingleValue(el))
    else:
      self.value = [self.__parseXMLSingleValue(xmlvalue)]

    logger.debug( "Parsed Value: " + str(self.value))

  def __parseXMLSingleValue(self, xmlvalue, alias=None, encodingPart=None):
    # Parse an encoding list such as enc = [[Int32], ['Duration', ['DateTime']]],
    # returning a possibly aliased variable or list of variables.
    # Keep track of aliases, as ['Duration', ['Hawaii', ['UtcTime', ['DateTime']]]]
    # will be of type DateTime, but tagged as <Duration>2013-04-10 12:00 UTC</Duration>,
    # and not as <Duration><Hawaii><UtcTime><String>2013-04-10 12:00 UTC</String>...

    # Encoding may be partially handed down (iterative call). Only resort to
    # type definition if we are not given a specific encoding to match
    if encodingPart == None:
      enc = self.parent.dataType().target().getEncoding()
    else:
      enc = encodingPart

    # Check the structure of the encoding list to determine if a type is to be
    # returned or we need to descend further checking aliases or multipart types
    # such as extension Objects.
    if len(enc) == 1:
      # 0: ['BuiltinType']          either builtin type
      # 1: [ [ 'Alias', [...], n] ] or single alias for possible multipart
      if isinstance(enc[0], str):
        # 0: 'BuiltinType'
        if alias != None:
          if not xmlvalue.tagName == alias:
            logger.error("Expected XML element with tag " + alias + " but found " + xmlvalue.tagName + " instead")
            return None
          else:
            t = self.getTypeByString(enc[0], enc)
            t.alias(alias)
            t.parseXML(xmlvalue)
            return t
        else:
          if not self.isBuiltinByString(xmlvalue.tagName):
            logger.error("Expected XML describing builtin type " + enc[0] + " but found " + xmlvalue.tagName + " instead")
          else:
            t = self.getTypeByString(enc[0], enc)
            t.parseXML(xmlvalue)
            return t
      else:
        # 1: ['Alias', [...], n]
        # Let the next elif handle this
        return self.__parseXMLSingleValue(xmlvalue, alias=alias, encodingPart=enc[0])
    elif len(enc) == 3 and isinstance(enc[0], str):
      # [ 'Alias', [...], 0 ]          aliased multipart
      if alias == None:
        alias = enc[0]
      # if we have an alias and the next field is multipart, keep the alias
      elif alias != None and len(enc[1]) > 1:
        alias = enc[0]
      # otherwise drop the alias
      return self.__parseXMLSingleValue(xmlvalue, alias=alias, encodingPart=enc[1])
    else:
      # [ [...], [...], [...]] multifield of unknowns (analyse separately)
      # create an extension object to hold multipart type

      # FIXME: This implementation expects an extensionobject to be manditory for
      #        multipart variables. Variants/Structures are not included in the
      #        OPCUA Namespace 0 nodeset.
      #        Consider moving this ExtensionObject specific parsing into the
      #        builtin type and only determining the multipart type at this stage.
      if not xmlvalue.tagName == "ExtensionObject":
        logger.error("Expected XML tag <ExtensionObject> for multipart type, but found " + xmlvalue.tagName + " instead.")
        return None

      extobj = opcua_BuiltinType_extensionObject_t(self.parent)
      extobj.setEncodingRule(enc)
      etype = xmlvalue.getElementsByTagName("TypeId")
      if len(etype) == 0:
        logger.error("Did not find <TypeId> for ExtensionObject")
        return None
      etype = etype[0].getElementsByTagName("Identifier")
      if len(etype) == 0:
        logger.error("Did not find <Identifier> for ExtensionObject")
        return None
      etype = self.parent.getNamespace().getNodeByIDString(etype[0].firstChild.data)
      if etype == None:
        logger.error("Identifier Node not found in namespace" )
        return None

      extobj.typeId(etype)

      ebody = xmlvalue.getElementsByTagName("Body")
      if len(ebody) == 0:
        logger.error("Did not find <Body> for ExtensionObject")
        return None
      ebody = ebody[0]

      # Body must contain an Object of type 'DataType' as defined in Variable
      ebodypart = ebody.firstChild
      if not ebodypart.nodeType == ebodypart.ELEMENT_NODE:
        ebodypart = getNextElementNode(ebodypart)
      if ebodypart == None:
        logger.error("Expected ExtensionObject to hold a variable of type " + str(self.parent.dataType().target().browseName()) + " but found nothing.")
        return None

      if not ebodypart.tagName == self.parent.dataType().target().browseName():
        logger.error("Expected ExtensionObject to hold a variable of type " + str(self.parent.dataType().target().browseName()) + " but found " + str(ebodypart.tagName) + " instead.")
        return None
      extobj.alias(ebodypart.tagName)

      ebodypart = ebodypart.firstChild
      if not ebodypart.nodeType == ebodypart.ELEMENT_NODE:
        ebodypart = getNextElementNode(ebodypart)
      if ebodypart == None:
        logger.error("Description of dataType " + str(self.parent.dataType().target().browseName()) + " in ExtensionObject is empty/invalid.")
        return None

      extobj.value = []
      for e in enc:
        if not ebodypart == None:
          extobj.value.append(extobj.__parseXMLSingleValue(ebodypart, alias=None, encodingPart=e))
        else:
          logger.error("Expected encoding " + str(e) + " but found none in body.")
        ebodypart = getNextElementNode(ebodypart)
      return extobj

  def setStringRepresentation(self):
    pass

  def setNumericRepresentation(self):
    pass

  def getNumericRepresentation(self):
    return self.__binTypeId__

  def __str__(self):
    if self.__alias__ != None:
      return "'" + self.alias() + "':" + self.stringRepresentation + "(" + str(self.value) + ")"
    return self.stringRepresentation + "(" + str(self.value) + ")"

  def __repr__(self):
    return self.__str__()

###
### Actual builtin types
###

class opcua_BuiltinType_extensionObject_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "ExtensionObject"
    self.__typeId__ = None

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_EXTENSIONOBJECT

  def typeId(self, data=None):
    if not data == None:
      self.__typeId__ = data
    return self.__typeId__

  def getCodeInstanceName(self):
    return self.__codeInstanceName__

  def setCodeInstanceName(self, recursionDepth, arrayIndex):
    self.__inVariableRecursionDepth__ = recursionDepth
    self.__inVariableArrayIndex__ = arrayIndex
    self.__codeInstanceName__ = self.parent.getCodePrintableID() + "_" + str(self.alias()) + "_" + str(arrayIndex) + "_" + str(recursionDepth)
    return self.__codeInstanceName__

  def printOpen62541CCode_SubType(self, asIndirect=True):
    if asIndirect == False:
      return "*" + str(self.getCodeInstanceName())
    return str(self.getCodeInstanceName())

  def __str__(self):
    return "'" + self.alias() + "':" + self.stringRepresentation + "(" + str(self.value) + ")"

class opcua_BuiltinType_localizedtext_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "LocalizedText"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_LOCALIZEDTEXT

  def parseXML(self, xmlvalue):
    # Expect <LocalizedText> or <AliasName>
    #          <Locale>xx_XX</Locale>
    #          <Text>TextText</Text>
    #        <LocalizedText> or </AliasName>
    #
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    if xmlvalue.firstChild == None:
      if self.alias() != None:
        logger.debug("Neither locale nor text in XML description field " + self.alias() + ". Setting to default ['','']")
      else:
        logger.debug("Neither locale nor text in XML description. Setting to default ['','']")
      self.value = ['','']
      return

    self.value = []
    tmp = xmlvalue.getElementsByTagName("Locale")
    if len(tmp) == 0:
      logger.warn("Did not find a locale. Setting to \"\" per default.")
      self.value.append('')
    else:
      if tmp[0].firstChild == None:
        logger.warn("Locale tag without contents. Setting to \"\" per default.")
        self.value.append('')
      else:
        self.value.append(tmp[0].firstChild.data)
      clean = ""
      for s in self.value[0]:
        if s in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_":
          clean = clean + s
      self.value[0] = clean

    tmp = xmlvalue.getElementsByTagName("Text")
    if len(tmp) == 0:
      logger.warn("Did not find a Text. Setting to empty string per default.")
      self.value.append('')
    else:
      if tmp[0].firstChild == None:
        logger.warn("Text tag without content. Setting to empty string per default.")
        self.value.append('')
      else:
        self.value.append(tmp[0].firstChild.data)

class opcua_BuiltinType_expandednodeid_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "ExpandedNodeId"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_EXPANDEDNODEID

  def parseXML(self, xmlvalue):
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    logger.debug("Not implemented", LOG_LEVEL_ERR)

class opcua_BuiltinType_nodeid_t(opcua_value_t):
  def printOpen62541CCode_SubType(self, asIndirect=True):
    if self.value == None:
      return "UA_NODEID_NUMERIC(0,0)"
    nodeId = self.value.id()
    if nodeId.i != None:
      return "UA_NODEID_NUMERIC(" + str(nodeId.ns) + ", " + str(nodeId.i) + ")"
    elif nodeId.s != None:
      return "UA_NODEID_STRING("  + str(nodeId.ns) + ", " + str(nodeId.s) + ")"
    elif nodeId.b != None:
      logger.debug("NodeID Generation macro for bytestrings has not been implemented.")
      return "UA_NODEID_NUMERIC(0,0)"
    elif nodeId.g != None:
      logger.debug("NodeID Generation macro for guids has not been implemented.")
      return "UA_NODEID_NUMERIC(0,0)"
    return "UA_NODEID_NUMERIC(0,0)"

class opcua_BuiltinType_datetime_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "DateTime"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_DATETIME

  def parseXML(self, xmlvalue):
    # Expect <DateTime> or <AliasName>
    #        2013-08-13T21:00:05.0000L
    #        </DateTime> or </AliasName>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <DateTime /> by setting the value to a default
    if xmlvalue.firstChild == None :
      logger.debug("No value is given. Setting to default now()")
      self.value = strptime(strftime("%Y-%m-%dT%H:%M%S"), "%Y-%m-%dT%H:%M%S")
    else:
      timestr = unicode(xmlvalue.firstChild.data)
      # .NET tends to create this garbage %Y-%m-%dT%H:%M:%S.0000z
      # strip everything after the "." away for a posix time_struct
      if "." in timestr:
        timestr = timestr[:timestr.index(".")]
      # If the last character is not numeric, remove it
      while len(timestr)>0 and not timestr[-1] in "0123456789":
        timestr = timestr[:-1]
      try:
        self.value = strptime(timestr, "%Y-%m-%dT%H:%M:%S")
      except:
        logger.error("Timestring format is illegible. Expected 2001-01-30T21:22:23, but got " + timestr + " instead. Time will be defaultet to now()")
        self.value = strptime(strftime("%Y-%m-%dT%H:%M%S"), "%Y-%m-%dT%H:%M%S")

class opcua_BuiltinType_qualifiedname_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "QualifiedName"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_QUALIFIEDNAME

  def parseXML(self, xmlvalue):
    # Expect <QualifiedName> or <AliasName>
    #           <NamespaceIndex>Int16<NamespaceIndex> # Optional, apparently ommitted if ns=0 ??? (Not given in OPCUA Nodeset2)
    #           <Name>SomeString<Name>                # Speculation: Manditory if NamespaceIndex is given, omitted otherwise?
    #        </QualifiedName> or </AliasName>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Qalified /> by setting the value to a default
    if xmlvalue.firstChild == None :
      logger.debug("No value is given. Setting to default empty string in ns=0: [0, '']")
      self.value = [0, '']
    else:
      # Is a namespace index passed?
      if len(xmlvalue.getElementsByTagName("NamespaceIndex")) != 0:
        self.value = [int(xmlvalue.getElementsByTagName("NamespaceIndex")[0].firstChild.data)]
        # namespace index is passed and <Name> tags are now manditory?
        if len(xmlvalue.getElementsByTagName("Name")) != 0:
          self.value.append(xmlvalue.getElementsByTagName("Name")[0].firstChild.data)
        else:
          logger.debug("No name is specified, will default to empty string")
          self.value.append('')
      else:
        logger.debug("No namespace is specified, will default to 0")
        self.value = [0]
        self.value.append(unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_statuscode_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "StatusCode"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_STATUSCODE

  def parseXML(self, xmlvalue):
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return
    logger.warn("Not implemented")

class opcua_BuiltinType_diagnosticinfo_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "StatusCode"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_DIAGNOSTICINFO

  def parseXML(self, xmlvalue):
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return
    logger.warn("Not implemented")

class opcua_BuiltinType_guid_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "Guid"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_GUID

  def parseXML(self, xmlvalue):
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Guid /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = [0,0,0,0]
    else:
      self.value = unicode(xmlvalue.firstChild.data)
      self.value = self.value.replace("{","")
      self.value = self.value.replace("}","")
      self.value = self.value.split("-")
      tmp = []
      ok = True
      for g in self.value:
        try:
          tmp.append(int("0x"+g, 16))
        except:
          logger.error("Invalid formatting of Guid. Expected {01234567-89AB-CDEF-ABCD-0123456789AB}, got " + unicode(xmlvalue.firstChild.data))
          self.value = [0,0,0,0,0]
          ok = False
      if len(tmp) != 5:
        logger.error("Invalid formatting of Guid. Expected {01234567-89AB-CDEF-ABCD-0123456789AB}, got " + unicode(xmlvalue.firstChild.data))
        self.value = [0,0,0,0]
        ok = False
      self.value = tmp

class opcua_BuiltinType_boolean_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "Boolean"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_BOOLEAN

  def parseXML(self, xmlvalue):
    # Expect <Boolean>value</Boolean> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Boolean /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = "false"
    else:
      if "false" in unicode(xmlvalue.firstChild.data).lower():
        self.value = "false"
      else:
        self.value = "true"

class opcua_BuiltinType_byte_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "Byte"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_BYTE

  def parseXML(self, xmlvalue):
    # Expect <Byte>value</Byte> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Byte /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0
    else:
      try:
        self.value = int(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_sbyte_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "SByte"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_SBYTE

  def parseXML(self, xmlvalue):
    # Expect <SByte>value</SByte> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <SByte /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0
    else:
      try:
        self.value = int(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_int16_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "Int16"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_INT16

  def parseXML(self, xmlvalue):
    # Expect <Int16>value</Int16> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Int16 /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0
    else:
      try:
        self.value = int(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_uint16_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "UInt16"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_UINT16

  def parseXML(self, xmlvalue):
    # Expect <UInt16>value</UInt16> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <UInt16 /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0
    else:
      try:
        self.value = int(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_int32_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "Int32"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_INT32

  def parseXML(self, xmlvalue):
    # Expect <Int32>value</Int32> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Int32 /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0
    else:
      try:
        self.value = int(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_uint32_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "UInt32"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_UINT32

  def parseXML(self, xmlvalue):
    # Expect <UInt32>value</UInt32> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <UInt32 /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0
    else:
      try:
        self.value = int(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_int64_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "Int64"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_INT64

  def parseXML(self, xmlvalue):
    # Expect <Int64>value</Int64> or
    #        <Aliasname>value</Aliasname>
    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Int64 /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0
    else:
      try:
        self.value = int(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_uint64_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "UInt64"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_UINT64

  def parseXML(self, xmlvalue):
    # Expect <UInt16>value</UInt16> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <UInt64 /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0
    else:
      try:
        self.value = int(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_float_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "Float"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_FLOAT

  def parseXML(self, xmlvalue):
    # Expect <Float>value</Float> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Float /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0.0
    else:
      try:
        self.value = float(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_double_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "Double"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_DOUBLE

  def parseXML(self, xmlvalue):
    # Expect <Double>value</Double> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <Double /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = 0.0
    else:
      try:
        self.value = float(unicode(xmlvalue.firstChild.data))
      except:
        logger.error("Error parsing integer. Expected " + self.stringRepresentation + " but got " + unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_string_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "String"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_STRING

  def pack(self):
    bin = structpack("I", len(unicode(self.value)))
    bin = bin + str(self.value)
    return bin

  def parseXML(self, xmlvalue):
    # Expect <String>value</String> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <String /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = ""
    else:
      self.value = str(unicode(xmlvalue.firstChild.data))

class opcua_BuiltinType_xmlelement_t(opcua_BuiltinType_string_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "XmlElement"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_XMLELEMENT

class opcua_BuiltinType_bytestring_t(opcua_value_t):
  def setStringRepresentation(self):
    self.stringRepresentation = "ByteString"

  def setNumericRepresentation(self):
    self.__binTypeId__ = BUILTINTYPE_TYPEID_BYTESTRING

  def parseXML(self, xmlvalue):
    # Expect <ByteString>value</ByteString> or
    #        <Aliasname>value</Aliasname>
    if xmlvalue == None or xmlvalue.nodeType != xmlvalue.ELEMENT_NODE:
      logger.error("Expected XML Element, but got junk...")
      return

    if self.alias() != None:
      if not self.alias() == xmlvalue.tagName:
        logger.warn("Expected an aliased XML field called " + self.alias() + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")
    else:
      if not self.stringRepresentation == xmlvalue.tagName:
        logger.warn("Expected XML field " + self.stringRepresentation + " but got " + xmlvalue.tagName + " instead. This is a parsing error of opcua_value_t.__parseXMLSingleValue(), will try to continue anyway.")

    # Catch XML <ByteString /> by setting the value to a default
    if xmlvalue.firstChild == None:
      logger.debug("No value is given. Setting to default 0")
      self.value = ""
    else:
      self.value = str(unicode(xmlvalue.firstChild.data))
