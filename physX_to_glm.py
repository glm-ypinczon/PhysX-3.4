#**********************************************************************
#
# Launchers
#
#**********************************************************************
import sys
import os
import string
import xml.etree.ElementTree as ET

#------------------------------------------------------------------
def addOrChangeXMLTagInFile(fullFilePath, XMLcontainerTag, XMLTag, value):
    openedOutputFile = False

    #print("Reading XML file: {}").format(fullFilePath)
    srcFile = open(fullFilePath, 'r')
    fileAsText = srcFile.read()
    srcFile.close()

    currentSrcPos = 0
    nextSrcPos = len(fileAsText)

    #search the parent XMLTag...
    parentXmlBeginTagPos = string.find(fileAsText, "<{}>".format(XMLcontainerTag))
    parentXmlEndTagEndPos = string.find(fileAsText, "</{}>".format(XMLcontainerTag), parentXmlBeginTagPos+1)
    while parentXmlBeginTagPos>=0 and parentXmlEndTagEndPos>=0 and (parentXmlEndTagEndPos-parentXmlBeginTagPos)>0:
        #now search the XMLTag...
        xmlBeginTagPos = string.find(fileAsText, "<{}>".format(XMLTag), parentXmlBeginTagPos, parentXmlEndTagEndPos)
        xmlEndTagEndPos = string.find(fileAsText, "</{}>".format(XMLTag), xmlBeginTagPos+1, parentXmlEndTagEndPos)
        #check the current tag value...
        xmlTagValue = fileAsText[xmlBeginTagPos+len(XMLTag)+2:xmlEndTagEndPos]
        if(xmlTagValue!=value):
            if xmlBeginTagPos<0 or xmlEndTagEndPos<0:
                xmlBeginTagPos = parentXmlEndTagEndPos-1
                xmlEndTagEndPos = xmlBeginTagPos
            else:
                xmlEndTagEndPos = xmlEndTagEndPos+len(XMLTag)+3
       
            if(not openedOutputFile):
                openedOutputFile = True
                #print("Writing XML file: {}").format(fullFilePath)
                dstFile = open(fullFilePath, 'w')
            #write file
            nextSrcPos = xmlBeginTagPos-1
            nextFilePart = fileAsText[currentSrcPos:nextSrcPos]
            dstFile.write(nextFilePart)
            currentSrcPos = xmlEndTagEndPos
            #write tag
            dstFile.write("\n<{}>{}</{}>\n".format(XMLTag, value, XMLTag))

        #search the NEXT parent XMLTag...
        parentXmlBeginTagPos = string.find(fileAsText, "<{}>".format(XMLcontainerTag), parentXmlEndTagEndPos+1)
        parentXmlEndTagEndPos = string.find(fileAsText, "</{}>".format(XMLcontainerTag), parentXmlBeginTagPos+1)


    #write the end of file
    if(openedOutputFile):
        nextFilePart = fileAsText[currentSrcPos:]
        dstFile.write(nextFilePart)
        dstFile.close()

    return openedOutputFile

#------------------------------------------------------------------
def replaceTextInFile(fullFilePath, textToReplace, textReplacement):
    openedOutputFile = False
    replacementCount = 0

    #print("Reading file: {}").format(fullFilePath)
    srcFile = open(fullFilePath, 'r')
    fileAsText = srcFile.read()
    srcFile.close()

    textOffset = len(textToReplace)
    currentSrcPos = 0
    nextSrcPos = string.find(fileAsText, textToReplace, currentSrcPos)
    while(nextSrcPos>=0):
        #check if it's not already the replacement text...
        checkNextSrcPos = string.find(fileAsText, textReplacement, nextSrcPos-len(textReplacement))
        if checkNextSrcPos>=0 and abs(checkNextSrcPos-nextSrcPos)<=abs(len(textToReplace)-len(textReplacement)):
            nextSrcPos = string.find(fileAsText, textToReplace, nextSrcPos+1)
            continue

        if(not openedOutputFile):
            openedOutputFile = True
            #print("Writing file: {}").format(fullFilePath)
            dstFile = open(fullFilePath, 'w')
   
        nextFilePart = fileAsText[currentSrcPos:nextSrcPos]
        dstFile.write(nextFilePart)
        dstFile.write(textReplacement)
        replacementCount=replacementCount+1  

        currentSrcPos = nextSrcPos+textOffset
        nextSrcPos = string.find(fileAsText, textToReplace, currentSrcPos)

    #write the end of file
    if(openedOutputFile):
        nextFilePart = fileAsText[currentSrcPos:]
        dstFile.write(nextFilePart)
        dstFile.close()

    return replacementCount

