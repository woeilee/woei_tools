import os
import nuke
from Qt import QtWidgets
from Qt import QtCompat
from Qt import QtGui
from fnmatch import fnmatch
from Qt import QtCore as QtCore


Home = os.environ.get ("HOME", None )
file_interface = os.path.join(Home, ".nuke/connectionEditor_FS.ui")

# global ConnectionEditor



##################################################################################################



class ConnectionEditorPanel(QtWidgets.QMainWindow):


    def __init__(self, parent=None):
        '''
        Loading interface, ui made in Designer
        '''
        super(ConnectionEditorPanel, self).__init__(parent)
        self.main_widget = QtCompat.loadUi(file_interface)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("Connection Editor")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.warning = QtWidgets.QMessageBox()

        #hidden LineEdit for saving Nodes
        self.sourceNode = QtWidgets.QLineEdit()
        self.targetNodes = QtWidgets.QLineEdit()

        self.resize(580, 760)



        
        #### Get QtWidget objects, edit ui in designer
        
        self.listWidget_SourceKnobsList = self.main_widget.findChild(QtWidgets.QListWidget, "listWidget_SourceKnobs")
        self.listWidget_TargetKnobsList = self.main_widget.findChild(QtWidgets.QListWidget, "listWidget_TargetKnobs")

        ### Grab Source label for updatting
        self.source_knobs_label = self.main_widget.findChild(QtWidgets.QLabel, "Label_SourceKnobs")       

        ### Define Search
        self.searchBox = self.main_widget.findChild(QtWidgets.QLineEdit, "lineEdit_SearchText")
        self.searchBox.textEdited.connect(self.on_search_entered)
        self.searchBox.setFocus()

        ### Define PushButtons role
        self.reloadSource = self.main_widget.findChild(QtWidgets.QPushButton, "pushButton_reloadSource")
        self.reloadSource.clicked.connect(  self.on_reload_source_clicked  )

        self.reloadTarget = self.main_widget.findChild(QtWidgets.QPushButton, "pushButton_reloadTarget")
        self.reloadTarget.clicked.connect(  self.on_reload_target_clicked  )


        self.clearAll = self.main_widget.findChild(QtWidgets.QPushButton, "clearAll")
        self.clearAll.clicked.connect(  self.on_clear_all_clicked  )

        self.copyValue = self.main_widget.findChild(QtWidgets.QPushButton, "copyValue")
        self.copyValue.clicked.connect(  self.on_copyValue_clicked  )

        self.setExpression = self.main_widget.findChild(QtWidgets.QPushButton, "setExpression")
        self.setExpression.clicked.connect(  self.on_setExpression_clicked  )

        self.breakButton = self.main_widget.findChild(QtWidgets.QPushButton, "breakButton")
        self.breakButton.clicked.connect(  self.on_breakButton_clicked  )

        self.button_close = self.main_widget.findChild(QtWidgets.QPushButton, "closeButton")
        self.button_close.clicked.connect(self.main_widget.parent().close)


        self.gather_nodes()
        self.initiate_panel()




##################################################################################################




    def gather_nodes(self):
        '''
        Gather all the Selected Nodes
        '''

        nodes = []
        source_node = None
        target_nodes = []
        nodes.extend(nuke.selectedNodes())

        if nodes:
            source_node = nodes[-1]


        return nodes, source_node, target_nodes

    # def save_nodes_selections(self, nodes):
    #     nodes = nodes
    #     self.sourceNode.insert(str(nodes[-1].name()))
    #     self.targetNodes.insert(str(', '.join([n.name() for n in nodes[:-1]])))

    #     return nodes

        #########
        '''
        To Do, Copy and Expression won't work when the Nodes are not currently selected
        Need to store the the Node selected some where
        '''

        #########

    def initiate_panel(self):
        '''
        Open Panel the first time, populate list if Knobs availabe
        '''
        nodes = []
        nodes = self.gather_nodes()[0]
        self.gather_knobs_list(nodes)
        self.on_reload_source_clicked()

        if len(nodes)>1:
            target_nodes = nuke.selectedNodes()[:-1]
            self.on_reload_target_clicked()


    def gather_knobs_list(self, nodes):
        '''
        Gather available knob names to the list
        '''
        nodes = nodes #nuke.selectedNodes()
        if not len(nodes):
            self.warning.setVisible(True)
            self.warning.setText('Nothing Selected,\nPlease select a source node and target nodes...')
            nodes = []
            self.main_widget.show()
            return

        source_node = nodes[-1]        
        source_knobs = []
        try:
            for knob in source_node.knobs():
                source_knobs.append(knob)
        except:
            pass        

        target_nodes = nodes[:-1] 
        target_knobs = set()

        for node in target_nodes:
            for knob in node.knobs():
                target_knobs.add(knob)
     


        return source_knobs, list(target_knobs)



