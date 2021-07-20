from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QSizePolicy, QPushButton, QHBoxLayout, QFrame, QComboBox
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
        self.selectedRule = self.comboBox_name.currentText()
        self.written_rule = self.nest_dict_rule[self.selectedRule][1]
        self.spoilerplate = RuleTreeSpoilerPlate(self.nest_dict_rule, self.comboBox_name.currentText()) #just so that the first if statement in toggling the spoilerplate doesn't flip out

        ### events
        self.toggleButton.clicked.connect(self.toggleShowWrittenRule)

    def setupUI(self):
        """ Creates the UI component"""
        ### Construct the thing
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setMaximumSize(100, 30)
        self.setMinimumSize(100, 30)
        self.setStyleSheet("background-color: #c3c3c3;"
                           "border: 2px outset #5b5b5b;")


        self.toggleButton = RuleTreeToggleButton()
        self.toggleButton.setStyleSheet("background-color: #c3c3c3;"
                                        "border: 2px outset #5b5b5b;")
        self.comboBox_name = RuleTreeComboBox(self.nest_dict_rule)
        self.hLayout = QHBoxLayout()
        self.hLayout.setContentsMargins(0,0,0,0)
        self.hLayout.addWidget(self.toggleButton)
        self.hLayout.addWidget(self.comboBox_name)
        self.setLayout(self.hLayout)


    def toggleBaseGroup(self):
        """ Toggles whether the rule is part of a base group. Function is only available for rules with 100% chance to
        happen, that have no prev_ruleTreeWidgets or 1 prev_ruleTreeWidget that also has base_group = True"""
        if self.nest_dict_rule[self.selectedRule][4] == 100.0:
            if len(self.next_ruleTreeWidgets) <= 1:
                if self.isSelected == True and self.isBaseGroup == False:
                    self.isBaseGroup = True
                    self.setStyleSheet("background-color: #c37676;"
                                       "border: 3px outset #5b3737;")
                    self.toggleButton.setStyleSheet("background-color: #c37676;"
                                                    "border: 2px outset #5b3737;")
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



    def toggleShowWrittenRule(self):
        """Opens or closes a spoilerplate with the fully written out version of the rule taken from the rule data"""
        #if shown then hide, if hidden then show

        if self.spoilerplate.isVisible() == False:
            self.spoilerplate = RuleTreeSpoilerPlate(self.nest_dict_rule, self.comboBox_name.currentText(), self.width(),
                                                     self.x() + self.main_dialog_x, self.y() + self.main_dialog_y) #TODO get spoilerplate to show up in the right place
            self.spoilerplate.show()
        elif self.spoilerplate.isVisible():
            self.spoilerplate.hide()
        pass

    def mouseReleaseEvent(self, event):
        """ connect the clicked signal to a mouseReleaseEvent, so that it emits when the widget is clicked"""
        self.clicked.emit()


class RuleTreeSpoilerPlate(QLabel): # TODO this one needs to be placed in the scrollarea rather than on the screen
    """ Creates the spoiler plate associated with the rule number in ruleTreeWidget"""
    def __init__(self, nest_dict_rules, current_rule, width=200, x_pos=1, y_pos=1, parent = None):
        super(RuleTreeSpoilerPlate, self).__init__(parent)
        #variables
        self.width = width
        self.nest_dict_rules = nest_dict_rules
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.current_rule = current_rule
        #events
        self.setupUI()

    def setupUI(self):
        self.setText(self.nest_dict_rules[self.current_rule][1])
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.setMaximumWidth(self.width)
        self.setGeometry(self.x_pos, self.y_pos, 0, 0)
        self.setStyleSheet("border: 2px solid black")
        self.setWordWrap(True)


class RuleTreeComboBox(QComboBox):
    """ Creates the label with the rule number in it"""
    def __init__(self, nest_dict_rule, parent = None):
        super(RuleTreeComboBox, self).__init__(parent)

        #setup UI
        self.setupUI(nest_dict_rule)

    def setupUI(self, nest_dict_rule):
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setMaximumSize(60, 13)
        self.setMinimumSize(60, 13)
        self.setStyleSheet('border: 1px;')
        for item in nest_dict_rule:
            self.addItem(item)


class RuleTreeToggleButton(QPushButton):
    """ Creates a small pushbutton"""
    def __init__(self, parent = None):
        super(RuleTreeToggleButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setMaximumSize(20, 20)
        self.setMinimumSize(20, 20)
        self.setText('V')
        # TODO make button look like a button again...

