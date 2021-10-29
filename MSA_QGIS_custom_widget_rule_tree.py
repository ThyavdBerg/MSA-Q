from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QSizePolicy, QPushButton, QHBoxLayout, QFrame, QComboBox
from qgis.PyQt import QtGui, QtCore, QtWidgets
from qgis.utils import iface


class RuleTreeWidget(QFrame):
    """ A custom widget that functions as a spoiler widget and can be placed in a rule tree with other ruleTreeWidgets
    parent: QWidget"""
    clicked = pyqtSignal()
    def __init__(self, nest_dict_rule, order_id, next_layout= None, own_layout = None, connection_type ='normal', prev_ruleTreeWidgets = None, next_ruleTreeWidgets = None, duplicate_ruleTreeWidgets = None, main_dialog_x=1, main_dialog_y=1, parent = None):
        super(RuleTreeWidget, self).__init__(parent)
        ### variables before UI
        self.nest_dict_rule = nest_dict_rule
        self.order_id = order_id
        if prev_ruleTreeWidgets == None:
            self.prev_ruleTreeWidgets = []
        else:
            self.prev_ruleTreeWidgets = prev_ruleTreeWidgets
        if next_ruleTreeWidgets == None:
            self.next_ruleTreeWidgets = []
        else:
            self.next_ruleTreeWidgets = next_ruleTreeWidgets
        if duplicate_ruleTreeWidgets == None:
            self.duplicate_ruleTreeWidgets = []
        else:
            self.duplicate_ruleTreeWidgets = duplicate_ruleTreeWidgets
        self.connection_type = connection_type
        self.next_ruleTreeWidgets = []
        self.main_dialog_x = main_dialog_x
        self.main_dialog_y = main_dialog_y
        self.isSelected = False
        self.isBaseGroup = False
        self.next_layout = next_layout
        self.own_layout = own_layout


        #setup UI
        self.setupUI()

        #variables after UI
        self.written_rule = self.nest_dict_rule[self.comboBox_name.currentText()][1]

        ### events
        self.comboBox_name.currentTextChanged.connect(self.changeToolTip)

    def setupUI(self):
        """ Creates the UI component"""
        ### Construct the thing
        self.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum))

        self.setStyleSheet("background-color: #c3c3c3;"
                           "border: 2px outset #5b5b5b;")

        self.comboBox_name = RuleTreeComboBox(self.nest_dict_rule)
        self.hLayout = QHBoxLayout()
        self.hLayout.setContentsMargins(3,3,3,3)
        self.hLayout.addWidget(self.comboBox_name)
        self.setLayout(self.hLayout)
        self.setToolTip(self.nest_dict_rule[self.comboBox_name.currentText()][1])


    def toggleBaseGroup(self):
        """ Toggles whether the rule is part of a base group. Function is only available for rules with 100% chance to
        happen, that have no prev_ruleTreeWidgets or 1 prev_ruleTreeWidget that also has base_group = True"""
        if self.nest_dict_rule[self.comboBox_name.currentText()][4] == 100.0:
            if len(self.next_ruleTreeWidgets) <= 1:
                if self.isSelected == True and self.isBaseGroup == False:
                    self.isBaseGroup = True
                    self.setStyleSheet("background-color: #c37676;"
                                       "border: 3px outset #5b3737;")
                    self.isSelected = False
                elif self.isSelected == True and self.isBaseGroup == True:
                    self.isBaseGroup = False
            else:
                iface.messageBar().pushMessage("Error", "cannot add rule with multiple branches to base group",
                                               level=1)  # TODO replace with popup once I have the energy
                return # exit function
        else:
            self.isBaseGroup = False
            iface.messageBar().pushMessage("Error", "cannot add rule with less than 100% chance to base group",
                                           level=1)  # TODO replace with popup once I have the energy



    def changeToolTip(self):
        self.setToolTip(self.nest_dict_rule[self.comboBox_name.currentText()][1])


    def mouseReleaseEvent(self, event):
        """ connect the clicked signal to a mouseReleaseEvent, so that it emits when the widget is clicked"""
        self.clicked.emit()


class RuleTreeComboBox(QComboBox):
    """ Creates the label with the rule number in it"""
    def __init__(self, nest_dict_rule, parent = None):
        super(RuleTreeComboBox, self).__init__(parent)
        self.nest_dict_rule = nest_dict_rule
        #setup UI
        self.setupUI()

    def setupUI(self):
        # this scaling works so long as you don't change text size or resolution halfway
        width = self.minimumSizeHint().width()
        height = self.minimumSizeHint().height()
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        self.setStyleSheet('border: 1px;')
        for item in self.nest_dict_rule:
            self.addItem(item)

    def changeItemList(self):
        list_current_items = []
        for index in range(self.count()):
            list_current_items.append(self.itemText(index))
        for item in self.nest_dict_rule:
            if item not in list_current_items:
                self.addItem(item)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.changeItemList()



