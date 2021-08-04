#batchRead.py


import re
import os
import nuke       
import nukescripts
import nukeRead
from fnmatch import fnmatch

 
 
 
# Batch Read      
 
"""
Batch Read allow user to bring multiple files inside subfolders at once.
"""
 
_EXT_MAPPING = {
            'OCIOFileTransform': ['3dl', 'blut', 'cms', 'csp', 'cub', 'cube', 'vf', 'vfz'],
            'Read': ['cin', 'dpx', 'exr', 'external', 'hdr', 'jpeg', 'mov\t\t\tffmpeg', 'mp4', 'null', 'pic', 'png', 'sgi', 'targa', 'tiff', 'xpm', 'yuv'],
            'ReadGeo2': ['abc', 'external', 'fbx', 'obj']
}

_EXT_MAPPING = {'.' + ext: node_type for node_type, extensions in _EXT_MAPPING.items() for ext in extensions} 
 
class BatchRead( nukescripts.PythonPanel ):
 
    def __init__( self ):
        nukescripts.PythonPanel.__init__( self, 'Batch Read')
        self.setMinimumSize(800, 500)   
        self.trigger_knob = {} 
        self.knob_list = []
        knobPanelMap = {}
 
 
        # Create Main Knobs
        self.filepath_knob = nuke.File_Knob( "filepath", "filepath" )
        self.filter_knob = nuke.EvalString_Knob( 'filter', 'filter',  )
        self.list_knob = nuke.SceneView_Knob( "list", "list", [] )
 
 
        # trigger Knobs
        self.trigger_knob['filepath'] = False
        self.trigger_knob['filter'] = False
        self.trigger_knob['list'] = False
 
        # Add Knob to Panel
        self.addKnob( self.filepath_knob )
        self.knob_list.append( self.filepath_knob )
 
        self.addKnob( self.filter_knob )
        self.knob_list.append( self.filter_knob )
 
        self.addKnob( self.list_knob )
        self.knob_list.append( self.list_knob )
 
 
 
 
        ###############################################
 
 
 
    def on_browseButton_clicked(self):
        curPath = self.filepath.text()
        seqPath = ' '.join(nuke.getClipname('Get Sequence','*',curPath).split(' '))    
        print seqPath    
        self.filepath_knob.clear()
        self.list_knob.clear()
        self.filepath.insert(seqPath)
        self.validatePath(seqPath)
 
    def on_lineEdit_returnPressed(self):
        seqPath = self.filepath_knob.text()
        self.list_knob.clear()
        self.validatePath(seqPath)
 


    def get_extension(self, path):
        if not path:
            return
        path = path.strip()
        if ' ' in path:
            segments = path.split(' ')
            if len(segments) != 2:
                print("[INVALID] Not exactly two segments {}.".format(segments))
                return

            tail = re.sub(r'[^A-Za-z]', '', segments[-1])
            if tail:
                print("[INVALID]The string after space '{}' is not composed by only digits and symbols.".format(segments[-1]))
                return

            path = segments[0]
        
        match = re.match(r".+\.(\w+)", path)
        # if match:
        #     extension = match.group(1)
        # else:
        extension = os.path.splitext(os.path.basename(path))[-1]

        if not extension:
            print("File '{}' has no extension.".format(path))
            return
        return extension


    def on_searched_filter(self):

        line = self.filter_knob.getText()

        cur_items = list(set(self.list_knob.getAllItems()))


        if line:
            #filtered = [key for key in cur_items if self.match_filter(key, line)]
            _filtered = list()
            for key in cur_items:
                #print "printing key and type", key, type(key)
                if self.match_filter(key, line):
                    _filtered.append(key)
            #print _filtered


            self.list_knob.removeItems(self.list_knob.getAllItems())
            self.list_knob.addItems( sorted( _filtered )  )     


    @staticmethod
    def match_filter( source, line_string, full_text=True):


        line_string = [i.strip() for i in line_string.split(',')]
        line_string = [item.strip() for sublist in [i.split(' ') for i in line_string] for item in sublist if item.strip()]
        
        if full_text:
            line_string = ['*{}*'.format(i) for i in line_string]
        line_string = list(set(line_string))
        return all([fnmatch(source.lower(), string.lower()) for string in line_string])





    def on_readNodeButton_clicked(self, paths):


        for path in paths:
            extension = self.get_extension(path)
            if not extension:
                continue

            node_type = _EXT_MAPPING.get(extension.lower())
            if not node_type:
                print("Cannot find node type through extension '{}' from file '{}'".format(extension, path))
                continue

            content = "file {" + '%s' % path + "}"

            n = nuke.createNode(node_type, content, inpanel=False)
            n.setSelected(False)
            nuke.autoplace(n)


 
    def on_filepath_BrowseButton_clicked(self):    
        file = ' '.join(nuke.getClipname('Get Sequence','*').split(' '))
        self.list_knob.append('%s'%file)
 
    def add_list(self, seqPath):
        dirList={}
        if seqPath.find('#')!=-1:
            self.list_knob.addItems(seqPath) 
        else:
            dirList = nukeRead.parsePath(seqPath)
            self.list_knob.addItems(dirList)
        return dirList
 
 
 
        ###############################################
 
 
 
    def showModalDialog( self ):
 
        show = nukescripts.PythonPanel.showModalDialog( self )
        if show:
            paths =  self.list_knob.getSelectedItems()
            self.on_readNodeButton_clicked(paths)
 
    def knobChanged( self, knob ):
        path =  self.filepath_knob.value()
 
        if knob == self.filepath_knob:
            self.add_list(path)
 
        if knob == self.filter_knob:
            # self.list_knob.removeItems()

            # ext = self.filter_knob.value()
            # paths =  self.add_list(path)
            # filtered_paths = [s for s in paths if ext in s]

            # self.list_knob.removeItems(self.list_knob.getAllItems())
            # self.list_knob.addItems(filtered_paths)

            self.on_searched_filter()
            # return filtered_paths
 


 
    if __name__ == '__main__':
        create_node_by_file_types() 
 
        ###############################################WL#
 
 
 
 
#BatchRead().showModalDialog()


