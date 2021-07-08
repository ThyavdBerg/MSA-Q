from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QFrame
from .MSA_QGIS_custom_widget_rule_tree import RuleTreeWidget


class RuleTreeFrame(QFrame):
    """ A custom widget that functions as a spoiler widget and can be placed in a rule tree with other ruleTreeWidgets
    parent: QWidget"""
    def __init__(self, parent = None):
        super(RuleTreeFrame, self).__init__(parent)

    def paintEvent(self, event):
        for child in self.children():
            if isinstance(child, RuleTreeWidget):
                self.drawLines(child)


    def drawLines(self, ruleTreeWidget):
        """ Draws lines between ruleTreeWidgets and their next_ruleTreeWidgets"""
        # TODO draw multiple lines if RuleTreeWidget has duplicates
        # TODO draw line from RuleTreeWidgets in series to the duplicates of their next rules
        painter = QPainter()
        painter.setRenderHint(QPainter.Antialiasing)

        for next_widget in ruleTreeWidget.next_ruleTreeWidgets:
            for child in self.children():
                if isinstance(child, RuleTreeWidget):
                    if child.order_id == next_widget:
                        painter.begin(self)
                        middle_x = ruleTreeWidget.x() + 50
                        middle_y = ruleTreeWidget.y() + 15
                        top_next_widget_x = child.x() + 50
                        top_next_widget_y = child.y() + 15
                        painter.drawLine(middle_x, middle_y, top_next_widget_x, top_next_widget_y)
                        painter.end()
                        # if the next widget has duplicates, check if ruleTreeWidget was a 'series' or 'parallel' (not 'series start')
                        # if yes, then search for children with codes that are ruleTreeWidget order_id with only 0s added
                        # draw lines from those widgets to the next_widget
                        if len(child.duplicate_ruleTreeWidgets) >0:
                            if ruleTreeWidget.connection_type == 'series' or ruleTreeWidget.connection_type == 'parallel':
                                for child_search_again in self.children():
                                    if isinstance(child_search_again, RuleTreeWidget):
                                        if ((str(ruleTreeWidget.order_id)) in str(child_search_again.order_id)):
                                            length_order_id = len(str(ruleTreeWidget.order_id))
                                            child_is_part_of_series = False
                                            if len(str(child_search_again.order_id))>length_order_id:
                                                if str(child_search_again.order_id)[:length_order_id] == str(ruleTreeWidget.order_id):
                                                    if str(child_search_again.order_id)[length_order_id] != '0':
                                                        child_is_part_of_series = True
                                                    if child_is_part_of_series:
                                                        painter.begin(self)
                                                        top_next_widget_x = child.x() + 50
                                                        top_next_widget_y = child.y()
                                                        middle_x = child_search_again.x() + 50
                                                        middle_y = child_search_again.y() + 30
                                                        painter.drawLine(middle_x, middle_y, top_next_widget_x, top_next_widget_y)
                                                        painter.end()

