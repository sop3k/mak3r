# -*- coding: utf-8 -*-


class Container(object):
    def __init__(self, sceneview, pos_x, pos_y, width, height):
        self.sceneview = sceneview
        self.x = pos_x
        self.y = pos_y
        self.width = width
        self.height = height

    def checkHit(self, x, y):
        if (x >= self.x and x <= self.x + self.width) and \
                (y >= self.y and y <= self.y + self.height):
            return True
        return False

    def mouseEvent(self, x, y):
        if self.checkHit(x, y):
            return True
        return False

    def mouseMoveEvent(self, x, y):
        return self.mouseEvent(x, y)

    def mousePressEvent(self, x, y):
        return self.mouseEvent(x, y)

    def mouseReleaseEvent(self, x, y):
        return self.mouseEvent(x, y)

    def keyPressEvent(self):
        # Check if there is focus on any editable fields in top bar
        if self.sceneview.hasFocusTopBar():
            return True
        return False