##################################################################################################




    def on_search_entered(self):
        '''
        User Search text filter knob list
        '''
        search_text = self.main_widget.findChild(QtWidgets.QLineEdit, "lineEdit_SearchText").displayText()
        SourceKnob_listWidget = (self.listWidget_SourceKnobsList)


        items = []
        for index in xrange(SourceKnob_listWidget.count()):
             items.append(SourceKnob_listWidget.item(index))


        if search_text:

            _filtered = list()
            for item in items:
                key = item.text() 
                if self.match_filter(key, search_text):
                    _filtered.append(str(key))
       
            SourceKnob_listWidget.clear()
            SourceKnob_listWidget .addItems( sorted( _filtered ) ) 

 


        else:
            self.gather_knobs_list()




    def search_filtered(self, orig_items):
         search_text = self.main_widget.findChild(QtWidgets.QLineEdit, "lineEdit").displayText()


         if (orig_items in search_text):
             return True
         else:
             return False


    @staticmethod
    def match_filter(source, line_string, full_text=True):
        '''
        Filter from the Search text
        '''
        line_string = [i.strip() for i in line_string.split(',')]
        line_string = [item.strip() for sublist in [i.split(' ') for i in line_string] for item in sublist if item.strip()]


        if full_text:
            line_string = ['*{}*'.format(i) for i in line_string]
        line_string = list(set(line_string))


        return all([fnmatch(source.lower(), string.lower()) for string in line_string])



##################################################################################################



    ### Push Buttons ###

    def on_reload_source_clicked(self):
        nodes = []
        nodes.extend(nuke.selectedNodes())
        if nodes:
            source_knobs = self.gather_knobs_list(nodes)[0]

            self.listWidget_SourceKnobsList.clear()
            self.listWidget_SourceKnobsList.addItems(source_knobs)
            self.listWidget_SourceKnobsList.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.sourceNode.clear()
            self.sourceNode.insert(str(nodes[-1].name()))
            self.source_knobs_label.setText('Source Node: %s\nKnobs' %(nodes[-1].name()))



    def on_reload_target_clicked(self):  
        target_nodes = nuke.selectedNodes()
        target_knobs = set()
        for node in target_nodes:
            for knob in node.knobs():
                target_knobs.add(knob)
        self.listWidget_TargetKnobsList.clear()
        self.listWidget_TargetKnobsList.addItems(sorted(list(target_knobs)))
        self.targetNodes.clear()
        self.targetNodes.setText(str(', '.join([n.name() for n in target_nodes[:-1]])))



    def on_clear_all_clicked(self):
        '''
        Clear All List
        '''
        self.source_knobs_label.setText('Source Knobs')
        self.listWidget_SourceKnobsList.clear()
        self.listWidget_TargetKnobsList.clear()

    def on_copyValue_clicked(self):
        '''
        Copy Value from Selected Knob from Source to Target knobs
        '''
        nodes = str(self.targetNodes.text()).split(', ')
        source_node = nuke.toNode(str(self.sourceNode.text()))

        selected_source_knobs = self.listWidget_SourceKnobsList.selectedItems()

        target_connection = self.listWidget_TargetKnobsList.currentItem()
        connection_list = []


        ### Going through targert knobs on target nodes
        for item in selected_source_knobs:
            knob_name = item.text()


            for node in nodes:
                    node_name = nuke.toNode(node).name()
                    knob_value = source_node[knob_name].getValue()
                    nuke.toNode(node)[knob_name].clearAnimated()
                    nuke.toNode(node)[knob_name].setValue(knob_value)           
                    connection_list.append( '%s.%s: %s: %s'%(node_name, knob_name, 'setValue', knob_value))    
            print connection_list



    def on_setExpression_clicked(self):
        '''
        Set Expression Link from Selected Knob from Source to Targer knobs
        '''

        nodes = str(self.targetNodes.text()).split(', ')
        source_node = str(self.sourceNode.text())


        SourceKnob_listWidget = self.listWidget_SourceKnobsList
        selected_knobs = SourceKnob_listWidget.selectedItems()


        target_connection = self.listWidget_TargetKnobsList.currentItem()
        connection_list = []


        for item in selected_knobs:
            knob_name = item.text()
            expression = '%s.%s'%(source_node, knob_name)


            for node in nodes:
                    node_name = nuke.toNode(node).name()
                    nuke.toNode(node)[ knob_name ].setExpression( expression )
                    connection_list.append( str('%s.%s: %s: "%s"'%(node_name, knob_name, 'setExpression', expression)))
            print connection_list        



    def on_breakButton_clicked(self):

        target_nodes = str(self.targetNodes.text()).split(', ')

        for node in target_nodes:
            for knob in nuke.toNode(node).knobs():
                if nuke.toNode(node)[knob].hasExpression():
                    try:
                        nuke.toNode(node)[knob].clearAnimated()
                    except:        
                        nuke.message("error while breaking expression")
                        pass














ConnectionEditor = None
def showDialog():
    global ConnectionEditor
    ConnectionEditor = ConnectionEditorPanel()
    ConnectionEditor.show()
showDialog()
