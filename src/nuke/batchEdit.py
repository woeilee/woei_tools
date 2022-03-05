#-*- coding: utf-8
#batchEdit.py



import os
import nuke
import nukescripts
import json

   
class batchEdit( nukescripts.PythonPanel ):
 
    def __init__( self ):
        nukescripts.PythonPanel.__init__( self, 'Woei Lee Batch Edit', '' )
        '''
        Defining Knobs
        '''

        self.Knob = nuke.Enumeration_Knob( 'knob', 'knob', [''] )
        self.edit = nuke.Enumeration_Knob( 'edit', 'edit in', ['value', 'expression'] )
        self.newValue = nuke.String_Knob( 'value', 'new value')
        self.pulldownKnob = nuke.Enumeration_Knob( 'value', 'new value',[''] )   
        self.clearExpression = nuke.Boolean_Knob( 'clear', 'clear current expression ' )
        self.warning = nuke.Text_Knob( 'warning', '<span style="color:red">select nodes to edit</span>' )
        self.font = nuke.Enumeration_Knob( 'font', 'font',  [''] )
        self.font_style = nuke.Enumeration_Knob( 'font_style', 'font style',  [ 'Regular' ] )
        self.setMinimumSize(500, 120)
 
        self.addKnob(self.Knob)
        self.addKnob(self.warning)
        self.warning.clearFlag(nuke.STARTLINE)
        self.warning.setVisible(False)
        self.addKnob(self.edit)
        self.split = nuke.PyScript_Knob( 'split', 'xyz/rgba' )         
        self.addKnob(self.split)
        self.split.clearFlag(nuke.STARTLINE)
        self.addKnob(self.newValue)

        self.newKnob0 = nuke.String_Knob('new value  x/r')
        self.newKnob1 = nuke.String_Knob('y/g')
        self.newKnob2 = nuke.String_Knob('z/b')
        self.newKnob3 = nuke.String_Knob('a')
        
        self.addKnob(self.newKnob0)
        self.addKnob(self.newKnob1)
        self.addKnob(self.newKnob2)
        self.addKnob(self.newKnob3)
        self.addKnob(self.font)
        self.addKnob(self.font_style)
        self.font_style.clearFlag(nuke.STARTLINE)
        self.addKnob(self.clearExpression)
 
        self.newKnob1.clearFlag(nuke.STARTLINE)
        self.newKnob1.clearFlag(nuke.STARTLINE)
        self.newKnob2.clearFlag(nuke.STARTLINE)
        self.newKnob3.clearFlag(nuke.STARTLINE)
        self.clearExpression.setFlag(nuke.STARTLINE)
 
        self.newKnob0.setVisible(False)
        self.newKnob1.setVisible(False)
        self.newKnob2.setVisible(False)
        self.newKnob3.setVisible(False)   
        self.font.setVisible(False)
        self.font_style.setVisible(False)
        self.addKnob(self.pulldownKnob)
        self.pulldownKnob.setVisible(False)
        self.getKnobs()     
        self.buildFontsDic()
 

    ##############################################################################################################  

 
    def getKnobs(self):
        '''
        Get all the knobs on all the selectedNodes
        '''
        
        def knobsIntersect(knobsA, knobsB):
            intersection = dict()
 
            for name, knob in knobsA.items():
                if knobsB.has_key(name) and \
                   knobsB[name].Class() == knob.Class():
                    intersection[name] = knob
 
            return intersection
 
 
        nodes = nuke.selectedNodes()
        for node in nodes:
            if node.Class() == "Group":
                n=nuke.toNode(node.name())
                n.begin()
 
        if not len(nodes):
            nuke.message("nothing selected")            
            self.warning.setVisible( True )
            return
 
        knobs = nodes[0].knobs()
        for node in nodes[1:]:
            knobs = knobsIntersect(knobs, node.knobs())
 
        knobs = knobs.keys()
        knobs.sort()
        
        if nodes[-1].Class() == 'Text2':
            self.Knob.setValue( 'font' )
 
        self.Knob.setValues( knobs )      
        
        
        #Insert fonts to the font knob        
        self.font.setValues( sorted( self.buildFontsDic() ) )
 
 
    def get_root_channels(self):
        '''
        Get all the available Channels from the script root
        '''
        channels = set()    
        for i in nuke.root().channels():
            channels.add(i.split('.')[0])

        return channels         

       

    def pulldown_class_list(self):
        '''
        List of all pulldown knobs
        '''

        pulldown_classes = ['Enumeration_Knob', 'Pulldown_Knob'] #'Format_Knob'

        channel_classes =  ['ChannelSet_Knob', 'ChannelMask_Knob', 
                            'Input_ChannelSet_Knob', 'Input_ChannelMask_Knob', 'Channel_Knob', 
                            'Input_Channel_Knob']

        return pulldown_classes, channel_classes
 

        
    def buildFontsDic(self):
        '''
        Print the font family and styles form the font manifest files
        
        '''

        from subprocess import PIPE, Popen

        font_dict = {}
        proc = Popen(["fc-list"], stdout=PIPE)
        for line in proc.stdout:
            _, name, elements = line.split(":")
            font_dict.setdefault(
                name.strip().split(',')[0],[]).extend(
                    elements.strip().replace('style=','').split(',')
            )
        
        
        return font_dict


    ##############################################################################################################  

 
    def knobChanged( self, knob ):

        selectedKnob = self.Knob.value() 
        self.pulldownKnob.setVisible(False)

        if selectedKnob == 'font':
            if self.font.visible() != True:
                self.font.setVisible(True)
                self.font_style.setVisible(True)
                self.newValue.setVisible(False)
                self.newKnob0.setVisible(False)
                self.newKnob1.setVisible(False)
                self.newKnob2.setVisible(False)
                self.newKnob3.setVisible(False)
                self.edit.setVisible(False)
                self.split.setVisible(False)
                self.clearExpression.setVisible(False)
 
        elif knob.name() == 'split':
            if self.newValue.visible() == True:
                self.newValue.setVisible(False)
                self.newKnob0.setVisible(True)
                self.newKnob1.setVisible(True)
                self.newKnob2.setVisible(True)
                self.newKnob3.setVisible(True)
                self.font.setVisible(False)
            else:
                self.newValue.setVisible(True) 
                self.newKnob0.setVisible(False)
                self.newKnob1.setVisible(False)
                self.newKnob2.setVisible(False)
                self.newKnob3.setVisible(False)
                self.font.setVisible(False)
        else:
            self.font.setVisible(False)
            self.font_style.setVisible(False)
            self.newValue.setVisible(True) 
            self.edit.setVisible(True)
            self.split.setVisible(True)
            self.clearExpression.setVisible(False)               
 
        if knob.name()== 'font':
            self.font_style.setValues( self.buildFontsDic()[self.font.value()] )
 
        pulldown_classes = self.pulldown_class_list()[0]
        channel_classes =self.pulldown_class_list()[1]
        node = nuke.selectedNodes()[-1]

        if selectedKnob:
            if any( word in node[selectedKnob].Class() for word in pulldown_classes):

                if self.pulldownKnob.visible() != True:
                    self.pulldownKnob.setVisible(True)
                    self.pulldownKnob.setValues( node[selectedKnob].values() )
                    # self.pulldownKnob.setValue(node[selectedKnob].value())
                    self.newValue.setVisible(False)
                    self.split.setVisible(False)
                    pass

            elif any( word in node[selectedKnob].Class() for word in channel_classes):
                if self.pulldownKnob.visible() != True:
                    self.pulldownKnob.setVisible(True)
                    self.pulldownKnob.setValues( list(self.get_root_channels())) 
                    # self.pulldownKnob.setValue(node[selectedKnob].value())
                    self.newValue.setVisible(False)
                    self.split.setVisible(False)
                    pass

            elif selectedKnob == 'format':
                self.newValue.setVisible(False)
                self.split.setVisible(False)
                self.pulldownKnob.setVisible(True)
                self.pulldownKnob.setValues( [i.name() for i in nuke.formats()] )
                # self.pulldownKnob.setValue(node[selectedKnob].value().name())
                pass

            else:
                self.newValue.setVisible(True)
                self.split.setVisible(True)    


    ##############################################################################################################  
    

    def setDefaultValue( self ):
        '''
        set default knob for certain node
        '''

        node = nuke.selectedNodes()[-1]

        if node.Class() in ['Text','Text2']:
            self.Knob.setValue('font')
            self.font.setValue(node['font'].getValue()[0])
            self.font_style.setValue(node['font'].getValue()[1])  

        if node.Class() in ['Blur', 'Dilate', 'Erode', 'FilterErode', 'ZBlur']:
            self.Knob.setValue('size')   

        if node.Class() in ['Grade']:
            self.Knob.setValue('white')         
        if node.Class() in ['ColorCorrect']:
            self.Knob.setValue('gain')    

        if node.Class() in ['Multiply']:
            self.Knob.setValue('value')   

        if node.Class() in ['Merge2']:
            self.Knob.setValue('operation')

        if node.Class() in ['Transform']:
            self.Knob.setValue('translate')

        if node.Class() in ['Reformat']:
            self.Knob.setValue('format')
                   
 

    def showModalDialog( self ):
 
        self.setDefaultValue()

        show = nukescripts.PythonPanel.showModalDialog( self )

        if self.newValue.visible() == True:
            newVal = self.newValue.getValue()

        elif self.pulldownKnob.visible() == True:
            newVal = self.pulldownKnob.value()    
  

        else:
            newVal = [self.newKnob0.getValue(), self.newKnob1.getValue(), self.newKnob2.getValue(), self.newKnob3.getValue()]
            newVal = [x if x else None for x in newVal]

        isExpr = self.edit.getValue()
        clear = self.clearExpression.getValue()  

        if show:
            self.changeKnobValue( newVal, isExpr, clear )
 
 
    def changeKnobValue(self, newVal, isExpr, clear):
 
        nodes = nuke.selectedNodes()
        Knob = self.Knob.value()
        print nodes
        print 'knob:', Knob
        print 'new value: ', newVal
        print 'is expression: ', isExpr
        split = self.newValue.visible() == False
        title = nukescripts.goofy_title()
        val = 0
        if isExpr:
            print "edit expression"       
            for node in nodes:
                if clear:
                    node.knob(Knob).clearAnimated()
                try:
                    if split:
                        for step, val in enumerate(newVal): 
                            if not val == None:                                 
                                node.knob(Knob).setSingleValue(False)          
                                node.knob(Knob).setExpression(newVal[step],step) 
                                print node.name(), val, step 
 
                    else:    
                        node.knob(Knob).setSingleValue(True)
                        node.knob(Knob).setExpression(newVal)
 
                except:
                    nuke.message("error while setting expression: \n\n" + title )
        else:
            print 'edit value'
            for node in nodes :
                if clear:
                    node.knob(Knob).clearAnimated()
                try:
                    newValType = type(node.knob(Knob).value())  
 
                    try :
                        if Knob == 'font': # <<<< Text Node here
                            if node.Class() == 'Text2':
                                newVal = self.font.value()
                                newStyle = self.font_style.value()             
                                node.knob('font').setValue( newVal , newStyle ) 
                                print node.name(), newVal, newStyle
  
 
                            elif node.Class() == 'Text':
                                newVal = self.buildFontsDic()[self.font.value()][1]
                                newStyle = self.font_style.value()               
                                node.knob('font').setValue( newVal )
                                node.knob('index').setValue( newStyle ) 
                                print node.name()
 
                                
                            else:
                                node.knob('font').setValue( newVal )
                                  

                        if Knob == 'format':            
                            node.knob(Knob).setValue(newVal)  

                            
                        if newValType == str:
                            if Knob != 'name':                   
                                node.knob(Knob).setValue(str(newVal))
                            if Knob == 'name':
                                val += 1
                                node.knob('name').setValue( '%s_%s' %( newVal , str(val) ) ) 
                                print  "new name: "   '%s_%s' %( newVal , str(val) )                        
                        if newValType == list or newValType == tuple or newValType == float: 
                            if split:
                                try:
                                    for step, val in enumerate(newVal): 
                                        if val == None: 
                                            continue
                                        else:     
                                            node.knob(Knob).setValue(float(val),step)   
                                except:
                                    raise 'error while editing new value'        
                        else:
                            node.knob(Knob).setSingleValue(True) 
                            node.knob(Knob).setValue(float(newVal))
                        if newValType == float:         
                            node.knob(Knob).setValue(float(newVal))
                        if newValType == int:                           
                            node.knob(Knob).setValue(int(newVal))
                        if newValType == unicode:                           
                            node.knob(Knob).setValue(unicode(newVal))
                        if newValType == tuple:                         
                            node.knob(Knob).setValue(float(newVal))
 
                        if newValType == bool:                   
                            node.knob(Knob).setValue(float(newVal))
                    except:
                        #nuke.message('error while editing new value')
                        continue
   
 
                except:
                    pass  
 
 
def showDialog():
    batchEdit().showModalDialog()
 
 
        ###############################################WL#
#showDialog()
