from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QPushButton, QHBoxLayout, QFrame
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

class RuleTreeWidget(QFrame):
    """ A custom widget that functions as a spoiler widget and can be placed in a rule tree with other ruleTreeWidgets
    parent: QWidget"""
    def __init__(self, list_rule, n_branch, n_row, base_group = False, prev_ruleTreeWidgets = None, next_ruleTreeWidgets = None, parent = None):
        super(RuleTreeWidget, self).__init__(parent)

        ### variables
        self.list_rule = list_rule
        self.rule_number = self.list_rule[0]
        self.written_rule = self.list_rule[1]
        self.n_branch = n_branch
        self.n_row = n_row
        self.base_group = base_group
        self.prev_ruleTreeWidgets = prev_ruleTreeWidgets
        self.next_ruleTreeWidgets = next_ruleTreeWidgets


        # rule number (int)
        # rule data (list of dict associated with rule number
        # previous flowchart widgets (ordereddict of ruleTreeWidgets:[x,y])
        # next flowchart widgets (ordereddict of ruleTreeWidgets:[x,y])
        # branch number (int) - not the same a colum number
        # row number (int)
        # base group (boolean)
        # all previous flowchart widgets processed (boolean)
        # all next flowchart widgets processed (boolean)

        ### events
        # On press arrow, ToggleShowWrittenRule.
        self.setupUI()
        self.toggleButton.clicked.connect(self.ToggleShowWrittenRule)


        ### functions
        #DrawLine: draws lines from the bottom middle of all previous ruleTreeWidgets to the middle top of this ruleTreeWidget
                    #removes previous lines associated with the ruleTreeWidget
        #Paint: Draws the widget
    def ToggleBaseGroup(self):
        """ Toggles whether the rule is part of a base group. Function is only available for rules with 100% chance to
        happen, that have no prev_ruleTreeWidgets or 1 prev_ruleTreeWidget that also has base_group = True"""

    def setupUI(self):
        """ Creates the UI component"""
        ### Construct the thing
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setMaximumSize(100, 40)
        self.setMinimumSize(100, 40)
        self.setStyleSheet("background-color: white;"
                           "border: 1px solid black;"
                           "padding: 2px;")

        self.toggleButton = RuleTreeToggleButton()
        self.labelName = RuleTreeLabel(self.rule_number)
        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.toggleButton)
        self.hLayout.addWidget(self.labelName)
        self.setLayout(self.hLayout)
        self.spoilerPlate = RuleTreeSpoilerPlate(self.written_rule) # hand it the arguments it needs

    def ToggleShowWrittenRule(self):
        """Opens or closes a spoilerplate with the fully written out version of the rule taken from the rule data"""
        #if shown then hide, if hidden then show
        if self.spoilerPlate.isVisible():
            self.spoilerPlate.hide()
        else:
            self.spoilerPlate.show()
        pass


class RuleTreeSpoilerPlate(QLabel):
    """ Creates the spoiler plate associated with the rule number in ruleTreeWidget"""
    def __init__(self, written_rule, width=200, x_pos=1, y_pos=1, parent = None):
        super(RuleTreeSpoilerPlate, self).__init__(parent)
        #variables
        self.width = width
        self.written_rule = written_rule
        self.x_pos = x_pos
        self.y_pos = y_pos
        #events
        self.setupUI()

    def setupUI(self):
        self.setText(self.written_rule)
        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed))
        self.setMaximumWidth(self.width)
        self.setGeometry(self.x_pos, self.y_pos, 0, 0)
        self.setStyleSheet("border: 2px solid black")
        self.setWordWrap(True)

class RuleTreeLabel(QLabel):
    """ Creates the label with the rule number in it"""
    def __init__(self, rule_number, parent = None):
        super(RuleTreeLabel, self).__init__(parent)
        print('making the label was reached')
        self.rule_number = rule_number
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setMaximumSize(40,13)
        self.setMinimumSize(40,13)
        self.setText('Rule ' + str(self.rule_number))
        self.setStyleSheet('border: 0px;')

class RuleTreeToggleButton(QPushButton):
    """ Creates a small pushbutton"""
    def __init__(self, parent = None):
        super(RuleTreeToggleButton, self).__init__(parent)
        print('making the button was reached')
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setMaximumSize(20, 20)
        self.setMinimumSize(20, 20)
        self.setText('V')
        # TODO make button look like a button again...

