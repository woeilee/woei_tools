# -*- coding: utf-8
# BatchEdit.py

import nuke
import nukescripts

_PULL_DOWN_CLASSES = ["Enumeration_Knob", "Pulldown_Knob"]

_CHANNEL_CLASSES = [
    "ChannelSet_Knob",
    "ChannelMask_Knob",
    "Input_ChannelSet_Knob",
    "Input_ChannelMask_Knob",
    "Channel_Knob",
    "Input_Channel_Knob"
]

_CLASS_VALUE_MAP = {
    ('Blur', 'Dilate', 'Erode', 'FilterErode', 'ZBlur'): 'size',
    ('Crop',): 'box',
    ('ColorCorrect',): 'gain',
    ('Grade',): 'white',
    ('Multiply',): 'value',
    ('Merge2',): 'operation',
    ('Transform','Axis2', 'Camera2',): 'translate',
    ('Reformat',): 'format',

}
_CLASS_VALUE_MAP = {k: value for keys, value in _CLASS_VALUE_MAP.items() for k in keys}


class BatchEdit(nukescripts.PythonPanel):

    def __init__(self):
        nukescripts.PythonPanel.__init__(self, 'Woei Lee Batch Edit', '')
        """
        Defining Knobs
        """

        self.main_knob = nuke.Enumeration_Knob('knob', 'knob', [''])
        self.edit_knob = nuke.Enumeration_Knob('edit', 'edit in', ['value', 'expression'])
        self.new_value_knob = nuke.String_Knob('value', 'new value')
        self.pull_down_knob = nuke.Enumeration_Knob('value', 'new value', [''])
        self.clear_expression_knob = nuke.Boolean_Knob('clear', 'clear current expression ')
        self.warning_knob = nuke.Text_Knob(
            'warning', '<span style="color:red">select nodes to edit</span>'
        )
        self.format_knob = nuke.Format_Knob('format','new format')
        self.font_knob = nuke.FreeType_Knob('font','font')
        self.note_font_knob = nuke.Font_Knob('font','font')
        self.rgba_color_knob = nuke.AColor_Knob('values', 'new value')
        self.wh_knob = nuke.WH_Knob('values', 'new value')
        self.xy_knob = nuke.XY_Knob('values', 'new value')
        self.xyz_knob = nuke.XYZ_Knob('values', 'new value')
        self.double_knob = nuke.Double_Knob('values','new value')
        self.scale_knob = nuke.Scale_Knob('values','new value')
        self.color_knob = nuke.ColorChip_Knob('color','new color')
        self.disable_knob = nuke.Disable_Knob('disable','disable')
        self.checkbox_knob = nuke.Boolean_Knob('checkbox','select')
        self.channel_knob = nuke.ChannelMask_Knob('channels', 'select channels')
        self.update_knob = nuke.PyScript_Knob('update', '   update value to knob   ')
        self.bbox_knob = nuke.BBox_Knob('bbox','bbox')

        self.setMinimumSize(500, 220)

        self.addKnob(self.main_knob)
        self.addKnob(self.checkbox_knob)
        self.addKnob(self.warning_knob)
        self.warning_knob.clearFlag(nuke.STARTLINE)
        self.warning_knob.setVisible(False)
        self.addKnob(self.edit_knob)
        self.addKnob(self.new_value_knob)
        self.addKnob(self.channel_knob)
        self.channel_knob.setLabel("Channels")
        self.addKnob(self.format_knob)
        self.addKnob(self.font_knob)
        self.addKnob(self.note_font_knob)
        self.addKnob(self.pull_down_knob)
        self.addKnob(self.rgba_color_knob)
        self.addKnob(self.xy_knob)
        self.addKnob(self.xyz_knob)
        self.addKnob(self.wh_knob)
        self.addKnob(self.bbox_knob)
        self.addKnob(self.double_knob)
        self.addKnob(self.scale_knob)
        self.addKnob(self.color_knob)
        self.addKnob(self.update_knob)
        self.addKnob(self.disable_knob)
        self.addKnob(self.clear_expression_knob)

        self.disable_knob.setFlag(nuke.STARTLINE)
        self.update_knob.clearFlag(nuke.STARTLINE)

        self.checkbox_knob.setVisible(False)
        self.format_knob.setVisible(False)
        self.channel_knob.setVisible(False)
        self.disable_knob.setVisible(False)
        self.font_knob.setVisible(False)
        self.note_font_knob.setVisible(False)
        self.rgba_color_knob.setVisible(False)
        self.xy_knob.setVisible(False)
        self.xyz_knob.setVisible(False)
        self.wh_knob.setVisible(False)
        self.bbox_knob.setVisible(False)
        self.double_knob.setVisible(False)
        self.scale_knob.setVisible(False)
        self.color_knob.setVisible(False)
        self.pull_down_knob.setVisible(False)

        self.get_nodes()
        self.get_knobs()
        self.build_fonts_dict()

    ################################# get information before panel initiate #################################

    def get_nodes(self):
        nodes = nuke.selectedNodes()

        return nodes

    def get_knobs(self):
        """
        Get all the knobs on all the selectedNodes
        """

        def knobs_intersect(knobs_a, knobs_b):
            intersection = dict()

            for name, knob in knobs_a.items():
                if knobs_b.has_key(name) and knobs_b[name].Class() == knob.Class():
                    intersection[name] = knob

            return intersection

        nodes = nuke.selectedNodes()
        for node in nodes:
            if node.Class() == "Group":
                n = nuke.toNode(node.name())
                n.begin()

        if not nodes:
            nuke.message("Nothing selected!")
            self.warning_knob.setVisible(True)
            return

        knobs = nodes[0].knobs()
        for node in nodes[1:]:
            knobs = knobs_intersect(knobs, node.knobs())

        knobs = knobs.keys()
        knobs.sort()
        # remove _panelDropped for now, will think of how to handle it later
        for knob in knobs:
            if  knob.endswith('_panelDropped'):
                knobs.remove(knob)

        if nodes[-1].Class() == 'Text2':
            self.main_knob.setValue('font')

        self.main_knob.setValues(knobs)

        # Insert fonts to the font knob
        # self.font_knob.setValues(sorted(self.build_fonts_dict()))

    def get_root_channels(self):
        """
        Get all the available Channels from the script root
        """
        channels = []
        for i in nuke.root().channels():
            value = i.split('.')[0]
            if value in channels:
                continue
            channels.append(value)

        return channels

    ################################# building lists and dictionaries #################################



    def build_fonts_dict(self):
        """
        Print the font family and styles form the font manifest files
        """

        from subprocess import PIPE, Popen

        font_dict = {}
        proc = Popen(["fc-list"], stdout=PIPE)
        for line in proc.stdout:
            _, name, elements = line.split(":")
            font_dict.setdefault(
                name.strip().split(',')[0], []).extend(
                elements.strip().replace('style=', '').split(',')
            )

        return font_dict

    def replacing_knobs(self):
        replacing_knobs = [
            self.rgba_color_knob,
            self.wh_knob,
            self.xy_knob,
            self.xyz_knob,
            self.double_knob,
            self.checkbox_knob,
            self.scale_knob,
            self.color_knob,
            self.bbox_knob
        ]

        return replacing_knobs

    def single_input_knobs(self):
        pulldowns = [
            self.pull_down_knob,
            self.format_knob,
            self.font_knob,
            self.note_font_knob,
            self.channel_knob
        ]

        return pulldowns

    def extra_knobs(self):
        return [self.edit_knob]

    def font_family(self):
        font_family = [self.font_knob,]
        return font_family

    ################################# panel instantiate methods #################################

    def set_default_value(self, nodes):
        """
        set default knob for certain node selection
        """
        if nodes:
            node = nodes[-1]
            node_class = node.Class()
            if node_class in ['Text','Text2']:
                self.main_knob.setValue('font')
                self.font_knob.setValue(*node['font'].getValue()) if node_class == 'Text2' else None
            elif node_class in _CLASS_VALUE_MAP:
                self.main_knob.setValue(_CLASS_VALUE_MAP[node_class])

    def show_modal_dialog(self):
        """ show panel """
        nodes = nuke.selectedNodes()
        if len(nodes):
            self.set_default_value(nodes)
            show = nukescripts.PythonPanel.showModalDialog(self)
            if show:
                self.get_new_values(nodes)

    ################################# knobChanged operation on panel #################################

    def default_panel_knob(self, node, selected_knob):
        """
        default knob visibility
        """
        if not self.new_value_knob.visible():
            self.new_value_knob.setVisible(True)
            if node[selected_knob].Class() in [x.Class() for x in self.replacing_knobs()]:
                for knob in self.extra_knobs():
                    knob.setVisible(True)

        for knob in self.single_input_knobs() + self.replacing_knobs() + self.font_family() + [self.disable_knob]:
            knob.setVisible(False)

    def font_selected(self):
        """
        When font knob is select, hide all other knobs
        """
        for knob in [self.font_knob, self.note_font_knob]:
            if knob.Class() in [nuke.selectedNodes()[-1][self.main_knob.value()].Class(), "File_Knob"]:
                knob.setVisible(True)
                font_visible = knob.visible()
  
        if not font_visible:
            disabling_knobs = self.single_input_knobs() + self.replacing_knobs()
            disabling_knobs += [self.new_value_knob] + self.extra_knobs()

            for knob in disabling_knobs:
                knob.setVisible(font_visible)
            for f_knob in self.font_family():
                f_knob.setVisible(not font_visible)

        elif [knob.visible() == True for knob in self.single_input_knobs()]:
            self.new_value_knob.setVisible(False)
            for r_knob in self.replacing_knobs():
                r_knob.setVisible(False)

    def box_selected(self):
        """
        when box knob is select, hide all other knobs
        """
        if not self.bbox_knob.visible():
            disabling_knobs = self.single_input_knobs() + self.replacing_knobs()
            disabling_knobs += [self.new_value_knob] + self.extra_knobs()
            for knob in disabling_knobs:
                knob.setVisible(False)

            self.bbox_knob.setVisible(True)

    def format_selected(self):
        """
        When 'format' is selected on main_knob
        """
        self.new_value_knob.setVisible(not self.main_knob.value() == 'format')
        self.format_knob.setVisible(not self.new_value_knob.visible())

        for knob in self.extra_knobs():
            knob.setVisible(False)
        self.clear_expression_knob.setVisible(False)
        self.update_knob.clearFlag(nuke.STARTLINE)

    def on_checkbox_clicked(self, nodes, knob, selected_knob):
        """
        When checkbox is selcted on
        main_knob, change main_knob to boolean checkbox,
        when the checkbox is clicked update nodes instantly
        """
        for f_knob in self.font_family() + self.single_input_knobs() + self.replacing_knobs():
            f_knob.setVisible(False)
        self.checkbox_knob.setFlag(nuke.KNOB_CHANGED_RECURSIVE)
        edits_expression = self.edit_knob.value() == 'expression'
        self.new_value_knob.setVisible(edits_expression)
        self.disable_knob.setVisible(selected_knob == 'disable')
        self.disable_knob.setVisible(not edits_expression)
        self.checkbox_knob.setVisible(not edits_expression)
        self.checkbox_knob.setVisible(not selected_knob == 'disable')
        self.checkbox_knob.clearFlag(nuke.KNOB_CHANGED_RECURSIVE)

        split = None
        is_expr = self.edit_knob.getValue()
        clear = int(self.clear_expression_knob.getValue())

        # pass new values to selected nodes
        if knob.name() == 'disable': ### real time update on clicks
            new_val = self.disable_knob.getValue()
            self.update_knob_value(new_val, split, is_expr, clear, nodes)
        if knob.name() == 'checkbox': ### real time update on clicks
            new_val = self.checkbox_knob.getValue()
            self.update_knob_value(new_val, split, is_expr, clear, nodes)


    def color_chip_selected(self, node, selected_knob):
        """
        when color chip is selected, change knob to ColorChip_Knob
        """
        self.color_knob.setVisible(True)
        self.color_knob.setLabel(node[selected_knob].name())
        self.replacing_knobs().remove(self.color_knob)

        disabling_knobs = self.font_family() + self.single_input_knobs()
        disabling_knobs += self.replacing_knobs()
        disabling_knobs += [self.disable_knob, self.checkbox_knob , self.new_value_knob]
        for knob in disabling_knobs:
            knob.setVisible(False)

    def pulldown_selected(self, node, selected_knob, current_value):
        """
        if the selected knob is a pulldown,
        hide main_knob and replace with pulldown
        """
        self.channel_knob.setLabel('channels')
        if any(word in node[selected_knob].Class() for word in _PULL_DOWN_CLASSES):
            if not self.pull_down_knob.visible():
                for knob in self.single_input_knobs() + self.extra_knobs() + self.replacing_knobs():
                    knob.setVisible(False)
                self.new_value_knob.setVisible(False)
                self.pull_down_knob.setVisible(True)
                self.pull_down_knob.setLabel(selected_knob)
                new_list = current_value.values()
                new_list.insert(0, current_value.value())
                self.pull_down_knob.setValues(new_list)

        elif any(word in node[selected_knob].Class() for word in _CHANNEL_CLASSES):
            self.single_input_knobs().remove(self.channel_knob)
            self.new_value_knob.setVisible(False)
            for knob in self.single_input_knobs() + self.extra_knobs() + self.replacing_knobs():
                knob.setVisible(False)
            if not self.channel_knob.visible():
                self.channel_knob.setVisible(not self.new_value_knob.visible())

                pass

    def knobChanged(self, knob):
        nodes = self.get_nodes()
        node = self.get_nodes()[-1]
        selected_knob = self.main_knob.value()
        current_value = node[selected_knob]
        self.pull_down_knob.setVisible(False)
        self.checkbox_knob.setLabel(selected_knob)

        """ default knob visibility """
        if nodes[-1][selected_knob].Class() in [
            'Array_Knob', 'String_Knob','EvalString_Knob',
            'Multiline_Eval_String_Knob', 'Obsolete_Knob'
        ] or self.edit_knob.value() == 'expression':
            self.new_value_knob.setVisible(True)
            self.format_knob.setVisible(not(bool(self.new_value_knob.visible())))
            for r_knob in self.single_input_knobs() + self.extra_knobs() + self.replacing_knobs():
                r_knob.setVisible(
                    not(bool(self.new_value_knob.visible()))
                )

        # hide string knob if selection Class is in replacing_knobs
        elif nodes[-1][selected_knob].Class() in [r_knob.Class() for r_knob in self.replacing_knobs()]:
            self.new_value_knob.setVisible(False)
            for r_knob in self.replacing_knobs():
                r_knob.setVisible(bool(self.new_value_knob.visible()))
                if r_knob.Class() == nodes[-1][selected_knob].Class():
                    r_knob.setVisible(not(bool(self.new_value_knob.visible())))

        else:
            self.new_value_knob.setVisible(True)
            self.checkbox_knob.setVisible(not self.new_value_knob.visible())

        # When font knob is select, hide all other knobs
        if selected_knob == 'font' or nodes[-1][selected_knob].Class() == 'Font_Knob':
            self.font_selected()

        # when format is selected, change main_knob to channel pulldown
        elif selected_knob == 'format':
            self.format_selected()

        elif selected_knob == 'box':
            self.box_selected()

        # when disable or boolean is selected, change main_knob to Disable_Knob
        elif nodes[-1][selected_knob].Class() in ['Disable_Knob','Boolean_Knob']:
            self.on_checkbox_clicked(nodes, knob, selected_knob)

        # when selected knob is a pull down, change main_knob to pulldown
        elif self.pull_down_knob or self.channel_knob:
            self.pulldown_selected(node, selected_knob, current_value)

        # when update knob is click, update knob values but keep panel open
        if knob.name() in ['update', 'disable']:
            self.get_new_values(nodes)


    ################################# execute new values to selectedNodes #################################

    def get_new_values(self, nodes):
        """ get new value on panel """
        split = None ### to detect if the single input knob has been split
        for knob in [self.pull_down_knob, self.channel_knob,  self.format_knob]:
            if knob.visible():
                new_val = knob.value()

        for knob in [self.new_value_knob, self.font_knob,]:
            if knob.visible():
                try:
                    new_val = knob.getValue()
                except ValueError:
                    print('Invalid Value')

        for knob in [self.color_knob, self.note_font_knob]:
            if knob.visible():
                new_val = knob.value()

        for r_knob in self.replacing_knobs():
            if r_knob.visible():
                split = not bool(r_knob.singleValue())
                new_val = r_knob.value()
                if isinstance(new_val, list):
                    new_val = [x if x else None for x in new_val]

        for c_knob in [self.disable_knob,self.checkbox_knob]:
            if c_knob.visible():
                new_val = bool(c_knob.getValue())

        is_expr = self.edit_knob.getValue()
        clear = int(self.clear_expression_knob.getValue())

        # pass new values to selected nodes
        self.update_knob_value(new_val, split, is_expr, clear, nodes)

    def update_knob_value(self, new_val, split, is_expr, clear, nodes):
        """ execute batch edit on multiple nodes in the selection """
        knob = self.main_knob.value()
        title = nukescripts.goofy_title()
        val = 0

        if is_expr:
            print("edit expression", '%s: %s'%(knob, new_val))
            for node in nodes:
                if clear:
                    node.knob(knob).clearAnimated()
                try:
                    if split:
                        for step, val in enumerate(new_val):
                            if val is not None:
                                node.knob(knob).setSingleValue(False)
                    else:
                        node.knob(knob).setSingleValue(True)
                        node.knob(knob).setExpression(str(new_val))
                except:
                    nuke.message("error while setting expression: \n\n" + title)
        else:
            print('Edit values')
            for node in nodes:
                if clear:
                    node.knob(knob).clearAnimated()
                try:
                    new_val_type = type(node.knob(knob).value())

                    try:
                        if knob == 'font':  # <<<< Text Node here
                            if node.Class() == 'Text2':
                                node.knob('font').setValue(*new_val)
                                print("{} {} {}".format(node.name(), new_val))

                            elif node.Class() == 'Text':
                                new_styles = self.build_fonts_dict()[new_val[0]]
                                new_style = new_val[1]
                                node.knob('font').setValue(new_val[0])
                                node.knob('index').setValue(new_styles.index(new_style))
                                print(node.name())

                            elif node[knob].Class() == Font_Knob:
                                node.knob('note_font').setValue(new_val)

                        elif new_val_type == str:
                            if knob != 'name':
                                node.knob(knob).setValue(str(new_val))
                            if knob == 'name':
                                val += 1
                                node.knob('name').setValue('%s_%s' % (new_val, str(val)))
                                print("new name: {}_{}".format(new_val, str(val)))
                        if knob == 'format':
                            new_val = new_val.name()
                            node.knob(knob).setValue(new_val)

                        if new_val_type == list or new_val_type == tuple or new_val_type == float:
                            if split:
                                try:
                                    for step, val in enumerate(new_val):
                                        if val is None:
                                            continue
                                        else:
                                            node.knob(knob).setValue(float(val), step)
                                except:
                                    raise 'error while editing new value'
                            else:
                                node.knob(knob).setValue(float(new_val))
                                node.knob(knob).setValue(str(new_val))
                        else:
                            node.knob(knob).setSingleValue(True)
                            node.knob(knob).setValue(float(new_val))
                        if new_val_type == float:
                            node.knob(knob).setValue(float(new_val))
                            if new_val == "all":
                                node.knob(knob).setValue('all')
                        elif new_val_type == int:
                            node.knob(knob).setValue(int(new_val))
                        elif new_val_type == unicode:
                            node.knob(knob).setValue(unicode(new_val))
                        elif new_val_type == tuple:
                            node.knob(knob).setValue(float(new_val))
                        elif new_val_type == bool:
                            node.knob(knob).setValue(float(new_val))
                        else:
                            node.knob(knob).setValue(new_val_type(new_val))
                    except:
                        # nuke.message('error while editing new value')
                        continue

                except ValueError:
                    nuke.message('error while editing new value')
                    pass

        # # print edited node and knob informations
        # print([node.name() for node in nodes])
        # print('Edited knob: {}'.format(knob))
        # print('new value is: {}'.format(new_val))
        # print('is expression: {}'.format(is_expr))


def show_dialog():
    ui = BatchEdit()
    ui.show_modal_dialog()
    return ui


if __name__ == '__main__':
    _BatchEdit_UI = show_dialog()
