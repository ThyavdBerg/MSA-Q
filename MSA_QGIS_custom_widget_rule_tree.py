from PyQt5.QtWidgets import QLabel, QSizePolicy, QPushButton, QHBoxLayout, QFrame, QComboBox

class RuleTreeWidget(QFrame):
    """ A custom widget that functions as a spoiler widget and can be placed in a rule tree with other ruleTreeWidgets
    parent: QWidget"""
    def __init__(self, nest_dict_rule, order_id, prev_ruleTreeWidgets = None, next_ruleTreeWidgets = [],  main_dialog_x=1, main_dialog_y=1, parent = None):
        super(RuleTreeWidget, self).__init__(parent)
        ### variables before UI
        self.nest_dict_rule = nest_dict_rule
        self.order_id = order_id
        self.prev_ruleTreeWidgets = prev_ruleTreeWidgets
        self.next_ruleTreeWidgets = next_ruleTreeWidgets
        self.next_ruleTreeWidgets = []
        self.main_dialog_x = main_dialog_x
        self.main_dialog_y = main_dialog_y
        self.isSelected = False
        self.isBaseGroup = False

        #setup UI
        self.setupUI()

        #variables after UI
        self.selectedRule = self.comboboxname.currentText()
        self.written_rule = self.nest_dict_rule[self.selectedRule][1]
        self.spoilerplate = RuleTreeSpoilerPlate(self.nest_dict_rule, self.comboboxname.currentText()) #just so that the first if statement in toggling the spoilerplate doesn't flip out

        ### events
        self.toggleButton.clicked.connect(self.toggleShowWrittenRule)


        ### functions
        #DrawLine: draws lines from the bottom middle of all previous ruleTreeWidgets to the middle top of this ruleTreeWidget
                    #removes previous lines associated with the ruleTreeWidget
        #Paint: Draws the widget
    def toggleBaseGroup(self):
        """ Toggles whether the rule is part of a base group. Function is only available for rules with 100% chance to
        happen, that have no prev_ruleTreeWidgets or 1 prev_ruleTreeWidget that also has base_group = True"""

        if self.nest_dict_rule[self.selectedRule] == 100:
            if self.isSelected == True and self.isBaseGroup == False:
                self.isBaseGroup = True
            elif self.isSelected == True and self.isBaseGroup == True:
                self.isBaseGroup = False
        else:
            self.isBaseGroup = False
            #TODO: give warning message: cannot assign as base group if rule does not have 100% chance to happen wherever it applies
            #TODO: give warning message: cannot assign as base group if has branches >1
            pass


    def setupUI(self):
        """ Creates the UI component"""
        ### Construct the thing
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setMaximumSize(150, 40)
        self.setMinimumSize(150, 40)
        self.setStyleSheet("background-color: #c3c3c3;"
                           "border: 3px outset #5b5b5b;")


        self.toggleButton = RuleTreeToggleButton()
        self.toggleButton.setStyleSheet("background-color: #c3c3c3;"
                                        "border: 2px outset #5b5b5b;")
        self.comboboxname = RuleTreeComboBox(self.nest_dict_rule)
        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.toggleButton)
        self.hLayout.addWidget(self.comboboxname)
        self.setLayout(self.hLayout)

    def toggleShowWrittenRule(self):
        """Opens or closes a spoilerplate with the fully written out version of the rule taken from the rule data"""
        #if shown then hide, if hidden then show

        if self.spoilerplate.isVisible() == False:
            self.spoilerplate = RuleTreeSpoilerPlate(self.nest_dict_rule, self.comboboxname.currentText(), self.width(),
                                                     self.x()+self.main_dialog_x, self.y()+self.main_dialog_y) #TODO get spoilerplate to show up in the right place
            self.spoilerplate.show()
        elif self.spoilerplate.isVisible():
            self.spoilerplate.hide()
        pass

    def mouseReleaseEvent(self, e):
        """ Sets isSelected to true/false when the widget is clicked and changes the colour of the widget to indicate
        its selection status"""
        if self.isSelected == True:
            self.isSelected = False
            self.setStyleSheet("background-color: #c3c3c3;"
                               "border: 3px outset #5b5b5b;")
            self.toggleButton.setStyleSheet("background-color: #c3c3c3;"
                                            "border: 2px outset #5b5b5b;")
        elif self.isSelected == False:
            self.isSelected = True
            self.setStyleSheet("background-color: #7dc376;"
                               "border: 3px inset #3a5b37;")
            self.toggleButton.setStyleSheet("background-color: #7dc376;"
                                            "border: 2px outset #3a5b37;")




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

