#knob_imputer
 
# -*- coding: utf-8 -*-
__version__ = '0.1.1'
 
from fnmatch import fnmatch
 
import nuke
import nukescripts
from PySide2 import QtCore, QtGui, QtWidgets
 
def keep_selection(list_widget):
    """
    This is decorator to select things after list_widget update
    """
    def decorator(function):
        def wrapper(*args, **kwargs):
            the_list_widget = getattr(args[0], list_widget)
            prev_items = [i.text() for i in the_list_widget.selectedItems()]
            result = function(*args, **kwargs)
            all_items = [the_list_widget.item(c) for c in range(the_list_widget.count())]
            if not result:
                return
            for prev in prev_items:
                if prev in result:
                    the_list_widget.item(result.index(prev)).setSelected(True)
            return result
        return wrapper
    return decorator
 
class MainWindow(QtWidgets.QMainWindow):
    _instance = None
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.central_widget = QtWidgets.QWidget(self)
        self.central_widget_layout = QtWidgets.QGridLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)
 
        self.top_tab = QtWidgets.QTabWidget(self.central_widget)
        self.central_widget_layout.addWidget(self.top_tab, 0, 0, 1, 1)
        self.connector_tab = QtWidgets.QWidget()
        self.top_tab.addTab(self.connector_tab, "Connect | Copy")
        self.empty_tab = QtWidgets.QWidget()
        self.top_tab.addTab(self.empty_tab, "Empty")
        self.connector_tab_layout = QtWidgets.QGridLayout(self.connector_tab)
 
        self.resize(1200, 584)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 734, 21))
        self.top_tab.setCurrentIndex(0)
        self.central_widget_layout.setContentsMargins(3, 2, 3, 0)
        self.connector_tab_layout.setContentsMargins(0, 3, 0, 0)
        self.connector_tab_layout.setHorizontalSpacing(0)
 
        self._1_qvl_widget = QtWidgets.QWidget(self.connector_tab)
        self.connector_tab_layout.addWidget(self._1_qvl_widget, 0, 0, 1, 1)
        self._1_qvl = QtWidgets.QVBoxLayout(self._1_qvl_widget)
        self._2_qhl_widget = QtWidgets.QWidget(self._1_qvl_widget)
        self._2_qhl = QtWidgets.QHBoxLayout(self._2_qhl_widget)
        self._1_qvl.setContentsMargins(0, 0, 0, 0)
        self._2_qhl.setContentsMargins(0, 0, 0, 0)
 
        # Left Panel
        self.source_knobs_qvl_widget = QtWidgets.QWidget(self._2_qhl_widget)
        self._2_qhl.addWidget(self.source_knobs_qvl_widget)
        self.source_knobs_qvl = QtWidgets.QVBoxLayout(self.source_knobs_qvl_widget)
        self.load_connect_source_qpb = QtWidgets.QPushButton('Load Source',self.source_knobs_qvl_widget)
        self.select_source_qpb = QtWidgets.QPushButton('Select Source',self.source_knobs_qvl_widget)
        self.source_knob_name_qle = QtWidgets.QLineEdit(self.source_knobs_qvl_widget)
        self.source_knobs_list = QtWidgets.QListWidget(self.source_knobs_qvl_widget)
 
        self.source_knobs_qvl.addWidget(self.load_connect_source_qpb)
        self.source_knobs_qvl.addWidget(self.select_source_qpb)
        self.source_knobs_qvl.addWidget(self.source_knob_name_qle)
        self.source_knobs_qvl.addWidget(self.source_knobs_list)
 
        # self.source_knobs_qvl_widget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.source_knobs_qvl.setSpacing(2)
        self.source_knobs_qvl.setContentsMargins(0, 0, 0, 0)
 
        # Right Panel
        self.target_qvl_widget = QtWidgets.QWidget(self._2_qhl_widget)
        self.target_qvl = QtWidgets.QVBoxLayout(self.target_qvl_widget)
        self.target_qvl.setContentsMargins(0, 0, 0, 0)
        self.lists_qhl_widget = QtWidgets.QWidget(self.target_qvl_widget)
        self.lists_qhl = QtWidgets.QHBoxLayout(self.lists_qhl_widget)
        self.lists_qhl.setContentsMargins(0, 0, 0, 0)
        self.target_nodes_qvl_widget = QtWidgets.QWidget(self.lists_qhl_widget)
 
        self.target_nodes_qvl = QtWidgets.QVBoxLayout(self.target_nodes_qvl_widget)
        self.target_nodes_qvl.setContentsMargins(0, 0, 0, 0)
        self.target_node_toggle_qpb = QtWidgets.QPushButton('Load Selection / ALL toggle button',self.target_nodes_qvl_widget)
        self.target_node_toggle_qpb.setEnabled(False)
        self.target_nodes_qvl.addWidget(self.target_node_toggle_qpb)
        self.target_name_qhl_widget = QtWidgets.QWidget(self.target_nodes_qvl_widget)
        self.target_name_qhl = QtWidgets.QHBoxLayout(self.target_name_qhl_widget)
        self.target_name_qhl.setContentsMargins(0, 0, 0, 0)
        self.target_name_qcb = QtWidgets.QCheckBox(self.target_name_qhl_widget)
        self.target_name_qcb.setText("Name")
        self.target_name_qcb.setChecked(False)
        self.target_name_qhl.addWidget(self.target_name_qcb)
        self.target_name_qle = QtWidgets.QLineEdit(self.target_name_qhl_widget)
        self.target_name_qhl.addWidget(self.target_name_qle)
        self.target_name_qhl.setStretch(2, 1)
        self.target_nodes_qvl.addWidget(self.target_name_qhl_widget)
        self.target_type_qhl_widget = QtWidgets.QWidget(self.target_nodes_qvl_widget)
        self.target_type_qhl = QtWidgets.QHBoxLayout(self.target_type_qhl_widget)
        self.target_type_qhl.setContentsMargins(0, 0, 0, 0)
        self.target_type_qcb = QtWidgets.QCheckBox(self.target_type_qhl_widget)
        self.target_type_qcb.setText("Type")
        self.target_type_qcb.setChecked(True)
        self.target_type_qhl.addWidget(self.target_type_qcb)
        self.target_type_qle = QtWidgets.QLineEdit(self.target_type_qhl_widget)
        self.target_type_qhl.addWidget(self.target_type_qle)
        self.target_nodes_qvl.addWidget(self.target_type_qhl_widget)
        self.target_node_list = QtWidgets.QListWidget(self.target_nodes_qvl_widget)
        self.target_node_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.target_nodes_qvl.addWidget(self.target_node_list)
        self.lists_qhl.addWidget(self.target_nodes_qvl_widget)
        self.target_knobs_qvl_widget = QtWidgets.QWidget(self.lists_qhl_widget)
        self.target_knobs_qvl = QtWidgets.QVBoxLayout(self.target_knobs_qvl_widget)
        self.target_knobs_qvl.setContentsMargins(0, 0, 0, 0)
 
        self.__ = QtWidgets.QWidget(self.target_knobs_qvl_widget)
        self.__qhl = QtWidgets.QHBoxLayout(self.__)
        self.__qhl.setContentsMargins(0, 0, 0, 0)
        self.knob_class_match_qcb = QtWidgets.QCheckBox('Match Knob Type',self.__)
        self.knob_class_match_qcb.setChecked(True)
        self.__qhl.addWidget(self.knob_class_match_qcb)
        self.target_knobs_toggle_qpb = QtWidgets.QPushButton('Show All',self.__)
        self.target_knobs_toggle_qpb.setCheckable(True)
        self.__qhl.addWidget(self.target_knobs_toggle_qpb)
        self.target_knobs_qvl.addWidget(self.__)
        self.__qhl.setStretch(1, 1)
 
        self.target_knobs_text_filter = QtWidgets.QLineEdit(self.target_knobs_qvl_widget)
        self.target_knobs_qvl.addWidget(self.target_knobs_text_filter)
        self.target_knobs_list = QtWidgets.QListWidget(self.target_knobs_qvl_widget)
        self.target_knobs_qvl.addWidget(self.target_knobs_list)
        self.lists_qhl.addWidget(self.target_knobs_qvl_widget)
        self.target_qvl.addWidget(self.lists_qhl_widget)
        self.connect_cmds_widget = QtWidgets.QWidget(self.target_qvl_widget)
        self.connect_cmds_qhl = QtWidgets.QHBoxLayout(self.connect_cmds_widget)
        self.connect_cmds_qhl.setContentsMargins(0, 0, 0, 0)
        self.connect_knobs_qpb = QtWidgets.QPushButton('Connect ->', self.connect_cmds_widget)
        self.connect_knobs_qpb.setMinimumSize(QtCore.QSize(0, 30))
        self.connect_cmds_qhl.addWidget(self.connect_knobs_qpb)
        self.copy_knobs_qpb = QtWidgets.QPushButton('Copy',self.connect_cmds_widget)
        self.copy_knobs_qpb.setMinimumSize(QtCore.QSize(0, 30))
        self.connect_cmds_qhl.addWidget(self.copy_knobs_qpb)
        self.target_qvl.addWidget(self.connect_cmds_widget)
 
        # self.main_input_qte = QtWidgets.QPlainTextEdit(self.target_qvl_widget)
        # self.main_input_qte.setFixedHeight(50)
        # self.main_input_qte.setEnabled(False)
        # self.target_qvl.addWidget(self.main_input_qte)
        # self.input_cmds_qhl_widget = QtWidgets.QWidget(self.target_qvl_widget)
        # self.input_cmds_qhl = QtWidgets.QHBoxLayout(self.input_cmds_qhl_widget)
        # self.input_cmds_qhl.setContentsMargins(0, 0, 0, 0)
        # self.enter_value_qpb = QtWidgets.QPushButton('Enter',self.input_cmds_qhl_widget)
        # self.enter_value_qpb.setEnabled(False)
        # self.enter_value_qpb.setMinimumSize(QtCore.QSize(0, 30))
        # self.input_cmds_qhl.addWidget(self.enter_value_qpb)
        # self.target_qvl.addWidget(self.input_cmds_qhl_widget)
        self.target_qvl.setStretch(0, 1)
        self._2_qhl.addWidget(self.target_qvl_widget)
        self._2_qhl.setStretch(1, 5)
        self._2_qhl.setStretch(0, 2)
        self._1_qvl.addWidget(self._2_qhl_widget)
 
        self.source = None
        self.source_knobs = None
        self.all_nodes = []
        self.all_knobs = []
        self.all_node_names = []
        self.all_node_classes = []
        self.installEventFilter(self)
        self.connect_signal()
 
    def connect_signal(self):
        self.load_connect_source_qpb.clicked.connect(self.load_source)
        self.select_source_qpb.clicked.connect(self.select_source)
 
        self.target_knobs_toggle_qpb.clicked.connect(self.toggle_target_knobs_mode)
        self.knob_class_match_qcb.clicked.connect(self.toggle_target_knobs_mode)
        self.target_name_qcb.clicked.connect(self.update_all)
        self.target_type_qcb.clicked.connect(self.update_all)
 
        self.source_knob_name_qle.textChanged.connect(self.update_source)
        self.target_name_qle.textChanged.connect(self.update_target_node_list)
        self.target_type_qle.textChanged.connect(self.update_target_node_list)
        self.target_knobs_text_filter.textChanged.connect(self.update_target_knobs_list)
        self.target_node_list.itemSelectionChanged.connect(self.update_target_knobs_list)
        self.source_knobs_list.itemSelectionChanged.connect(self.update_target_knobs_list)
 
        self.connect_knobs_qpb.clicked.connect(self.connect_knobs)
        self.copy_knobs_qpb.clicked.connect(self.copy_knobs)
 
    def enterEvent(self,event):
        """ Update on mouse entering """
        self.get_all_nodes()
        self.update_all()
 
    def eventFilter(self, object, event):
        """ Update on window active, even by keyboard switch """
        if event.type() == QtCore.QEvent.WindowActivate or event.type()== QtCore.QEvent.FocusIn:
            self.get_all_nodes()
            self.update_all()
            return True
        else:
            return False
 
    def display(self):
        self.show()
        self.raise_()
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
        self.get_all_nodes()
        self.update_all()
 
    def select_source(self):
        if self.source:
            nukescripts.clear_selection_recursive()
            self.source.setSelected(True)
 
    def match_knob_type(self, knob):
        """
        Test if given knob's type matches the selected source knob
        """
        sl = self.source_knobs_list.selectedItems()
        try:
            if sl and not knob.Class() == sl[0].n_knob.Class():
                return False
        except:
            return False
        return True
 
 
    def update_all(self):
        """
        Update all UI without reload self.all_nodes
        """
        self.update_source()
        self.update_target_node_list()
        self.update_target_knobs_list()
 
    def get_all_nodes(self):
        """
        Refresh all nodes attributes
        """
        self.all_nodes = nuke.allNodes()
        if not self.all_nodes:
            self.target_knobs_list.clear()
            self.target_node_list.clear()
            return
        if self.source:
            self.all_nodes.remove(self.source)
        self.all_nodes.sort(key=lambda x: x.name())
        self.all_knobs = [i.knobs() for i in self.all_nodes]
        self.all_node_classes = [i.Class() for i in self.all_nodes]
        self.all_node_names = [i.name() for i in self.all_nodes]
 
    @keep_selection('target_node_list')
    def update_target_node_list(self,*args,**kwargs):
        self.target_node_list.clear()
        if not self.all_nodes:
            self.get_all_nodes()
        node_names = list(self.all_node_names)
 
        # filter by the names and types
        if self.target_name_qcb.isChecked():
            line = self.target_name_qle.text()
            node_names = [i for i in node_names if match_filter(i, line)]
        if self.target_type_qcb.isChecked():
            line = self.target_type_qle.text()
            node_names = [i for i in node_names if match_filter(self.all_node_classes[self.all_node_names.index(i)], line)]
 
        # store all attribute with QListWidgetItem for faster access
        result_nodes = [(name,
                         self.all_nodes[self.all_node_names.index(name)],
                         self.all_node_classes[self.all_node_names.index(name)],
                         self.all_knobs[self.all_node_names.index(name)]) for name in node_names]
        result_nodes.sort(key=lambda x: x[0].lower()) # sort by name
        for c, node in enumerate(result_nodes):
            self.target_node_list.addItem(node[0])
            self.target_node_list.item(c).n_name = node[0]
            self.target_node_list.item(c).n_node = node[1]
            self.target_node_list.item(c).n_class = node[2]
            self.target_node_list.item(c).n_knobs = node[3]
        return node_names
 
    @keep_selection('target_knobs_list')
    def update_target_knobs_list(self,*args,**kwargs):
        # get selected QListWidgetItems and the knobs assigned with them
        target_nodes_widget = [self.target_node_list.item(c) for c in range(self.target_node_list.count())]
        selected_node_widget = [i for i in target_nodes_widget if i.isSelected()]
        if not selected_node_widget:
            return
        all_knobs_items = [i.n_knobs.items() for i in selected_node_widget]
        all_knob_keys = [[i[0] for i in items] for items in all_knobs_items]
        all_knob_objs = [[i[1] for i in items] for items in all_knobs_items]
 
        filtered_knob_keys, filtered_knob_objs, filtered_knob_class = [], {}, {}
        # all knobs
        if self.target_knobs_toggle_qpb.isChecked():
            for c, key in enumerate(all_knob_keys[0]):
                if all([key in others_keys for others_keys in all_knob_keys[1:]]):
                    filtered_knob_keys.append(key)
                    if not key in filtered_knob_objs.keys():
                        filtered_knob_objs[key] = []
                    # all knobs with same keys in selected target nodes
                    filtered_knob_objs[key]+=[widget.n_knobs.get(key,None) for widget in selected_node_widget]
        # only knobs that are common in all target nodes
        else:
            for c, keys in enumerate(all_knob_keys):
                for d, key in enumerate(keys):
                    if key not in filtered_knob_keys:
                        filtered_knob_keys.append(key)
                        if not key in filtered_knob_objs.keys():
                            filtered_knob_objs[key] = []
                        filtered_knob_objs[key]+=[widget.n_knobs.get(key,None) for widget in selected_node_widget]
 

         # take out duplicate knobs
        for key, knobs in filtered_knob_objs.items():
            filtered_knob_objs[key] = list(set(knobs))
 
        self.target_knobs_list.clear()
        # filter by text filter
        line = self.target_knobs_text_filter.text()
        if line:
            filtered_knob_keys = [key for key in filtered_knob_keys if match_filter(key, line)]
        if self.knob_class_match_qcb.isChecked():
            filtered_knob_keys = [key for key in filtered_knob_keys if filtered_knob_objs.get(key) and self.match_knob_type(filtered_knob_objs.get(key)[0])]
 
        # sort by name
        filtered_knob_keys.sort(key=lambda x: x.lower())
 
        # add to QListWidget
        for c, key in enumerate(filtered_knob_keys):
            self.target_knobs_list.addItem(key)
            self.target_knobs_list.item(c).n_knobs = filtered_knob_objs[key]
        return filtered_knob_keys
 
 
    def toggle_target_knobs_mode(self):
        text = {1:'Applicable',0:'All'}[self.target_knobs_toggle_qpb.isChecked()]
        self.target_knobs_toggle_qpb.setText(text)
        self.update_target_knobs_list()
 
 
    @classmethod
    def get_instance(cls):
        """ One instance per Nuke session """
        if not cls._instance:
            cls._instance = cls(parent=QtWidgets.QApplication.activeWindow())
        return cls._instance
 
 
    def connect_knobs(self):
        """ connect knob value by expression, 1 to multi """
        source_knobs = self.source_knobs_list.selectedItems()
        targets = self.target_knobs_list.selectedItems()
        if not source_knobs or not targets:
            return
        source_knob = source_knobs[-1].n_knob
        targets = [item for sublist in [i.n_knobs for i in targets] for item in sublist]
        # targets = [i.n_knobs for i in targets]
        for target in targets:
            exp = '{}.{}'.format(self.source.name(),source_knob.name())
            try:
                target.clearAnimated()
                target.setExpression(exp)
            except:
                print 'target {} fail to set expression'.format(target)
 
    def copy_knobs(self):
        """ Copy knob value, 1 to multi """
        source_knobs = self.source_knobs_list.selectedItems()
        targets = self.target_knobs_list.selectedItems()
        if not source_knobs or not targets:
            return
        source_knob = source_knobs[-1].n_knob
        value = source_knob.getValue()
        source_knob.clearAnimated()
        for target in targets:
            for knob in target.n_knobs:
                knob.clearAnimated()
                knob.setValue(value)
 
    def load_source(self):
        """ Load selected node into UI """
        selected = nuke.selectedNodes()
        if selected:
            self.source = nuke.selectedNodes()[-1]
            self.source_knobs = self.source.knobs()
            self.setWindowTitle(self.source.name())
            self.get_all_nodes()
            self.update_all()
 
 
    @keep_selection('source_knobs_list')
    def update_source(self,*args,**kwargs):
        self.source_knobs_list.clear()
        # try is prior to if node exists since delete node would cause value error
        try:
            self.source
        except:
            return
        if not self.source:
            return
        all_keys = self.source_knobs.keys()
        all_keys.sort(key=lambda x: x.lower())
        line = self.source_knob_name_qle.text()
        source_knob_keys = [i for i in all_keys if match_filter(i,line)] if line else all_keys
        for c, key in enumerate(source_knob_keys):
            self.source_knobs_list.addItems(source_knob_keys)
            self.source_knobs_list.item(c).n_knob = self.source_knobs[key]
 
        return source_knob_keys
 
 
def match_filter(source, line_string, full_text=True):
    line_string = [i.strip() for i in line_string.split(',')]
    line_string = [item.strip() for sublist in [i.split(' ') for i in line_string] for item in sublist if item.strip()]
    if full_text:
        line_string = ['*{}*'.format(i) for i in line_string]
    line_string = list(set(line_string))
    return all([fnmatch(source.lower(), string.lower()) for string in line_string])
 
def main():
    win = MainWindow.get_instance()
    win.display()
    return win
 
if __name__ == '__main__':
    win = main()
