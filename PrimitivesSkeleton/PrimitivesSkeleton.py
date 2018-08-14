'''
Tool allows to convert the skeleton or a set of joints to set sphere and cone primitives   
'''
import maya.cmds as mc

def makePrimitiveJoint(currentJoint):    
    SJsize = mc.jointDisplayScale(q=True) * SS_scale
    children = mc.listRelatives(currentJoint, c=True)    
    if (children != None) : 
        for node in children :
            if(mc.nodeType(node) == "joint") :
                makePrimitiveJoint(node)
            else :
                SJballEndName = currentJoint + SS_group + "_SJballEnd"        
                solidEndBall = mc.sphere(n=SJballEndName)
                mc.parent(solidEndBall, SS_group)                
                mc.scale(SJsize, SJsize, SJsize, solidEndBall, r=True)
                mc.pointConstraint(currentJoint, solidEndBall, weight=1)
                createMDN(solidEndBall, 'ball')
    elif (children == None) :
        SJballEndName = currentJoint + SS_group + "_SJballEnd"        
        solidEndBall = mc.sphere(n=SJballEndName)
        mc.parent(solidEndBall, SS_group)        
        mc.scale(SJsize, SJsize, SJsize, solidEndBall, r=True)
        mc.pointConstraint(currentJoint, solidEndBall, weight=1)
        createMDN(solidEndBall, 'ball')
    SJname = currentJoint + SS_group + "_SJ"
    SJballName = currentJoint + SS_group + "_SJball"
    parent = mc.listRelatives(currentJoint, p=True)
    if (parent != None) and (currentJoint != SS_root_jnt):
        parentJoint = parent[0]
        solidBall = mc.sphere(n=SJballName)
        solidJoint = mc.cone(p=(0,0,0), ax=(1,0,0), ssw=0, esw=360, r=0.5,
                                 hr=4, d=1, ut=0, tol=0.01, s=8, nsp=4, ch=1,
                                 n=SJname)
        mc.move(-1, 0, 0, SJname+".scalePivot", SJname+".rotatePivot", r=True)
        mc.parent(solidJoint, SS_group)
        mc.parent(solidBall, SS_group)        
        xform1 = mc.xform(currentJoint, q=True, ws=True, t=True)
        xform2 = mc.xform(parentJoint, q=True, ws=True, t=True)
        dist = 0.0
        for i in range(len(xform1)):dist += (xform1[i]-xform2[i])*(xform1[i]-xform2[i])        
        dist = (dist ** 0.5) / 2.0
        mc.scale(SJsize, SJsize, SJsize, solidBall, r=True)        
        bbox = mc.exactWorldBoundingBox(solidBall)
        bboxSize = ((((bbox[3]-bbox[0])**2+(bbox[4]-bbox[1])**2+(bbox[5]-bbox[2])**2)**0.5)/4.0)*SS_edgeScale
        mc.scale(dist, bboxSize, bboxSize, solidJoint, r=True)        
        mc.pointConstraint(parentJoint, solidJoint, weight=1)
        mc.pointConstraint(parentJoint, solidBall, weight=1)
        mc.aimConstraint(currentJoint, solidJoint, aim=(1,0,0), u=(0,1,0), wu=(0,1,0), weight=1)
        createMDN(solidBall, 'ball')
        createMDN(solidJoint, 'edge')
       
def createMDN(objName, objType) :           
    if(objType == 'ball') :
        SS_multiply = objName[0] + SS_group + "_ballMultiply"
        mc.createNode('multiplyDivide', n=SS_multiply)
        mc.setAttr(SS_multiply + ".input1X", 1)
        mc.setAttr(SS_multiply + ".input2X", mc.getAttr(objName[0]+'.scaleX'), lock=True)
        mc.connectAttr(SS_multiply+'.outputX', objName[0]+'.scaleX')
        mc.connectAttr(SS_multiply+'.outputX', objName[0]+'.scaleY')
        mc.connectAttr(SS_multiply+'.outputX', objName[0]+'.scaleZ')
    elif(objType == 'edge') :
        SS_multiply = objName[0] + SS_group + "_edgeMultiply"        
        coneShapeNode = mc.listConnections( objName[0]+'Shape', s=True, d=False)
        mc.createNode('multiplyDivide', n=SS_multiply)
        mc.setAttr(SS_multiply + ".input1X", 1)
        mc.setAttr(SS_multiply + ".input2X", mc.getAttr(objName[0]+'.scaleY'), lock=True)
        mc.setAttr(SS_multiply + ".input1Z", 8)
        mc.setAttr(SS_multiply + ".input2Z", 1, lock=True)
        mc.connectAttr(SS_multiply+'.outputX', objName[0]+'.scaleY')
        mc.connectAttr(SS_multiply+'.outputX', objName[0]+'.scaleZ')        
        mc.connectAttr(SS_multiply+'.outputZ', coneShapeNode[0]+'.sections') 

