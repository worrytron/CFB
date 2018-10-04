from maya import cmds
from maya import OpenMayaUI as omui 
from maya import mel
from PySide.QtCore import * 
from PySide.QtGui import * 
from shiboken import wrapInstance 

'''
vrayMatteTags.py

author:     Christopher Fung & Stephen Mackenzie
contact:    christopher@mrfung.com
web:        http://www.mrfung.com

version:    0.6
date:       2015.04.21

Description:
    Designed to allow quick and compreshensive setting of tags on objects via vrayUserAttributes, 
    to later be converted into individual render elements for each tag allowing for easily identified
    and extractable mattes in composite.

Notes:
  * Requires vrayformaya.mll to be activated (Obviously).

Limitations:
  * Less limited than before

Updates:
  v0.3  Added "Append vrayUserAttributes" button
  v0.4  Rewriting lots of stuff
  v0.5  Renamed to vrayMatteTags because it's pretty damn useful.  Rebuilt on Python List-based architecture vs String-based architecture.
  v0.6  createRenderElements() no longer creates duplicate "vrayMatteTagSet" maya sets
        createRenderElements() render elements disabled by default upon creation
        getCurrentLayerVrayMatteTagRE() project specific helper function.

References:
  * http://knowledge.autodesk.com/search-result/caas/CloudHelp/cloudhelp/2015/ENU/Maya-SDK/files/GUID-3F96AF53-A47E-4351-A86A-396E7BFD6665-htm.html
  * http://danostrov.com/2012/10/27/creating-a-simple-ui-in-maya-using-pyqt/
  * https://github.com/throb/vfxpipe/blob/master/maya/vrayUtils/createTechPasses.py
  * http://stackoverflow.com/questions/3845423/remove-empty-strings-from-a-list-of-strings
  * http://zurbrigg.com/maya-python/item/a-more-practical-pyside-example

'''

mayaMainWindowPtr = omui.MQtUtil.mainWindow() 
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget) 


class vrayMatteTagsUI(QWidget):

    def __init__(self, *args, **kwargs):
        super(vrayMatteTagsUI, self).__init__(*args, **kwargs)

        self.windowName = 'vrayMatteTags'

        # Check to see if this UI is already open. If UI already exists, destroy it.
        if cmds.window(self.windowName, exists=True):
            cmds.deleteUI(self.windowName)

        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)
        self.setObjectName(self.windowName)
        self.setWindowTitle(self.windowName)
        self.setAttribute(Qt.WA_DeleteOnClose)      # Tells Qt to delete the window when closed (Pyside.QtCore)
        self.createUI()



    ####################################################################################################
    # Builds UI for vrayMatteTags() functionality.        
    ####################################################################################################
    def createUI(self):

        ########################################################################
        # Create Widgets
        ######################################################################## 
        self.assetLabel = QLabel("Asset Tools", parent=self)
        self.tagsLE = QLineEdit('null', parent=self)
        self.getButton = QPushButton( 'Get vrayUserAttributes', self )
        self.getButton.clicked.connect( self.btnGetVrayUserAttributes ) 
        self.setButton = QPushButton( 'Set vrayUserAttributes', self )
        self.setButton.clicked.connect( self.btnSetVrayUserAttributes )
        self.deleteButton = QPushButton( 'Delete vrayUserAttributes', self )
        self.deleteButton.clicked.connect( self.btnDeleteVrayUserAttributes ) 
        self.appendButton = QPushButton( 'Append vrayUserAttributes', self )
        self.appendButton.clicked.connect( self.btnAppendVrayUserAttributes )
        self.selectButton = QPushButton( 'Select by vrayUserAttributes', self )
        self.selectButton.clicked.connect( self.btnSelectByVrayUserAttributes )

        self.renderLabel = QLabel("Render Tools", parent=self)
        self.createButton = QPushButton('Create Render Elements', self)
        self.createButton.clicked.connect(self.btnCreateRenderElements) 
        self.destroyButton = QPushButton('Destroy Render Elements', self)
        self.destroyButton.clicked.connect(self.btnDestroyRenderElements) 
        self.toggleButton = QPushButton('Toggle Render Elements', self)
        self.toggleButton.clicked.connect(self.btnToggleRenderElements) 

        self.debugLabel = QLabel("Debug", parent=self)
        self.verboseCB = QCheckBox('Verbose', parent=self)
        self.verboseCB.stateChanged.connect(self.cbVerboseMode)
        self.verboseCB.setChecked(True)

        self.taglistLabel = QLabel("Tag List", parent=self)
        self.comboMenu = QComboBox()
        self.comboItems= [ 'Widget One', 'Widget Two' ]
        self.comboMenu.insertItems( 0, self.comboItems )
        self.comboMenu.setFixedWidth( 100 )

        self.refresh = QPushButton( "Refresh" )
        self.refresh.clicked.connect( self.loadLights )
        self.listWidget = QListWidget()
        self.listWidget.setStyleSheet( "line-height:20px;" )

        ########################################################################
        # Layout the widgets
        ########################################################################
        assetToolsLayout = QBoxLayout(QBoxLayout.LeftToRight)
        assetToolsLayout.addWidget(self.getButton)
        assetToolsLayout.addWidget(self.setButton)
        assetToolsLayout.addWidget(self.deleteButton)
        assetToolsLayout.addWidget(self.appendButton)
        assetToolsLayout.addWidget(self.selectButton)

        renderToolsLayout = QBoxLayout(QBoxLayout.LeftToRight)
        renderToolsLayout.addWidget(self.createButton)
        renderToolsLayout.addWidget(self.destroyButton)
        renderToolsLayout.addWidget(self.toggleButton)

        mainLayout = QBoxLayout(QBoxLayout.TopToBottom, self)
        mainLayout.addWidget(self.assetLabel)
        mainLayout.addWidget(self.tagsLE)
        mainLayout.addLayout(assetToolsLayout)
        mainLayout.addWidget(self.renderLabel)
        mainLayout.addLayout(renderToolsLayout)
        mainLayout.addWidget(self.debugLabel)
        mainLayout.addWidget(self.verboseCB)

