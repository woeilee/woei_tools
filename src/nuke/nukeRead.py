#nukeRead.py
 
import nuke
import os
import re
import time
 
 
 
 
 
#####################################################################
 
"""
convert between /Volumes/ or Z: for windows
"""
unixRoot = '/Volumes/'
winRoot = 'Z:'
 
def unixStyleRead():
    reads = []
    sel = nuke.selectedNodes()
    for node in sel:
        if node.Class() == "Read":
            reads.append(node)
        
    if len(sel) == 0:
        reads = nuke.allNodes('Read')
        
    for read in reads:
        filein = read[ 'file' ].value()
        unixStyle = filein.replace( winRoot, unixRoot )
        read[ 'file' ].setValue( unixStyle )
        read[ 'reload' ].execute()
        print read['file']
 
def winStyleRead():
    reads = []
    sel = nuke.selectedNodes()
    for node in sel:
        if node.Class() == "Read":
            reads.append(node)
        
    if len(sel) == 0:
        reads = nuke.allNodes('Read')
        
    for read in reads:
        filein = read[ 'file' ].value()
        winStyle = filein.replace( unixRoot, winRoot )
        read[ 'file' ].setValue( winStyle )
        read[ 'reload' ].execute()
        print read[ 'file' ]
 
 
 
#####################################################################
 
"""
walk the directories and convert path to nuke style
"""
 
def parsePath(path):
    dirlist = list()
    task = nuke.ProgressTask('Examining files in ...          ')
 
    for (root, dirs, files) in os.walk(path):
    
        if len(dirs)==0:
                files=nuke.getFileNameList(path)
                for seq in files:  
                        filepath = os.path.join(path, seq)                          
                        if not os.path.isdir(filepath.split(' ')[0]):
                            if filepath not in dirlist:                        
                                dirlist.append(filepath)
                                
        for dir in dirs: 
 
            if len(dir) != 0:            
                if not dir.startswith('.'):
                        dirname = os.path.join(root, dir) 
                        files = nuke.getFileNameList(dirname) 
                        if len(files) != 0:
                            for seq in files:
 
 
                                                   
                                if seq.find('.')!=-1:  
                                    if seq != 'Thumbs.db' and seq != '' : 
                                        try: 
                                            filepath = os.path.join(dirname, seq)
                                            if filepath not in dirlist: 
                                                dirlist.append(filepath)
       
                                        except ValueError: 
                                            break                           
 
 
        progressIncr = 0.1*len(files)  
        if task.isCancelled():
            break                                     
        for i in range(int(progressIncr)):
            task.setProgress(int(i))
            task.setMessage(root)
            time.sleep(0.01)
 
    return dirlist
    
def validatePath(path):
    validate = re.split("[/_]+",path)    
    if not validate:
        return None
    return validate    
 
 
def nukePath(path):
    mtch = re.match(r"(.+?).(\d+-\d+)(#+).(\w+)", path)
    if not mtch:
        newPath = path # <-- Need full path including the basename 
        if os.path.isdir(path):
           fileList = nuke.getFileNameList(path)
           
           print '\nfileList:',fileList
        else: 
            dirname = os.path.dirname(path)
            fileList = nuke.getFileNameList(dirname)
            filename = os.path.basename(path)
 
        for f in fileList:
            
            if (' ') in f:
                basename, frame = f.split()
                firstframe = frame.split('-')[0]
                lastframe = frame.split('-')[-1] 
                if len(f)<=2:
                   filename, ext = basename
                   firstframe = '1'
                   lastframe = '1'
                else:
                   filename = f 
            else:
                filename = f
                basename = f
                firstframe = '1'
                lastframe = '1'                
                          
            newPath = os.path.join(path,basename)    
            dic = {filename:[newPath, firstframe, lastframe]} 
            return dic
        
    else: 
        pad = mtch.group(3).count('#')
        newPath =  '.'.join([mtch.group(1), '%%0%sd'%pad, mtch.group(4)]) + ' ' + mtch.group(2)
 
        
    dirname, filename = os.path.split(mtch.group(1))
    firstframe, lastframe = mtch.group(2).split('-')
 
    return dic
   
def frames(path):
    firstframe = nukePath(path).values()[0][1]
    lastframe = nukePath(path).values()[0][2]
 
    return firstframe, lastframe
    
    
    #####################################################################

