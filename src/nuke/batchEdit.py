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
    ('Grade',): 'white',
    ('ColorCorrect',): 'gain',
    ('Multiply',): 'value',
    ('Merge2',): 'operation',
    ('Transform',): 'translate',
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
        self.warning_knob = nuke.Text_Knob('warning',
                                           '<span style="color:red">select nodes to edit</span>')
        self.font_knob = nuke.Enumeration_Knob('font', 'font', [''])
        self.font_style_knob = nuke.Enumeration_Knob('font_style', 'font style', ['Regular'])
        self.setMinimumSize(500, 120)

        self.addKnob(self.main_knob)
        self.addKnob(self.warning_knob)
        self.warning_knob.clearFlag(nuke.STARTLINE)
        self.warning_knob.setVisible(False)
        self.addKnob(self.edit_knob)
        self.split_knob = nuke.PyScript_Knob('split', 'xyz/rgba')
        self.addKnob(self.split_knob)
        self.split_knob.clearFlag(nuke.STARTLINE)
        self.addKnob(self.new_value_knob)

        self.new_knob0 = nuke.String_Knob('new value  x/r')
        self.new_knob1 = nuke.String_Knob('y/g')
        self.new_knob2 = nuke.String_Knob('z/b')
        self.new_knob3 = nuke.String_Knob('a')

        self.addKnob(self.new_knob0)
        self.addKnob(self.new_knob1)
        self.addKnob(self.new_knob2)
        self.addKnob(self.new_knob3)
        self.addKnob(self.font_knob)
        self.addKnob(self.font_style_knob)
        self.font_style_knob.clearFlag(nuke.STARTLINE)
        self.addKnob(self.clear_expression_knob)

        self.new_knob1.clearFlag(nuke.STARTLINE)
        self.new_knob1.clearFlag(nuke.STARTLINE)
        self.new_knob2.clearFlag(nuke.STARTLINE)
        self.new_knob3.clearFlag(nuke.STARTLINE)
        self.clear_expression_knob.setFlag(nuke.STARTLINE)

        self.new_knob0.setVisible(False)
        self.new_knob1.setVisible(False)
        self.new_knob2.setVisible(False)
        self.new_knob3.setVisible(False)
        self.font_knob.setVisible(False)
        self.font_style_knob.setVisible(False)
        self.addKnob(self.pull_down_knob)
        self.pull_down_knob.setVisible(False)
        self.get_knobs()
        self.build_fonts_dict()

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

        if not len(nodes):
            nuke.message("nothing selected")
            self.warning_knob.setVisible(True)
            return

        knobs = nodes[0].knobs()
        for node in nodes[1:]:
            knobs = knobs_intersect(knobs, node.knobs())

        knobs = knobs.keys()
        knobs.sort()

        if nodes[-1].Class() == 'Text2':
            self.main_knob.setValue('font')

        self.main_knob.setValues(knobs)

        # Insert fonts to the font knob
        self.font_knob.setValues(sorted(self.build_fonts_dict()))

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

    def knobChanged(self, knob):

        selectedKnob = self.main_knob.value()
        self.pull_down_knob.setVisible(False)
        newKnobs = [self.new_value_knob, self.new_knob0, self.new_knob1, self.new_knob2,
                    self.new_knob3]

        if selectedKnob == 'font':
            """
            When font knob is select, hide all other knobs
            """
            if not self.font_knob.visible():
                self.font_knob.setVisible(True)
                self.font_style_knob.setVisible(True)
                for knob in newKnobs:
                    knob.setVisible(False)

                self.edit_knob.setVisible(False)
                self.split_knob.setVisible(False)
                self.clear_expression_knob.setVisible(False)

        elif knob.name() == 'split':
            """
            When split 'xyz/xy' is click, hide string input
            """
            if self.new_value_knob.visible():
                self.new_value_knob.setVisible(False)
                for knob in newKnobs[1:]:
                    knob.setVisible(True)
                self.font_knob.setVisible(False)

            else:
                self.new_value_knob.setVisible(True)
                for knob in newKnobs[1:]:
                    knob.setVisible(False)
                self.font_knob.setVisible(False)

        else:
            [newKnobs[0].setVisible(True) if newKnobs[1].visible() != True else None]
            self.font_knob.setVisible(False)
            self.font_style_knob.setVisible(False)
            self.edit_knob.setVisible(True)
            self.split_knob.setVisible(True)
            self.clear_expression_knob.setVisible(False)

        if knob.name() == 'font':
            self.font_style_knob.setValues(self.build_fonts_dict()[self.font_knob.value()])

        node = nuke.selectedNodes()[-1]
        current_value = node[selectedKnob]
        if selectedKnob:
            if any(word in node[selectedKnob].Class() for word in _PULL_DOWN_CLASSES):

                if not self.pull_down_knob.visible():
                    self.pull_down_knob.setVisible(True)
                    new_list = current_value.values()
                    new_list.insert(0, current_value.value())
                    self.pull_down_knob.setValues(new_list)
                    # self.pulldownKnob.setValue(node[selectedKnob].value())
                    self.new_value_knob.setVisible(False)
                    self.split_knob.setVisible(False)
                    pass

            elif any(word in node[selectedKnob].Class() for word in _CHANNEL_CLASSES):
                if not self.pull_down_knob.visible():
                    self.pull_down_knob.setVisible(True)
                    channel_list = list(self.get_root_channels())
                    channel_list.insert(0, current_value.value())
                    self.pull_down_knob.setValues(channel_list)

                    self.new_value_knob.setVisible(False)
                    self.split_knob.setVisible(False)
                    pass

            elif selectedKnob == 'format':
                self.new_value_knob.setVisible(False)
                self.split_knob.setVisible(False)
                self.pull_down_knob.setVisible(True)
                format_list = [i.name() for i in nuke.formats()]

                format_list.insert(0, "%s %sx%s" % (
                current_value.value().name(), current_value.value().width(),
                current_value.value().height()))
                self.pull_down_knob.setValues(format_list)

                pass

            else:
                # self.newValue.setVisible(True)
                # self.split_knob.setVisible(True)
                pass

    def set_default_value(self, nodes):
        """
        set default knob for certain node
        """
        if nodes:
            node = nodes[-1]
            node_class = node.Class()
            if node_class in ['Text', 'Text2']:
                self.main_knob.setValue('font')
                self.font_knob.setValue(node['font'].getValue()[0])
                self.font_style_knob.setValue(node['font'].getValue()[1])

            elif node_class in _CLASS_VALUE_MAP:
                self.main_knob.setValue(_CLASS_VALUE_MAP[node_class])

    def show_modal_dialog(self):

        nodes = nuke.selectedNodes()
        if len(nodes):
            self.set_default_value(nodes)

        show = nukescripts.PythonPanel.showModalDialog(self)

        if self.new_value_knob.visible():
            new_val = self.new_value_knob.getValue()

        elif self.pull_down_knob.visible():
            new_val = self.pull_down_knob.value()
        else:
            new_val = [self.new_knob0.getValue(), self.new_knob1.getValue(),
                       self.new_knob2.getValue(), self.new_knob3.getValue()]
            new_val = [x if x else None for x in new_val]

        is_expr = self.edit_knob.getValue()
        clear = self.clear_expression_knob.getValue()

        if show:
            self.change_knob_value(new_val, is_expr, clear, nodes)

        return show

    def change_knob_value(self, new_val, is_expr, clear, nodes):
        knob = self.main_knob.value()
        split = not bool(self.new_value_knob.visible())
        title = nukescripts.goofy_title()
        val = 0
        if is_expr:
            print("edit expression")
            for node in nodes:
                if clear:
                    node.knob(knob).clearAnimated()
                try:
                    if split:
                        for step, val in enumerate(new_val):
                            if val is not None:
                                node.knob(knob).setSingleValue(False)
                                node.knob(knob).setExpression(new_val[step], step)
                                print("{} {} {}".format(node.name(), val, step))

                    else:
                        node.knob(knob).setSingleValue(True)
                        node.knob(knob).setExpression(new_val)

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
                                new_val = self.font_knob.value()
                                new_style = self.font_style_knob.value()
                                node.knob('font').setValue(new_val, new_style)
                                print("{} {} {}".format(node.name(), new_val, new_style))

                            elif node.Class() == 'Text':
                                new_val = self.build_fonts_dict()[self.font_knob.value()][1]
                                new_style = self.font_style_knob.value()
                                node.knob('font').setValue(new_val)
                                node.knob('index').setValue(new_style)
                                print(node.name())

                            else:
                                node.knob('font').setValue(new_val)

                        if knob == 'format':
                            node.knob(knob).setValue(new_val)

                        if new_val_type == str:
                            if knob != 'name':
                                node.knob(knob).setValue(str(new_val))
                            if knob == 'name':
                                val += 1
                                node.knob('name').setValue('%s_%s' % (new_val, str(val)))
                                print("new name: {}_{}".format(new_val, str(val)))
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
                            node.knob(knob).setSingleValue(True)
                            node.knob(knob).setValue(float(new_val))
                        if new_val_type == float:
                            node.knob(knob).setValue(float(new_val))
                        if new_val_type == int:
                            node.knob(knob).setValue(int(new_val))
                        if new_val_type == unicode:
                            node.knob(knob).setValue(unicode(new_val))
                        if new_val_type == tuple:
                            node.knob(knob).setValue(float(new_val))

                        if new_val_type == bool:
                            node.knob(knob).setValue(float(new_val))
                    except:
                        # nuke.message('error while editing new value')
                        continue

                except:
                    pass

        # print edited node and knob informations
        print([node.name() for node in nodes])
        print('Edited knob: {}'.format(knob))
        print('new value is: {}'.format(new_val))
        print('is expression: {}'.format(is_expr))


def show_dialog():
    return BatchEdit().show_modal_dialog()


if __name__ == '__main__':
    _BatchEdit_UI = show_dialog()