#       mainLayout.addWidget(self.refresh)
#       mainLayout.addWidget(self.listWidget)

        mainLayout.addStretch()
        
        self.setLayout(mainLayout)
        self.show()



    ####################################################################################################
    # btnGetVrayUserAttributes()
    # Helper function that activates on "Get Vray User Attributes" button on all selected objects
    ####################################################################################################  
    def btnGetVrayUserAttributes(self):

        attributeList = []
        attributeString = ''
        shapes = cmds.ls(sl=1, dag=1, lf=1, s=1)

        if not shapes:
            print "btnGetVrayUserAttributes:  No objects selected. Getting empty atributeString"
        else:
            attributeList = parseVrayUserAttributes(shapes)
            attributeString = convertAttributeListToString(attributeList)

        self.tagsLE.setText(attributeString)

        return 0;



    ####################################################################################################
    # btnSetVrayUserAttributes()
    # Helper function that activates on "Set Vray User Attributes" button on all selected objects
    ####################################################################################################  
    def btnSetVrayUserAttributes(self):

        attributeList = []
        attributeString = ''
        attributeString = self.tagsLE.text()
        shapes = cmds.ls(sl=1, dag=1, lf=1, s=1)

        attributeList = convertDirtyInputStringToList( attributeString )

        for attr in attributeList:
            print attr

        for shape in shapes:
            setVrayUserAttributes(shape, attributeList)

        return 0;



    ####################################################################################################
    # btnAppendVrayUserAttributes()
    # Helper function that activates on "Add Vray User Attributes" button
    ####################################################################################################  
    def btnAppendVrayUserAttributes(self):

        attributeList = []
        attributeAnnex = []
        attributeString = self.tagsLE.text()
        shapes = cmds.ls(sl=1, dag=1, lf=1, s=1)

        if not shapes:
            print "btnAppendVrayUserAttributes:  No objects selected. No nodes to apply to."

        attributeAnnex = convertDirtyInputStringToList( attributeString )

        for shape in shapes:
            attributeList = getVrayUserAttributes( shape )
            attributeList = attributeList + attributeAnnex
            attributeList = removeDuplicates( attributeList )
            setVrayUserAttributes( shape, attributeList )

        return 0;



    ####################################################################################################
    # btnDeleteVrayUserAttributes()
    # Helper function that activates on "Set Vray User Attributes" button on all selected objects
    ####################################################################################################  
    def btnDeleteVrayUserAttributes(self):

        shapes = cmds.ls(sl=1, dag=1, lf=1, s=1)

        for shape in shapes:
            if cmds.objExists('%s.vrayUserAttributes' %shape ):
                cmds.deleteAttr( '%s.vrayUserAttributes' %shape )

        return 0;



    ####################################################################################################
    # btnSelectByVrayUserAttributes()
    # 
    ####################################################################################################  
    def btnSelectByVrayUserAttributes(self):

        attributeString = self.tagsLE.text()
        attributeList = convertDirtyInputStringToList( attributeString )
        selectByVrayUserAttributes( attributeList )



    ####################################################################################################
    # btnCreateRenderElements()
    # Helper function that activates on "Create Render Elements" button
    ####################################################################################################  
    def btnCreateRenderElements(self):

        # Select all shape nodes in the scene
        geometry = cmds.ls( geometry=True )
        shapes = cmds.listRelatives( geometry, p=True, path=True )
        # cmds.select(shapes, r=True)               # Don't actually need to perform a selection

        allAttributes = parseVrayUserAttributes( shapes )
        createRenderElements( allAttributes )



    ####################################################################################################
    # btnDestroyRenderElements()
    # Helper function that activates on "Destroy Render Elements" button
    ####################################################################################################  
    def btnDestroyRenderElements(self):

        if not cmds.objExists( 'vrayMatteTagSet' ):
            print "btnDestroyRenderElements: "
            return;

        cmds.select( 'vrayMatteTagSet' )
        cmds.delete()



    ####################################################################################################
    # btnToggleRenderElements()
    # Helper function that activates on "Toggle Render Elements" button
    # Toggles render elements and overrides for vrayUserAttributes found on the current render layer
    ####################################################################################################
    def btnToggleRenderElements(self):

        # Get objects in current render layer
        currentRenderLayer = cmds.editRenderLayerGlobals( query=True, currentRenderLayer=True )
        objectList = cmds.listConnections( currentRenderLayer, source=0, destination=1 );

        # Get a filtered list from the children
        # Always use fullPath=True to avoid short name conflict errors
        meshNodes = cmds.listRelatives(objectList, allDescendents=True, noIntermediate=True, fullPath=True, type="mesh") 
        attributes = parseVrayUserAttributes(meshNodes);

        toggleRenderElements(attributes);

        return 0;



    ####################################################################################################
    # cbVerboseMode()
    # Helper function that activates on checking/unchecking "Verbose" check box
    ####################################################################################################  
    def cbVerboseMode(self, state):
        if state == 0:
            print "\n"
            print "\nExiting Verbose Mode..."
            print "##################################################\n";
        else:
            print "##################################################";
            print "Entering Verbose Mode...\n"



    ####################################################################################################
    # loadLights()
    # 
    #################################################################################################### 
    def loadLights(self):

        # Clear the listWidget for good measure
        self.listWidget.clear()

        # Select all shape nodes in the scene
        geometry = cmds.ls( geometry=True )
        shapes = cmds.listRelatives( geometry, p=True, path=True )
        allAttributes = parseVrayUserAttributes( shapes )


        # Get objects in current render layer
        currentRenderLayer = cmds.editRenderLayerGlobals( query=True, currentRenderLayer=True )
        objectList = cmds.listConnections( currentRenderLayer, source=0, destination=1 );


        # Get a filtered list from the children
        # Always use fullPath=True to avoid short name conflict errors
        meshNodes = cmds.listRelatives( objectList, allDescendents=True, noIntermediate=True, fullPath=True, type="mesh" ) 
        attributes = parseVrayUserAttributes( meshNodes );


        for attribute in attributes:
            #if light.nodeType() == "VRayLightRectShape" or light.nodeType() == "VRayLightDomeShape":

            # Create List Widget Item for each attribute
            item = QListWidgetItem( "%s" %attribute )
            item.setFlags( Qt.ItemIsUserCheckable | Qt.ItemIsEnabled )


            item.setCheckState( Qt.Unchecked ) 
            self.listWidget.addItem( item )
            size = QSize()
            size.setHeight( 20 )
            item.setSizeHint( size )


    ####################################################################################################
    # closeEvent()
    # 
    ####################################################################################################  
    def closeEvent(self, event):
        if self.verboseCB.isChecked():
            print "vrayMatteTagsUI Window Closed."
            print "##################################################\n\n";