#------------------------------------------------------------------
def addMethodAtEndOfSourceFile(fullFilePath, namespace, methodText):
    return addTextAtEndOfSection(fullFilePath, "namespace", namespace, '{', '}', methodText, False)

#------------------------------------------------------------------
def addMethodDeclarationInHeader(fullFilePath, className, methodDeclarationText):
    return addTextAtEndOfSection(fullFilePath, "class", className, '{', '}', methodDeclarationText, True)

#------------------------------------------------------------------
def addTextAtEndOfSection(fullFilePath, sectionName, sectionValue, sectionStartSymbol, sectionEndSymbol, textToAdd, usePublicSubSection):
    srcFile = open(fullFilePath, 'r')
    fileAsText = srcFile.read()
    srcFile.close()

    #check if the text was already added...
    alreadyThere = string.find(fileAsText, textToAdd)
    if alreadyThere>=0:
        return False

    #find the begin and end brackets of the class...
    classPos = string.find(fileAsText, "{} {}".format(sectionName, sectionValue))
    if(classPos<=0):
        print "Error: Could not find the {} {} in {}".format(sectionName, sectionValue, fullFilePath)
        return False
    currentSrcPos = classPos+6+len(sectionStartSymbol)

    classBeginBracketPos = string.find(fileAsText, sectionStartSymbol, currentSrcPos)
    classEndBracketPos = -1
    if(classBeginBracketPos<=0):
        return False
    currentSrcPos = classBeginBracketPos+1
    currentBracketLevel=1
    while(currentBracketLevel>0 and currentSrcPos<len(fileAsText)):
        nextOpeningBracketPos = string.find(fileAsText, sectionStartSymbol, currentSrcPos)
        nextClosingBracketPos = string.find(fileAsText, sectionEndSymbol, currentSrcPos)
        if(nextClosingBracketPos<=0):
            print "Error: Mismatch in opening and closing {} {} in {}".format(sectionName, sectionValue, fullFilePath)
            return False
        if(nextOpeningBracketPos>=0 and nextOpeningBracketPos<nextClosingBracketPos):
            currentBracketLevel+=1
            currentSrcPos=nextOpeningBracketPos+1
        else:
            currentBracketLevel-=1
            currentSrcPos=nextClosingBracketPos+1

    if(currentBracketLevel!=0):
        print "Error: Could not locate the {} {} closing symbol in {}".format(sectionName, sectionValue, fullFilePath)
        return False

    classEndBracketPos = nextClosingBracketPos

    #now find the end of the public part of the class
    publicPartPos = string.find(fileAsText, 'public:', classBeginBracketPos, classEndBracketPos)
    endOfPublicPartPos = classEndBracketPos
    if(usePublicSubSection):
        if(publicPartPos>=0):
            nextPartPos = string.find(fileAsText, 'protected:', publicPartPos, classEndBracketPos)
            if(nextPartPos>=0 and nextPartPos<endOfPublicPartPos):
                endOfPublicPartPos=nextPartPos
            nextPartPos = string.find(fileAsText, 'private:', publicPartPos, classEndBracketPos)
            if(nextPartPos>=0 and nextPartPos<endOfPublicPartPos):
                endOfPublicPartPos=nextPartPos

    #now finally write the file down with the added declaration text
    dstFile = open(fullFilePath, 'w')
    #write file
    dstFile.write(fileAsText[:endOfPublicPartPos])
    dstFile.write("\n")
    if(usePublicSubSection and publicPartPos<0):
        dstFile.write("public:\n")
    dstFile.write(textToAdd)
    dstFile.write("\n")
    dstFile.write(fileAsText[endOfPublicPartPos:])
    dstFile.close()

    return True