class PrimitiveSkeletonUI() :
    def __init__(self, winName = "PrimitiveSkeletonUI") :
        self.winTitle = "Primitive Skeleton"
        self.winName = winName
        self.SS_MDNlist = []    
        
    def makeSS(self, arg=None):        
        self.makePrimitiveSkeleton()
        return
    
    def doNothing(self, arg=None):
        return
    
    def changeBallScale(self, arg=None):
        ballSize = mc.floatSliderGrp(self.ballSizeSlider, q=True, value=True)
        mc.setAttr(SS_scaleCtr+".input1X", ballSize)
        return
    
    def changeEdgeScale(self, arg=None):
        edgeSize = mc.floatSliderGrp(self.edgeSizeSlider, q=True, value=True)
        mc.setAttr(SS_scaleCtr+".input1Y", edgeSize)
        return
    
    def changeEdgeDivide(self, arg=None):
        edgeDivide = mc.intSliderGrp(self.edgeDivideSlider, q=True, value=True)
        mc.setAttr(SS_scaleCtr+".input1Z", edgeDivide)
        return

    def makePrimitiveSkeleton(self, ballScale=1.0, edgeScale=1.0) :        
        global SS_group
        global SS_root_jnt
        global SS_scale
        global SS_edgeScale
        global SS_scaleCtr
        #global SS_MDNlist
        selection = mc.ls(sl=True)
        
        templist = self.SS_MDNlist
       
        if len(self.SS_MDNlist)==0 : print "SS_MDNlist length  0! "
        
        SS_scale = ballScale
        SS_edgeScale = edgeScale      
        if len(mc.ls("PrimitiveSkeleton")) != 0 :              
            SS_group = "PrimitiveSkeleton"
        else :            
            SS_group = mc.group(empty=True, name="PrimitiveSkeleton")
            del self.SS_MDNlist
            self.SS_MDNlist = []
        SS_scaleCtr = SS_group + '_scaleCtr'
        for ss_node in selection :
            if (mc.nodeType(ss_node) == "joint") :
                SS_root_jnt = ss_node                
                makePrimitiveJoint(ss_node)
        if len(mc.ls(SS_scaleCtr)) == 0 :
            mc.createNode('multiplyDivide', n=SS_scaleCtr)
            mc.setAttr(SS_scaleCtr + ".input1X", 1)
            mc.setAttr(SS_scaleCtr + ".input2X", 1, lock=True)
            mc.setAttr(SS_scaleCtr + ".input1Y", 1)
            mc.setAttr(SS_scaleCtr + ".input2Y", 1, lock=True)
            mc.setAttr(SS_scaleCtr + ".input1Z", 8)
            mc.setAttr(SS_scaleCtr + ".input2Z", 1, lock=True)
            self.connectAttr()
        else :
            self.connectAttr()
            
    def connectAttr(self) :
        typeList = ["_ballMultiply", "_edgeMultiply"]
        for typeName in typeList :
            mc.select("*" + SS_group + typeName, r=True)
            selectionList = mc.ls(sl=True)
            if typeName == '_ballMultiply':
                for selection in selectionList :                    
                    if selection not in self.SS_MDNlist :
                        mc.connectAttr(SS_scaleCtr+'.outputX' , selection+'.input1X')
                        self.SS_MDNlist.append(selection)                        
            elif typeName == '_edgeMultiply' :
                for selection in selectionList : 
                    if selection not in self.SS_MDNlist :
                        mc.connectAttr(SS_scaleCtr+'.outputY' , selection+'.input1X')
                        mc.connectAttr(SS_scaleCtr+'.outputZ' , selection+'.input1Z')
                        self.SS_MDNlist.append(selection)
                        
    def create(self):        
        if mc.window(self.winName, exists=True):
            mc.deleteUI(self.winName)
        mc.window(self.winName, title=self.winTitle)
        self.mainCol = mc.columnLayout(adjustableColumn=True)
        mc.frameLayout( labelVisible=False, borderStyle='etchedOut', width=300 )
        mc.columnLayout(adjustableColumn=True, columnAttach=('both', 7))
        mc.rowColumnLayout(numberOfColumns=2, columnWidth=[(1,90),(2,200)])        
        mc.text(" ")        
        mc.text(" ")
        mc.text(label = '1.', align = 'center')
        mc.text(label = 'Choose the root joint')       
        mc.text(label = '2.', align = 'center')
        mc.button(label='Generate', command=self.makeSS)        
        mc.text(label = '3.', align = 'center')
        mc.text(label = 'edit')        
        mc.text(label = 'Ball Size', align = 'right')      
        self.ballSizeSlider = mc.floatSliderGrp(field=True, value = 1.0, minValue = 0.0, maxValue = 10, fieldMinValue = -10, fieldMaxValue = 100, 

columnWidth = [(1,30), (2,110)], pre=2, dc=self.changeBallScale, cc=self.doNothing)
        mc.text(label = 'Edge Size', align = 'right')      
        self.edgeSizeSlider = mc.floatSliderGrp(field=True, value = 1.0, minValue = 0.0, maxValue = 10, fieldMinValue = -10, fieldMaxValue = 100, 

columnWidth = [(1,30), (2,110)], pre=2, dc=self.changeEdgeScale, cc=self.doNothing)
        mc.text(label = 'Edge Divide', align = 'right')
        self.edgeDivideSlider = mc.intSliderGrp( field=True, minValue=3, maxValue=100, value=8, columnWidth = [(1,30), (2,110)], dc=self.changeEdgeDivide, 

cc=self.doNothing) 
        mc.text(" ")        
        mc.text(" ")
        mc.setParent('..')              
        mc.showWindow(self.winName)
        return
    
        
#create UI
PrimitiveSkeletonUI().create()