####################################################################################################
# convertAttributeListToString()
# 
####################################################################################################  
def convertAttributeListToString(attributeList):
    attributeString = ''

    if not attributeList:
        print "convertAttributeListToString:  No attributes given. Returning empty attribute string."
        return attributeString;

    for attribute in attributeList:
        attributeString = attributeString + attribute + '=1;'

    return attributeString;



####################################################################################################
# convertAttributeStringToList()
# 
####################################################################################################
def convertAttributeStringToList(attributeString):

    if not attributeString:
        #print "convertAttributeStringToList:  No attributes string given. Returning empty attributeList."
        return [];

    tokenizedList = [];
    tokenizedList = attributeString.split(';')

    # Removes empty items from list (Usually caused by terminating ";" in vrayUserAttribute List)
    tokenizedList = filter(None, tokenizedList)

    # Strips "=1" from each vrayUserAttribute
    strippedList = [];
    for str in tokenizedList:
        strippedStr = str.split('=')[0]
        strippedList.append(strippedStr)

    return strippedList;



####################################################################################################
# convertDirtyInputStringToList()
# Similar to convertAttributeStringtoList() but with significantly more error checking to account
# for human error.
####################################################################################################  
def convertDirtyInputStringToList(inputString):

    if not inputString:
        print "convertDirtyInputStringToList:  No input string given. Returning empty attributeList."
        return [];

    tokenizedList = [];

    # Removes spaces in inputString for cleaner tokenizing
    inputString = inputString.replace(' ','')

    if ',' in inputString:
        tokenizedList = inputString.split(',')
    elif ';' in inputString:
        tokenizedList = inputString.split(';')
    else:
        tokenizedList.append(inputString)

    # Removes empty items from list (Usually caused by terminating ";" in vrayUserAttribute List)
    tokenizedList = filter(None, tokenizedList)

    # Strips "=1" from each vrayUserAttribute
    strippedList = [];
    for str in tokenizedList:
        strippedStr = str.split('=')[0]
        strippedList.append(strippedStr)

    return strippedList;