#**********************************************************************
#
# PhysXToGlmConverter
#
#**********************************************************************
class PhysXToGlmConverter():
    #------------------------------------------------------------------
    # Constructor
    #------------------------------------------------------------------
    def __init__(self):
        # Configuration Data Members
        self.ignoreDirectories = {".git", ".vs", "Documentation", "build", "Media"}
        self.physXLibraries = {}
        self.apexLibraries = {}
        self.targetList  = {}
        self.processorsList  = {}
        # statistics data members
        self.projectFilesChanged = 0
        self.MDOptionReplaced = 0
        self.MDdOptionReplaced = 0
        self.IgnoreDefaultLibAdded = 0

        self.srcFilesChanged = 0
        self.namespacesReplaced = 0
        self.missingNamespacesFixed = 0
        self.glmPostFixAdded = 0
        self.glmPreFixAdded = 0
        self.classMethodsAdded = 0


    #******************************************************************
    # UI Accessors
    #******************************************************************

    #------------------------------------------------------------------
    def parseProjectFile(self, file, path):
        fullFilePath = "{}\\{}".format(path, file)

        currentTotalReplacements = self.MDOptionReplaced + self.MDdOptionReplaced + self.IgnoreDefaultLibAdded + self.glmPostFixAdded + self.glmPreFixAdded 

        # set MDd and MD options
        self.MDOptionReplaced += replaceTextInFile(fullFilePath, "<RuntimeLibrary>MultiThreaded</RuntimeLibrary>", "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>")
        self.MDdOptionReplaced += replaceTextInFile(fullFilePath, "<RuntimeLibrary>MultiThreadedDebug</RuntimeLibrary>", "<RuntimeLibrary>MultiThreadedDebugDLL</RuntimeLibrary>")

        #set ignore default lib XML tag
        self.IgnoreDefaultLibAdded += addOrChangeXMLTagInFile(fullFilePath, "Lib", "IgnoreSpecificDefaultLibraries", "LIBCMT")
        self.IgnoreDefaultLibAdded += addOrChangeXMLTagInFile(fullFilePath, "Link", "IgnoreSpecificDefaultLibraries", "LIBCMT")

        # prefix PhysX libraries
        for physXLibrary in self.physXLibraries:
            for target in self.targetList:
                for processor in self.processorsList:
                    textToReplace = "{}{}{}".format(physXLibrary, target, processor)
                    textReplacement = "glm_{}{}{}".format(physXLibrary, target, processor)
                    self.glmPreFixAdded += replaceTextInFile(fullFilePath, textToReplace, textReplacement)

        # postfix Apex libraries
        for apexLibrary in self.apexLibraries:
            for target in self.targetList:
                for processor in self.processorsList:
                    #in the library vcproj
                    if(string.find(file, apexLibrary)>=0):
                        textToReplace = "(ProjectName){}{}".format(target, processor)
                        textReplacement = "(ProjectName){}{}_glm".format(target, processor)
                        self.glmPostFixAdded += replaceTextInFile(fullFilePath, textToReplace, textReplacement)
                    #in other vcproj
                    textToReplace = "{}{}{}".format(apexLibrary, target, processor)
                    textReplacement = "{}{}{}_glm".format(apexLibrary, target, processor)
                    self.glmPostFixAdded += replaceTextInFile(fullFilePath, textToReplace, textReplacement)
        
        newTotalReplacements = self.MDOptionReplaced + self.MDdOptionReplaced + self.IgnoreDefaultLibAdded + self.glmPostFixAdded + self.glmPreFixAdded
        return newTotalReplacements>currentTotalReplacements


    #------------------------------------------------------------------
    def parseSourceFile(self, file, path):
        fullFilePath = "{}\\{}".format(path, file)

        namespaceReplacedCount=0
        namespaceFixedCount=0
        methodAdded = 0

        # if changing the physx namespace into glm_physx, it's not possible to use GPU acceleration anymore.
        #namespaceReplacedCount = replaceTextInFile(fullFilePath, "physx::", "glm_physx::")
        #namespaceReplacedCount += replaceTextInFile(fullFilePath, "namespace physx", "namespace glm_physx")

        namespaceFixedCount += replaceTextInFile(fullFilePath, " Array<", " physx::shdfnd::Array<")
        namespaceFixedCount += replaceTextInFile(fullFilePath, "(Array<", "(physx::shdfnd::Array<")
        namespaceFixedCount += replaceTextInFile(fullFilePath, "	Array<", "	physx::shdfnd::Array<")
        #Mutex replacement does not work properly in all files, lets just do it in files where it's needed...
        if file=="ApexScene.h":
            namespaceFixedCount += replaceTextInFile(fullFilePath, "	Mutex ", "	physx::shdfnd::Mutex ")
            namespaceFixedCount += replaceTextInFile(fullFilePath, "	Mutex	", "	physx::shdfnd::Mutex	")

        if(file=="ClothingAsset.h"):
            methodDeclaration = "\
\n\
\n	//---------------------------------------------------------------------------------\
\n	// Glm added accessors\
\n	//---------------------------------------------------------------------------------\
\n	virtual PxU32           getPhysicalMeshVertexCount(PxU32 graphicalLodId) const = 0;\
\n	virtual const PxVec3*   getPhysicalMeshVertexBuffer(PxU32 graphicalLodId) const = 0;\
\n\
\n	virtual PxU32           getPhysicalMeshIndexCount(PxU32 graphicalLodId) const = 0;\
\n	virtual const PxU16*    getPhysicalMeshIndexBuffer(PxU32 graphicalLodId) const = 0;\
\n\
\n	virtual PxU32           getGraphicalMeshVertexCount(PxU32 graphicalLodId, PxU32 submeshIndex) const = 0;\
\n	virtual void            getGraphicalMeshVertexBuffer(PxVec3* dstBuffer, PxU32 dstBufferSize, PxU32 graphicalLodId, PxU32 submeshIndex) const = 0;\
\n	//---------------------------------------------------------------------------------\
\n\
"
            methodAdded = addMethodDeclarationInHeader(fullFilePath, "ClothingAsset", methodDeclaration)
        elif(file=="ClothingAssetImpl.h"):
            methodDeclaration = "\
\n\
\n	//---------------------------------------------------------------------------------\
\n	// Glm added accessors\
\n	//---------------------------------------------------------------------------------\
\n	PxU32                   getPhysicalMeshVertexCount(PxU32 graphicalLodId) const;\
\n	const PxVec3*           getPhysicalMeshVertexBuffer(PxU32 graphicalLodId) const;\
\n\
\n	PxU32                   getPhysicalMeshIndexCount(PxU32 graphicalLodId) const;\
\n	const PxU16*            getPhysicalMeshIndexBuffer(PxU32 graphicalLodId) const;\
\n\
\n	PxU32                   getGraphicalMeshVertexCount(PxU32 graphicalLodId, PxU32 submeshIndex) const;\
\n	void                    getGraphicalMeshVertexBuffer(PxVec3* dstBuffer, PxU32 dstBufferSize, PxU32 graphicalLodId, PxU32 submeshIndex) const;\
\n	//---------------------------------------------------------------------------------\
\n\
"
            methodAdded = addMethodDeclarationInHeader(fullFilePath, "ClothingAssetImpl", methodDeclaration)
        elif(file=="ClothingAssetImpl.cpp"):
            methodText = "\
\n\
\n//---------------------------------------------------------------------------------\
\n// Glm added accessor\
\n//---------------------------------------------------------------------------------\
\nPxU32 ClothingAssetImpl::getPhysicalMeshVertexCount(PxU32 graphicalLodId) const\
\n{\
\n	ClothingPhysicalMeshParametersNS::PhysicalMesh_Type* pmesh = getPhysicalMeshFromLod(graphicalLodId);\
\n	return pmesh->numVertices;\
\n}\
\nconst PxVec3* ClothingAssetImpl::getPhysicalMeshVertexBuffer(PxU32 graphicalLodId) const\
\n{\
\n	ClothingPhysicalMeshParametersNS::PhysicalMesh_Type* pmesh = getPhysicalMeshFromLod(graphicalLodId);\
\n	return pmesh->vertices.buf;\
\n}\
\nPxU32 ClothingAssetImpl::getPhysicalMeshIndexCount(PxU32 graphicalLodId) const\
\n{\
\n	ClothingPhysicalMeshParametersNS::PhysicalMesh_Type* pmesh = getPhysicalMeshFromLod(graphicalLodId);\
\n	return pmesh->numIndices;\
\n}\
\nconst PxU16* ClothingAssetImpl::getPhysicalMeshIndexBuffer(PxU32 graphicalLodId) const\
\n{\
\n	ClothingPhysicalMeshParametersNS::PhysicalMesh_Type* pmesh = getPhysicalMeshFromLod(graphicalLodId);\
\n	return pmesh->boneIndices.buf;\
\n}\
\nPxU32 ClothingAssetImpl::getGraphicalMeshVertexCount(PxU32 graphicalLodId, PxU32 submeshIndex) const\
\n{\
\n	const RenderMeshAssetIntl* renderMeshAsset = const_cast<ClothingAssetImpl*>(this)->getGraphicalMesh(graphicalLodId);\
\n	if (submeshIndex >= renderMeshAsset->getSubmeshCount())\
\n		return 0;\
\n\
\n	const RenderSubmesh& subMesh = renderMeshAsset->getSubmesh(submeshIndex);\
\n	return subMesh.getVertexBuffer().getVertexCount();\
\n}\
\nvoid ClothingAssetImpl::getGraphicalMeshVertexBuffer(PxVec3* dstBuffer, PxU32 dstBufferSize, PxU32 graphicalLodId, PxU32 submeshIndex) const\
\n{\
\n	const RenderMeshAssetIntl* renderMeshAsset = const_cast<ClothingAssetImpl*>(this)->getGraphicalMesh(graphicalLodId);\
\n	if (submeshIndex >= renderMeshAsset->getSubmeshCount())\
\n		return;\
\n\
\n	const RenderSubmesh& subMesh = renderMeshAsset->getSubmesh(submeshIndex);\
\n\
\n	subMesh.getVertexBuffer().getBufferData(dstBuffer, nvidia::apex::RenderDataFormat::FLOAT3, 0, 0,\
\n		0, (dstBufferSize <= subMesh.getVertexBuffer().getVertexCount() ? dstBufferSize : subMesh.getVertexBuffer().getVertexCount()));\
\n}\
\n//---------------------------------------------------------------------------------\
\n\
"
            methodAdded = addMethodAtEndOfSourceFile(fullFilePath, "clothing", methodText)


        self.namespacesReplaced += namespaceReplacedCount
        self.missingNamespacesFixed += namespaceFixedCount
        self.classMethodsAdded += methodAdded
        return (namespaceReplacedCount+namespaceFixedCount+methodAdded)>0


    #------------------------------------------------------------------
    def do(self, rootDir, printParsedFiles):
        for root, dirs, files in os.walk(rootDir):
            ignore = False
            for ignoreDir in self.ignoreDirectories:
                if(string.find(root, ignoreDir)>=0):
                    ignore = True
                    continue

            if(ignore):
                if(printParsedFiles==True):
                    print("\nIgnoring {} ...").format(root)
                while len(dirs)>0:
                    dirs.pop()
                continue

            if(printParsedFiles==True):
                print("\nParsing {} file(s) in {} ...").format(len(files), root)
            for file in files:
                isFileModified = False

                if(string.find(file, ".cpp")>=0 or string.find(file, ".h")>=0 or string.find(file, ".inl")>=0):
                    isFileModified = self.parseSourceFile(file, root)
                    if(isFileModified):
                        self.srcFilesChanged+=1
                elif(string.find(file, ".vcxproj")>=0):
                    isFileModified = self.parseProjectFile(file, root)
                    if(isFileModified):
                        self.projectFilesChanged += 1
                else:
                    if(printParsedFiles==True):
                        print("Ignoring file: {}").format(file)
                    continue

                if(printParsedFiles==True):
                    if(isFileModified):
                        print("Writing in {}").format(file)
                    elif(printParsedFiles==True):
                         print("Reading file: {}").format(file)

        print("\nDone.")

    #------------------------------------------------------------------
    def printStats(self):
        print("\nMade replacement in {} project files:\n     -{} /MT changed into /MD\n     -{} /MTd changed into /MDd\n     -{} ignore lib added\n     -{} _glm postfix added\n     -{} glm_ prefix added".format(self.projectFilesChanged, self.MDOptionReplaced, self.MDdOptionReplaced, self.IgnoreDefaultLibAdded, self.glmPostFixAdded, self.glmPreFixAdded))
        print("\nMade replacement in {} source files:\n     -{} physx namespace changed into glm_physx\n     -{} missing physx namespace fixed\n     -{} code addition".format(self.srcFilesChanged, self.namespacesReplaced, self.missingNamespacesFixed, self.classMethodsAdded))



def main():
    p = os.path._getfullpathname(".")

    converter = PhysXToGlmConverter()
    converter.ignoreDirectories = {".git", "External", "external", "Documentation", ".vs", "build", "Lib", "Media"}
    converter.physXLibraries = {"PhysX3", "PhysX3CharacterKinematic", "PhysX3Common", "PhysX3Cooking", "PxPvdSDK", "PxFoundation", "PhysX3Gpu"}
    converter.apexLibraries = {"APEX_Clothing", "APEX_Destructible", "ApexFramework", "APEX_Legacy"}
    converter.targetList = {"", "DEBUG", "CHECKED", "PROFILE"}
    converter.processorsList = {"_X86", "_x86", "_X64", "_x64"}

    converter.do(p, True)
    converter.printStats()             

if __name__ == '__main__':
    main()
    exit()
