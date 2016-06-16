import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import math
import re
from string import Template, zfill
from functools import partial

class Find_Out():
    '''
    multipurpose class for finding length of anything. Well, work in progress
    '''
    
    def edge_length(self, vertex_list):
        #find distance between two points. numpy required. need to rework this so numpy not required
        vtx_p=cmds.xform(vertex_list,q=True,t=True,ws=True)
        '''
        this is numpy version. reuse for machines with numpy for quicker calculations:
            
        vtx_p_array_a = np.array([[vtx_p[0]], [vtx_p[1]], [vtx_p[2]]])
        vtx_p_array_b = np.array([[vtx_p[3]], [vtx_p[4]], [vtx_p[5]]])
        dist = np.linalg.norm(vtx_p_array_a-vtx_p_array_b)
        
        '''
        dist = math.sqrt((vtx_p[3] - vtx_p[0])**2 + (vtx_p[4] - vtx_p[1])**2 + (vtx_p[5] - vtx_p[2])**2)
        return dist
        
    def curve_length(self, curve_sel):
        #find length of curve
        find_curve_length = cmds.arclen(curve_sel)
        return find_curve_length
        
class Chain_Constrain():
    def __init__(self, curve_sel, vertex_list, chain_geo):
        self.curve_sel = curve_sel
        self.verts = vertex_list
        self.chain_geo = chain_geo
        self.find_length = Find_Out()
        
        self.link_length = self.find_length.edge_length(self.verts)
        self.chain_length = self.find_length.curve_length(self.curve_sel)
        self.link_total = int(self.chain_length/self.link_length)
        self.motion_path_name = str(self.chain_geo) + '_Path'
        
        cmds.pathAnimation(self.chain_geo, name = self.motion_path_name, fractionMode = True, follow= True, followAxis = 'x', 
                upAxis = 'y', worldUpType = 'object', startTimeU = 1, endTimeU = self.link_total, c = self.curve_sel)
                
        cmds.setKeyframe(self.motion_path_name + '.frontTwist', v = 0.0, t = 1 )
        cmds.setKeyframe(self.motion_path_name + '.frontTwist', v = 60.0*self.link_total, t = self.link_total )
        
        cmds.keyTangent(self.motion_path_name + '.uValue', itt = 'linear', ott = 'linear' )
        cmds.keyTangent(self.motion_path_name + '.frontTwist', itt = 'linear', ott = 'linear')
        
        cmds.snapshot( self.chain_geo, constructionHistory=True, startTime=1, endTime = self.link_total, increment=1, update = 'animCurve', 
                name = str(self.chain_geo) + '_snapShot' )
        
        self.chain_group = cmds.group( em=True, name=str(self.chain_geo) + '_geo_grp' )
        
        self.chain_list = cmds.listRelatives(str(self.chain_geo + '_snapShotGroup'))
        
        for dummy_geo in self.chain_list:
            cmds.delete(icn = True, ch = True)
            cmds.parent(dummy_geo, self.chain_group)
                            
        
class Spline_Rig_Chain():
    def __init__(self, curve_sel, vertex_list):
        self.curve_sel = curve_sel
        self.verts = vertex_list
        self.find_length = Find_Out()
                
        self.link_length = self.find_length.edge_length(self.verts)
        self.chain_length = self.find_length.curve_length(self.curve_sel)
        self.link_total = int(self.chain_length/self.link_length)
        
        cmds.duplicate(self.curve_sel, n = 'buildCurve')
        cmds.rebuildCurve('buildCurve', ch = 1, rpo = 1, rt = 0, end = 1, kr = 2, kep = 1, kt = 0, kcp = 0, s = self.link_total/2, d = 3, tol = 0.01 )
        
        self.num_cv = int(cmds.getAttr ('buildCurve.degree'))+ (cmds.getAttr ('buildCurve.spans'))
        
        for dummy_cv in range(self.num_cv):
            dummy_cv_pos = (cmds.getAttr ('buildCurve.cv['+ str(dummy_cv) +']'))
            
            if dummy_cv == 0:
                cmds.joint(n=self.curve_sel+'_jointRoot',p = dummy_cv_pos[0])
            elif dummy_cv == self.num_cv - 1:
                cmds.joint(n=self.curve_sel+'_jointEnd', p = dummy_cv_pos[0])
            else:
                cmds.joint(n=self.curve_sel+'_joint_'+(str(dummy_cv)),p = dummy_cv_pos[0])    
        
        cmds.delete('buildCurve')        
        cmds.ikHandle( sj = (self.curve_sel+'_jointRoot'), ee = (self.curve_sel+'_jointEnd'), c = self.curve_sel,
                sol = 'ikSplineSolver', scv = 0, pcv = 0, ccv = 0, ns = 4)       
                

class Chain_Maker_UI():
    def __init__(self):
        window = cmds.window( title="Chain Maker", iconName='ChnMk', widthHeight=(300, 100) )
        cmds.columnLayout( adjustableColumn=True )
        cmds.separator( style='single' )
        self.curve_sel_name = cmds.textFieldGrp( label = 'Curve Selection' )
        cmds.separator( style='single' ) 
        cmds.button( label='Run', command=partial(self.run_command, 1) )
        cmds.separator( style='single' )     
        cmds.button( label='Exit', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
        cmds.setParent( '..' )
        cmds.showWindow( window )
        
    def curve_name(self, *args):
        self.curve_sel = cmds.textFieldGrp(self.curve_sel_name, query=True, text=True)
        return self.curve_sel
        
    def run_command(self, *args):
        curve_sel = self.curve_name()
        vert_sel_list = cmds.ls(sl=True, fl = True)
        if '.' in vert_sel_list[0]:
            dummy_item_index = vert_sel_list[0].index('.')
            self.geo_name = vert_sel_list[0][0:dummy_item_index]
                        
        Chain_Constrain(curve_sel, vert_sel_list, self.geo_name)
        Spline_Rig_Chain(curve_sel, vert_sel_list)
        
        self.chain_list = cmds.listRelatives(str(self.geo_name + '_geo_grp'))
        
        joint_list = cmds.ls(type = 'joint')
        
        for dummy_geo in self.chain_list:
            cmds.select(dummy_geo, add = True)
        
        for dummy_joint in joint_list:
            if 'ikHandle' in dummy_joint:
                pass
            elif curve_sel in dummy_joint:
                 cmds.select(dummy_joint, add=True)
        cmds.select('ikHandle*', d = True)          
        mel.eval('newBindSkin " -byClosestPoint -toSkeleton";')

               
        
        
        

Chain_Maker_UI()