####################################################################################################
# addVrayUserAttributes()
# adds vrayUserAttributes to selected object if it does not already exist.
####################################################################################################  
def addVrayUserAttributes(node):

    if not cmds.objExists('%s.vrayUserAttributes' %node):
        cmds.vray("addAttributesFromGroup", node, "vray_user_attributes", 1)

    return 0;



####################################################################################################
# parseVrayUserAttributes()
# Generates a list of all vrayUserAttributes found on a provided list of nodes
####################################################################################################
def parseVrayUserAttributes(nodeList):
    allAttributes = []
    count = 0

    if not nodeList:
        print "parseVrayUserAttributes:  No nodes selected. Returning empty attribute list."
        return allAttributes;

    # For each node selected...
    for node in nodeList:
        attributeList = []

        if cmds.objExists('%s.vrayUserAttributes' %node):
            attributeString = cmds.getAttr('%s.vrayUserAttributes' %node)
            attributeList = convertAttributeStringToList(attributeString)

        for attr in attributeList:
            if attr not in allAttributes: # Keeping this list shorter will mean we don't need to check for duplicates later and be faster
                allAttributes.append(attr)
                count = count + 1;

    # Remove duplicate vrayUserAttributes from list (There will be a lot!) // lol no
    allAttributes = removeDuplicates(allAttributes)

    return allAttributes;



####################################################################################################
# getVrayUserAttributes()
# 
####################################################################################################  
def getVrayUserAttributes(node):
    attributeList = []
    attributeString = ''

    if not node:
        print "getVrayUserAttributes:  No nodes given. Returning empty attributeList."

    if cmds.objExists('%s.vrayUserAttributes' %node) and cmds.getAttr('%s.vrayUserAttributes' %node):
        attributeString = cmds.getAttr('%s.vrayUserAttributes' %node);

    attributeList = convertAttributeStringToList(attributeString)

    return attributeList;



####################################################################################################
# setVrayUserAttributes()
# Formats and sets vrayUserAttributes of an object given an attributeList of matte assigments.
####################################################################################################  
def setVrayUserAttributes(node, attributeList):
    attributeString = convertAttributeListToString(attributeList);

    if not node:
        print "setVrayUserAttributes:  No node given."
        return;

    if not cmds.objExists('%s.vrayUserAttributes' %node):
        addVrayUserAttributes(node);

    if not attributeString:
        print "setVrayUserAttributes:  No attributes given. Not updating vrayUserAttributes."
        return;

    cmds.setAttr(('%s.vrayUserAttributes' %node), attributeString, type='string');

    return 0;


####################################################################################################
# selectByVrayUserAttribute()
#
#################################################################################################### 

def selectByVrayUserAttributes(tags):

    geometry = cmds.ls(geometry=True, sl=True)

    if not geometry:
        geometry = cmds.ls(geometry=True)

    shapes = cmds.listRelatives(geometry, p=True, path=True)

    selectList = []

    if shapes:
        for shape in shapes:
            if cmds.objExists('%s.vrayUserAttributes' %shape):
                attributeString = str(cmds.getAttr('%s.vrayUserAttributes' %shape))
                allTags = True
                if tags:
                    for tag in tags:
                        print "Comparing: " + tag + " to: " + attributeString
                        if '=' not in tag:
                            tag = tag + '='
                        if tag not in attributeString:
                            allTags = False
                else:
                    allTags = False
                if allTags:
                    selectList.append(shape)

    cmds.select(selectList)


####################################################################################################
# createRenderElements()
# Creates Render Elements and User Color nodes given a supplied list of attributes
####################################################################################################  
def createRenderElements(attributeList):

    if not attributeList:
        print "createRenderElements: No attributes given. No render elements created."
        return

    cBlack = 0;


    # Create maya set for easy selection and destruction of vrayMatteTags
    if not cmds.objExists( 'vrayMatteTagSet' ):     cmds.sets( n='vrayMatteTagSet', em=True )
    if not cmds.objExists( 'vrayMatteTagUCSet' ):   cmds.sets( n='vrayMatteTagUCSet', em=True )
    if not cmds.objExists( 'vrayMatteTagRESet' ):   cmds.sets( n='vrayMatteTagRESet', em=True )
    cmds.sets('vrayMatteTagUCSet', add='vrayMatteTagSet')
    cmds.sets('vrayMatteTagRESet', add='vrayMatteTagSet')


    # Create render elements for all attributes in attributeList
    for attribute in attributeList:
        matteName = ('m_%s' %attribute)

        if not cmds.objExists(matteName):

            # Create Vray User Color Node to link tags with their respective Render Element
            userColor = mel.eval( 'shadingNode -asUtility VRayUserColor;' )
            cmds.setAttr(userColor + '.userAttribute', '%s' %attribute, type = 'string')
            cmds.setAttr(userColor + '.color', 0.0, 0.0, 0.0, type = 'double3')

            # Create Vray Render Element
            renderElement = mel.eval( 'vrayAddRenderElement ExtraTexElement;' )
            cmds.setAttr( '%s.vray_explicit_name_extratex' %renderElement, matteName, type = 'string')
            cmds.setAttr( '%s.enabled' %renderElement, 0 );

            # Connect User Color to Render Element
            cmds.connectAttr( '%s.outColor' %userColor ,'%s.vray_texture_extratex' %renderElement );

            cmds.sets( userColor, add='vrayMatteTagUCSet' )
            cmds.sets( renderElement, add='vrayMatteTagRESet' )

            # Rename both nodes now that connections have been made
            cmds.rename(renderElement, matteName);
            cmds.rename(userColor, 'uc_%s' %attribute);



####################################################################################################
# toggleRenderElements()
# Toggles the vrayRenderElements for a provided (tokenized) list of attributes
####################################################################################################
def toggleRenderElements(attributeList):

    for attr in attributeList:
        renderElement = 'm_' + attr;

        if cmds.objExists(renderElement):
            cmds.editRenderLayerAdjustment( '%s.enabled' %renderElement );
            cmds.setAttr( '%s.enabled' %renderElement, 1 );
        else:
            print("toggleRenderElements:  vrayRenderElement: %s does not exist." %renderElement)

    return 0;



####################################################################################################
# getCurrentLayerVrayMatteTagRE()
# Same functionality as btnToggleRenderElements, but instead of toggling render elements returns an 
# attributeList of render elements to be used for ESPN CFB sort controller.
####################################################################################################
def getCurrentLayerVrayMatteTagRE():

    # Get objects in current render layer
    currentRenderLayer = cmds.editRenderLayerGlobals( query=True, currentRenderLayer=True )
    objectList = cmds.listConnections( currentRenderLayer, source=0, destination=1 );

    # Get a filtered list from the children
    # Always use fullPath=True to avoid short name conflict errors
    meshNodes = cmds.listRelatives(objectList, allDescendents=True, noIntermediate=True, fullPath=True, type="mesh") 
    attributes = parseVrayUserAttributes(meshNodes);

    return attributes;


####################################################################################################
# removeDuplicates()
# Removes duplicate entries in a given list WITHOUT reordering the elements
#################################################################################################### 
def removeDuplicates(myList):
    output = []
    seen = set()
    for value in myList:
        if value not in seen:
            output.append(value)
            seen.add(value)

    return output;



####################################################################################################
# main()
#
#################################################################################################### 
def main(*a):

    # Tries to close the window if it exists before creating a new window
    try:
        ui.close()
    except:
        pass

    ui = vrayMatteTagsUI();

    return ui


if __name__ == "__main__":
    main()