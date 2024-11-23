import ast
import copy
import math
import os
import pickle
import sys
from datetime import datetime

from matplotlib.artist import Artist
from matplotlib.text import Annotation, Text
import numpy as np
import matplotlib.patches as patches
import pandas as pd
from PyQt5.Qt import Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPen, QBrush , QCursor
from PyQt5.QtWidgets import QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsItem, \
    QGraphicsLineItem, QMenu, QToolBar, QAction, QMainWindow, QDesktopWidget, QApplication, QHBoxLayout,\
    QPushButton, QLabel, QVBoxLayout, QDialog, QProgressBar
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT, FigureCanvasQTAgg
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.lines import Line2D
from matplotlib.transforms import Affine2D, IdentityTransform


from angleWindow import AngleWindow
from fractionWindow import FractionWindow
from rectwindow import InputDialog
from blitmanager import BlitManager
from settingsgrid import InputDialogSettings, BlittedCursor
from matplotlib.ticker import AutoMinorLocator, AutoLocator, MultipleLocator, FixedLocator

PICKRADIUS = 50.0
FILE_PATH='params.ini'

sys.setrecursionlimit(2000)
plt.rcParams['figure.max_open_warning'] = 100


class LineAngle:
    
    def __init__(self, angle=0.0, color='black', hiden=False ):
        self.angle = angle
        self.color = color
        self.hiden = hiden

class LineItem(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, color):
        super().__init__(x1, y1, x2, y2)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        # self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        pen = QPen(color)
        pen.setWidth(2)
        self.setPen(pen)





class dragableController(QGraphicsEllipseItem):

    def __init__(self, ange_window, scene, x=200, y=200, d=12, parent=None, DraggablePointList=None):

        self.parent = parent
        self.DraggablePointList = DraggablePointList
        self.angleDis = 3000
        self.lineList = []
        super().__init__(0, 0, d, d)
        self.scene2 = scene
        self.ange_window = ange_window
        self.ange_window.ok_button.disconnect()
        self.ange_window.ok_button.clicked.connect(self.okWindow2)
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        # self.setZValue(self.plot_item.zValue() + 1)
        self.setBrush(QBrush(Qt.blue))

        self.setZValue(10)
        self.setPos(x, y)
        self.drawAngles()

        self.context_menu = QMenu()
        deleteAngle = QAction('Delete Angle', self.context_menu)
        deleteAngle.triggered.connect(self.deleteAngleFunc)
        self.context_menu.addAction(deleteAngle)

        dragAngle = QAction('Drag Angle', self.context_menu)
        dragAngle.triggered.connect(self.dragAngleFunc)
        self.context_menu.addAction(dragAngle)

        lockAngle = QAction('Lock Angle', self.context_menu)
        lockAngle.triggered.connect(self.lockAngleFunc)
        self.context_menu.addAction(lockAngle)

        self.copyAngle = QAction('Copy Angle', self.context_menu)
        self.copyAngle.triggered.connect(self.copyAngleFunc)
        self.context_menu.addAction(self.copyAngle)

        editgAngle = QAction('Edit Angle', self.context_menu)
        editgAngle.triggered.connect(self.angleWindow)
        self.context_menu.addAction(editgAngle)
        self.minPoint = QAction('Min Point to Min Squre', self.context_menu)

        # minPoint.triggered.connect(self.minPointFunc)
        self.context_menu.addAction(self.minPoint)

    def drawAngles(self):

        for i in self.lineList:
            self.scene2.removeItem(i)
        self.lineList = []
        for angle, color in self.ange_window.anglelist.items():
            lineColor = Qt.red
            dis = self.angle_to_line(angle*-1)
            if color == "Blue":
                lineColor = Qt.blue
            elif color == "Green":
                lineColor = Qt.green

            lineItem = LineItem(
                5, 5, dis[0]*self.angleDis, dis[1]*self.angleDis, color=lineColor)
            lineItem.setPos(self.pos().x(), self.pos().y())
            lineItem.setZValue(5)
            self.scene2.addItem(lineItem)
            self.lineList.append(lineItem)

    def angle_to_line(self, angle_degrees):
        angle_radians = math.radians(angle_degrees)
        x = math.cos(angle_radians)
        y = math.sin(angle_radians)
        return (x, y)

    def itemChange(self, change, value):

        for i in self.lineList:
            i.setPos(self.pos().x(), self.pos().y())
        return super().itemChange(change, value)
    # def mousePressEvent(self, event):
    #     if event.button() == Qt.RightButton:
    #         self.context_menu.exec_(QCursor().pos())
    #         return
    #
    #     super().mousePressEvent(event)
    #
    #
    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.RightButton:
    #         print(f"Clicked point: ({self.pos().x()}, {self.pos().y()})")
    #     else:
    #         super().mouseReleaseEvent(event)

    # def mousePressEvent(self, event):
    #     print("Move")
    #     if event.button() == Qt.LeftButton:
    #         self._last_mouse_pos = event.pos()
    #     if event.button() == Qt.RightButton:
    #         self.context_menu.exec_(QCursor().pos())
    #     print(f"Clicked point: ({event.pos().x()}, {event.pos().y()})")
    #     super().mousePressEvent(event)
    #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() == Qt.LeftButton:
    #         current_pos = event.pos()
    #         last_pos = self._last_mouse_pos
    #         delta = current_pos - last_pos
    #
    #         current_scene_pos = self.mapToScene(current_pos)
    #         last_scene_pos = self.mapToScene(last_pos)
    #         scene_offset = current_scene_pos - last_scene_pos
    #
    #         scene_rect = self.scene2.sceneRect()
    #         new_rect = scene_rect.translated(-scene_offset.x(), -scene_offset.y())
    #
    #         # Проверяем, находится ли новая область в пределах сцены
    #         if self.scene2.sceneRect().contains(new_rect):
    #             self.scene2.setSceneRect(new_rect)
    #
    #         self._last_mouse_pos = current_pos
    #
    #     super().mouseMoveEvent(event)
    #
    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         del self._last_mouse_pos
    #     super().mouseReleaseEvent(event)

    def okWindow2(self):
        self.ange_window.hide()
        self.drawAngles()
        if len(self.lineList) == 0:
            self.scene2.removeItem(self)

    def angleWindow(self):
        self.ange_window.show()

    def deleteAngleFunc(self):
        self.scene2.removeItem(self)
        for i in self.lineList:
            self.scene2.removeItem(i)

    def dragAngleFunc(self):
        self.setFlag(QGraphicsItem.ItemIsMovable, True)

    def lockAngleFunc(self):
        self.setFlag(QGraphicsItem.ItemIsMovable, False)

    def copyAngleFunc(self):
        self.ange_window2 = AngleWindow(
            anglelist=copy.deepcopy(self.ange_window.anglelist))
        self.copyController = dragableController(
            ange_window=self.ange_window2, parent=self.parent, scene=self.scene2, DraggablePointList=self.DraggablePointList)
        self.copyController.minPoint.triggered.connect(
            self.parent.minPointFunc)
        self.scene2.addItem(self.copyController)
        self.DraggablePointList.append(self.copyController)

    def showContextMenu(self, event):

        if event.button == 3:  # right-click
            pos = self.canvas.mapFromGlobal(QCursor().pos())
            if self.canvas.geometry().contains(pos):
                self.context_menu.exec_(QCursor().pos())


class QGraphicsView2(QGraphicsView):
    def __init__(self, *args):
        super().__init__(*args)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, event):
        event.ignore()


def coordinates_to_angle(x_start, y_start, x_end, y_end):
    dx = x_end - x_start
    dy = y_end - y_start
    angle_rad = np.arctan2(dy, dx)
    angle_degrees = np.rad2deg(angle_rad)
    # print(angle_degrees)
    if angle_degrees < 0:
        angle_degrees = 360+angle_degrees
    # print(round(angle_degrees, 2))
    return round(angle_degrees, 2)


class DraggableAnnotatedLineCollection:
    def __init__(self, ax, bm, canvas, color='black'):
        self.ax = ax
        self.bm = bm
        self.line_collection = LineCollection([])
        self.annotations = []
        self.scats = []
        self.color = color
        self.points = []
        self.selected_line = None  # Линия, выбранная для перемещения
        self.selected_annotation = None  # Аннотация, привязанная к выбранной линии
        self.offset = None
        self.canvas = canvas
        self.figure = self.canvas.figure
        self.is_line_fixed = False

    def add_line_with_annotations(self, line_coords, annotation1_text, annotation2_text):
        # Добавляем линию в коллекцию линий
        segments = self.line_collection.get_segments()
        segments.append(line_coords)
        self.line_collection.set_segments(segments)
        # self.line_collection.set_color(self.color)

        # Получаем координаты начальной и конечной точек линии
        
        # Добавляем точки концов линии
        

        # Создаем аннотации на концах линии
        
    def update_annotations(self, annot_text, coordinates):
        self.annotations[0].set_text(f'Firs {coordinates[0]}')
        self.annotations[1].set_text(f'Last {coordinates[1]}')
        self.annotations[0].xy = coordinates[0]
        self.annotations[1].xy = coordinates[1]

    def update_scates(self, coordinates):
        self.scats[0].set_offsets = coordinates[0]
        self.scats[1].set_offsets = coordinates[1]


    def add_to_axes(self):
        # Добавляем коллекцию линий и аннотации на оси
        self.ax.add_collection(self.line_collection)
        
        # Добавляем точки концов линий
        # Привязываем события для обработки перетаскивания
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)

    def on_press(self, event):
        # Проверяем, нажата ли левая кнопка мыши и попадает ли в линию
        if event.button == 1 and self.line_collection.contains(event)[0]:
            if not self.is_line_fixed:
                annotation1 = Annotation('', xy=(0, 0), textcoords="offset points",
                                 xytext=(5, 5), ha="right", va="bottom")
                annotation2 = Annotation('', xy=(1, 1), textcoords="offset points",
                                 xytext=(-5, -5), ha="left", va="top")

                # Добавляем аннотации в список
                self.annotations.extend([annotation1, annotation2])
                for annotation in self.annotations:
                    self.ax.add_artist(annotation)
                
                print(event.xdata)
                print(event.ydata)
                self.points = [event.xdata, event.ydata]
                if self.points:
                    scat = self.ax.scatter(event.xdata, event.ydata, color="red", s=50)  # Размер и цвет точек
                    self.scats.append(scat)
                    self.scats.append(scat)
    
                # self.line, = self.ax.plot([], [], color=self.color, marker='o', linestyle='-')
            # else:    
                self.selected_line = self.line_collection
                self.offset = (event.xdata, event.ydata)  # Сохраняем начальное положение курсора

    def on_motion(self, event):
        if self.selected_line and event.xdata and event.ydata:
            # Вычисляем смещение и обновляем координаты концов линии и аннотаций
            dx, dy = event.xdata - self.offset[0], event.ydata - self.offset[1]
            segments = self.selected_line.get_segments()
            new_segments = []

            # Обновляем координаты линий и аннотаций
            for i, (x0, y0, x1, y1) in enumerate([(x[0][0], x[0][1], x[1][0], x[1][1]) for x in segments]):
                new_segments.append([(x0 + dx, y0 + dy), (x1 + dx, y1 + dy)])
                self.update_annotations('test',[ (x0 + dx, y0 + dy), (x1 + dx, y1 + dy)])
                self.update_scates([(x0 + dx, y0 + dy), (x1 + dx, y1 + dy)])
                
                # self.annotations[2 * i].xy = 
                # self.annotations[2 * i + 1].xy = 

            # Обновляем линии
            self.selected_line.set_segments(new_segments)
            self.offset = (event.xdata, event.ydata)
            self.bm.update()
            # self.ax.figure.canvas.draw_idle()

    def on_release(self, event):
        # Сбрасываем выбранную линию после отпускания кнопки мыши
        self.selected_line = None
        self.offset = None


class LineDrawer(LineCollection):
    def __init__(self, plot_window, ax, fig, canvas, bm, segments=[], colors=['black'], **kwargs):
        self.plot_window = plot_window
        super().__init__(segments=segments, colors=colors)
        self.ax = ax
        self.fig = fig
        self.bm = bm
        self.canvas = canvas
        self.start_point = None
        self.current_line = None
        self.is_line_fixed = False
        self.end_line = False
        self.marker_collection = self.ax.scatter([], [], color='red', s=100, zorder=3)
        self.an1 = Text(0.0, 0.0, '')  # Annotation('',(0,0))
        self.an2 = Text(0.0, 0.0, '')  # Annotation('',(0,0))
        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.dragging = False
        self.set_picker(5)
        self.childrens = [self.marker_collection, self.an1, self.an2]
        self.ax.add_artist(self.an1)
        self.ax.add_artist(self.an2)
        self.set_figure_childrens()
        
    def set_figure_childrens(self):
        for itm in self.childrens:
            if not itm.get_figure():
                itm.set_figure(self.fig)   
        
    def on_click(self, event):
        if event.inaxes != self.ax:  # Only respond to left clicks within the axes
            return
        contains, attrd = self.contains(event)
        if contains:
            if event.button == 3: 
            
            # if event.dblclick:
                self.dragging = False
                self.show_menu(event=event)
                # self.open_edit_dialog()
                return
            elif self.is_line_fixed:
                self.dragging = True
                self.offset = (event.xdata, event.ydata)
        else:
            self.dragging = False      
        if not self.end_line:  # First click: start drawing the line
            self.start_point = (event.xdata, event.ydata)
            self.current_line, = self.ax.plot([event.xdata, event.xdata], [event.ydata, event.ydata], color='blue', marker='o')
            self.an1.set_text(f"{self.start_point[1]:.5f}")
            an_pos1 = self.start_point[0]
            an_pos2 = self.start_point[1]
            self.an1.set_position([an_pos1, an_pos2])
            
            self.bm.add_artist(self.current_line)
            
            
            self.end_line = True
        else:  # Second click: finalize the line and create the LineCollection
            if self.current_line:
                x_data, y_data = self.current_line.get_data()
                color = self.current_line.get_color()
                vertices = np.column_stack([x_data, y_data])
                self.set_segments([vertices])
                self.set_color([color])
                self.ax.add_collection(self)
                
                # Set markers at the endpoints
                self.marker_collection.set_offsets(vertices[[0, -1]])

                # Clean up the temporary line
                self.bm.add_artist(self)
                # self.bm.add_artist(self.marker_collection)

                self.bm.remove_artist(self.current_line)
                self.current_line.remove()
                self.current_line = None
                
                self.an2.set_text(f"{event.ydata:.5f}")
                self.an2.set_position(vertices[1])
                self.end_line = True
                self.is_line_fixed = True
                self.dragging = False
                
        self.bm.update()

    def on_motion(self, event):
        if event.inaxes != self.ax or not self.start_point or not self.end_line:
            return

        if not self.is_line_fixed:
            x = self.start_point[0]
            self.current_line.set_data([x, x], [self.start_point[1], event.ydata])
            self.bm.update()
        elif self.is_line_fixed and self.dragging:
            dx, dy = event.xdata - self.offset[0], event.ydata - self.offset[1]
            segments = self.get_segments()
            new_segments = []

            for i, (x0, y0, x1, y1) in enumerate([(x[0][0], x[0][1], x[1][0], x[1][1]) for x in segments]):
                new_segments.append([(x0 + dx, y0 + dy), (x1 + dx, y1 + dy)])

            self.an1.set_position(new_segments[0][0])
            self.an2.set_position(new_segments[-1][-1])
            self.an1.set_text(f"{new_segments[0][0][-1]:.5f}")  # f"{numObj:.{digits}f}"
            self.an2.set_text(f"{new_segments[-1][-1][-1]:.5f}")
            
            endpoints = np.array([point for segment in new_segments for point in segment])
        
            self.marker_collection.set_offsets(endpoints)
            self.set_segments(new_segments)
            self.offset = (event.xdata, event.ydata)

            self.bm.update()

    def on_release(self, event):
        if self.is_line_fixed:
            self.dragging = False
            
    def open_edit_dialog(self, event):
        from tkinter import Tk, Label, Entry, Button, colorchooser
        root = Tk()
        root.title("Edit Line Properties")

        Label(root, text="Line :").grid(row=0, column=0)
        width_entry = Entry(root)
        width_entry.insert(0, "1")
        width_entry.grid(row=0, column=1)
        
        def count_update_lines(num_divisions, color):
            segments = self.get_segments()

            total_length = 0
            for segment in segments:
                start_point, end_point = segment
                segment_length = np.linalg.norm(np.array(end_point) - np.array(start_point))
                total_length += segment_length

            if num_divisions == 0:
                num_divisions = 1
            segment_length = total_length / num_divisions

            new_points = [segments[0][0]]  

            remaining_length = segment_length
            for segment in segments:
                start_point, end_point = segment
                current_segment_length = np.linalg.norm(np.array(end_point) - np.array(start_point))

                while remaining_length < current_segment_length:
                    if current_segment_length == 0:
                        current_segment_length = 1 
                    direction = (np.array(end_point) - np.array(start_point)) / current_segment_length
                    new_point = np.array(start_point) + direction * remaining_length
                    new_points.append(tuple(new_point))
                    start_point = new_point  # Обновляем начальную точку
                    current_segment_length -= remaining_length
                    remaining_length = segment_length

                remaining_length -= current_segment_length

            new_points.append(segments[-1][1])  # Конечная точка

            new_segments = [[new_points[i], new_points[i + 1]] for i in range(len(new_points) - 1)]
            x_coords, y_coords = zip(*new_points)
            self.bm.remove_artist(self.marker_collection)
            self.childrens.remove(self.marker_collection)
            self.bm.update()
            self.marker_collection = self.ax.scatter(x_coords, y_coords, color=color, s=50, zorder=3)
            self.bm.add_artist(self.marker_collection)
            self.childrens.append(self.marker_collection)
            
            self.set_segments(new_segments)

        def choose_color():
            color = colorchooser.askcolor()[1]
            if color:
                color_button.config(bg=color)
                color_button.color = color

        def choose_color_price():
            color = colorchooser.askcolor()[1]
            if color:
                color_price.config(bg=color)
                color_price.color_price = color
                
        Label(root, text="Line Color:").grid(row=1, column=0)
        Label(root, text="Price Color:").grid(row=2, column=0)
        color_button = Button(root, text="Color line", command=choose_color)
        color_price = Button(root, text="Color price", command=choose_color_price)
        color_button.grid(row=1, column=1)
        color_price.grid(row=2, column=1)

        # Apply button
        def apply_changes():
            try:
                new_width = width_entry.get()
                if new_width.isdigit():
                    count_update_lines(int(new_width), 'red')

                if hasattr(color_button, 'color'):
                    self.set_color(color_button.color)
                
                if hasattr(color_price, 'color_price'):
                    self.an1.set_color(color_price.color_price)
                    self.an2.set_color(color_price.color_price)
                    
                # self.canvas.draw_idle()
            except Exception as e:
                print(f"Error: {e}")  # Печатаем ошибку, если есть
            finally:
                self.dragging = False
                root.destroy() 
            self.bm.update()

        apply_button = Button(root, text="Apply", command=apply_changes)
        apply_button.grid(row=5 , column=0, columnspan=2)
        # root.mainloop()
        root.grab_set()
        root.wait_window()
        
        
    def show_menu(self, event):
        context_menu = QMenu()
        # if event.inaxes == self.ax:
        #     for collection in self.ax.collections:
        #         if collection != self:
        #             pickradius = collection.get_pickradius()
        #             collection.set_pickradius(pickradius*3)
        #             contains, attrd = collection.contains(event)
        #             collection.set_pickradius(pickradius)
        #             if contains:
        #                 action_attach = QAction("Attach Angle")
        #                 action_attach.triggered.connect(lambda: self.menu_attach_angle(event, collection))
        #                 context_menu.addAction(action_attach)
        #                 break

        # action_ray = QAction("Ray Angle")
        # action_ray.triggered.connect(lambda: self.menu_ray_angle(event))
        # context_menu.addAction(action_ray)

        # action_lock = QAction("Lock Angle")
        # action_lock.triggered.connect(self.menu_lock_angle)
        # context_menu.addAction(action_lock)

        # action_drag = QAction("Drag Angle")
        # action_drag.triggered.connect(self.menu_drag_angle)
        # context_menu.addAction(action_drag)

        action_del = QAction("Delete line")
        action_del.triggered.connect(self.menu_delete_line)
        context_menu.addAction(action_del)

        # action_copy = QAction("Copy Angle")
        # action_copy.triggered.connect(self.menu_copy_angle)
        # context_menu.addAction(action_copy)

        action_edit = QAction("Edit line")
        action_edit.triggered.connect(lambda: self.open_edit_dialog(event))
        context_menu.addAction(action_edit)

        context_menu.exec_(QCursor.pos()) 
        
    def menu_delete_line(self):
        for collection in self.ax.collections:
            if self == collection:
                self.plot_window.rem_collections(collection)
                self.bm.remove_artist(self) 
                # collection.remove()
                break
        # del self    
        self.bm.update()       
        
        
class DraggableSquareCollection(PatchCollection):
    def __init__(self, parent_plot_window, canvas, ax, bm, parametrs, match_original, **kwargs):
        self.plot_window = parent_plot_window
        self.ax = ax
        self.canvas = canvas
        self.press = None
        self.parametrs = parametrs.copy()
        self.x_start = self.ax.get_xlim()[0]+1
        self.y_start = self.ax.get_ylim()[0]+1
        self.squares = self.draw_square()
        self.angle = 0
        self.current_transform = None
        self.matrix = None
        super().__init__(self.squares, match_original=match_original, **kwargs)
        self.rotate()
        self.figure = self.canvas.figure
        self.bm = bm
        self.lock = False
        self.connect()


    def connect(self):
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):

        if event.inaxes == self.axes:

            contains, attrd = self.contains(event)
            if contains:
                if event.button == 3:

                    self.show_menu()
                    return

                if event.dblclick:
                    self.update_square()
                else:
                    if not self.lock:
                        if self.current_transform is None:
                            self.current_transform = self.get_transform()
                        self.press = True

    def on_release(self, event):
        self.press = False

    def canvas_to_object_coordinates(self, x_canvas, y_canvas):
        paths = self.get_paths()
        x_left, y_bottom = paths[0].vertices[0]
        rotation_matrix = np.array([[np.cos(np.radians(self.angle)), -np.sin(np.radians(self.angle))],
                                    [np.sin(np.radians(self.angle)), np.cos(np.radians(self.angle))]])
        translated_coords = np.array([x_canvas - x_left, y_canvas - y_bottom])
        object_coords = np.dot(np.linalg.inv(rotation_matrix), translated_coords)
        return object_coords[0], object_coords[1]

    def on_motion(self, event):
        if event.inaxes is None:
            return
        if self.press:
            object_x, object_y = self.canvas_to_object_coordinates(event.xdata, event.ydata)
            rotation = Affine2D().translate(object_x, object_y)
            trans = rotation+self.current_transform
            self.matrix = rotation
            self.set_transform(trans)
            self.bm.update()

    def update_square(self):
        self.rect_window = InputDialog(self.parametrs)
        result = self.rect_window.exec_()
        if result == QDialog.Accepted:
            self.squares = self.draw_square()
            self.set_paths(self.squares)
            self.rotate(new=False)
            self.bm.update()
            # self.canvas.draw_idle()

    def get_ratio(self, expression):
        parts = expression.split('/')
        if len(parts) == 2:
            numerator = float(parts[0].strip())
            try:
                denominator = float(parts[1].strip())
            except:
                denominator = 1
            if denominator != 0:
                result = numerator / denominator
            else:
                result = 0
        else:
            result = 0
        return result

    def draw_square(self):
        angl, cols, ratio, square_size = self.parametrs
        cols = int(cols)
        ratio = self.get_ratio(ratio)
        cols += 1
        square_size = int(square_size)
        squares = []
        x = self.x_start
        y = self.y_start
        for i in range(cols):
            for j in range(cols):
                size_x = square_size
                size_y = square_size
                if i == cols - 1:
                    size_x *= ratio
                if j == 0:
                    size_y *= ratio

                rect = patches.Rectangle((x, y), size_x, size_y,
                                         linewidth=2,
                                         edgecolor='green', facecolor='none', )
                squares.append(rect)
                y += size_y
            y = self.y_start
            x += size_x

        return squares

    def rotate(self, new=True ):
        paths = self.get_paths()
        x_left, y_bottom = paths[0].vertices[0]

        if new:
            trans = self.ax.transData
        else:
            if self.matrix is not None:
                trans = self.matrix + self.current_transform
            else:
                trans = self.current_transform
        new_transform = (Affine2D()
                         .rotate_deg_around(x_left, y_bottom, - self.angle))
        new_transform += (Affine2D().rotate_deg_around(x_left, y_bottom, self.parametrs[0]))

        self.set_transform(new_transform + trans)
        if self.matrix is not None:
            self.current_transform = new_transform - self.matrix + trans
        else:
            self.current_transform = new_transform + trans
        self.angle = self.parametrs[0]
        self.canvas.draw_idle()

    def show_menu(self):
        context_menu = QMenu()


        action_lock = QAction("Lock Square")
        action_lock.triggered.connect(self.menu_lock_square)
        context_menu.addAction(action_lock)

        action_drag = QAction("Drag Square")
        action_drag.triggered.connect(self.menu_drag_square)
        context_menu.addAction(action_drag)

        action_del = QAction("Delete Square")
        action_del.triggered.connect(self.menu_delete_square)
        context_menu.addAction(action_del)

        action_copy = QAction("Copy Square")
        action_copy.triggered.connect(self.menu_copy_square)
        context_menu.addAction(action_copy)

        action_edit = QAction("Edit Square")
        action_edit.triggered.connect(self.update_square)
        context_menu.addAction(action_edit)

        context_menu.exec_(QCursor.pos())

    def menu_delete_square(self):
        for collection in self.ax.collections:
            if self == collection:
                self.plot_window.rem_collections(collection)
                self.bm.remove_artist(self)
                collection.remove()
                break
        self.bm.update()
        # self.canvas.draw_idle()

    def menu_copy_square(self):
        new_obj = DraggableSquareCollection(self.plot_window, self.canvas, self.ax, self.bm,
                                            parametrs=self.parametrs,
                                            match_original=True, zorder=3)
        self.bm.add_artist(new_obj)
        self.plot_window.add_collections(new_obj)
        self.ax.add_collection(new_obj)
        # self.canvas.draw_idle()
        self.bm.update()

    def menu_lock_square(self):
        self.lock = True

    def menu_drag_square(self):
        self.lock = False

def line_picker(lines, mouseevent):
    """
    Find the points within a certain distance from the mouseclick in
    data coords and attach some extra attributes, pickx and picky
    which are the data points that were picked.
    """
    if mouseevent.xdata is None:
        return False, dict()

    for segment in lines.get_paths():
        new_segment = segment.vertices
        xdata = new_segment[:, 0]
        ydata = new_segment[:, 1]
    xdata = np.array(xdata)
    ydata = np.array(ydata)
    maxd = 0.05
    d = np.sqrt(
        (xdata - mouseevent.xdata)**2 + (ydata - mouseevent.ydata)**2)

    ind, = np.nonzero(d <= maxd)
    if len(ind):
        pickx = xdata[ind]
        picky = ydata[ind]
        props = dict(ind=ind, pickx=pickx, picky=picky)
        return True, props
    else:
        return False, dict()


class DraggableLineCollection(LineCollection):

    def __init__(self, parent_plot_window, ax, bm, angles, colors, x_start=0, y_start=0, length=1000, **kwargs):
        self.plot_window = parent_plot_window
        self.ax = ax
        # self.canvas = canvas
        self.angles = angles
        self.colors = colors
        self.length = length
        self.linewidth = kwargs['linewidth']
        self.line_alpha = kwargs['alpha']
        self.set_xy_start(x_start, y_start)
        self.x_start == x_start
        self.y_start == y_start
        segments = self.angle_to_line()
        color = self.lower_color()

        # super().__init__(segments, color=color, picker=line_picker, **kwargs)
        super().__init__(segments, color=color, picker=True, **kwargs)
        # self.set_pickradius(10.5)
        # self.figure = self.canvas.figure
        self.bm = bm
        self.press = None
        self.lock_angle = False
        self.useblit = True
        self.connect()
        self.new_segments=None

        # self.update_lines()
        # self.set_alpha(alpha=alpha)

    def set_xy_start(self, x_start, y_start):
        self.x_start = x_start
        self.y_start = y_start

    def menu_ray_angle(self, event):
        paths = self.get_paths()

        # for _ in paths:
        #     new_line = Line2D(_.vertices[0], _.vertices[1], lw=2, color='green',
        #             axes=self.ax, alpha=0.7, transform=self.ax.transData)
        #     new_line.set_figure(self.ax.figure)
        #     # new_line.axes = self.axes
        #     self.ax.add_line(new_line)
        #     contains, attrd = new_line.contains(event)
        #     if contains:
        #         print(new_line)

        self.length *= 1000
        self.x_start, self.y_start = paths[0].vertices[0]
        segments = self.angle_to_line()
        color = self.lower_color()
        self.set_colors(color)
        self.set_linewidth(self.linewidth)
        self.set_segments(segments)
        self.bm.update()


    def menu_delete_angle(self):
        for collection in self.plot_window.get_collections():
            if self == collection:
                self.plot_window.rem_collections(collection)
                self.bm.remove_artist(self)
                collection.remove()
                break
        self.bm.update()
        # self.ax.figure.canvas.draw_idle()

    def menu_copy_angle(self):
        x_start = self.ax.get_xlim()[0] + 5
        y_start = self.ax.get_ylim()[0] + 5
        new_obj = DraggableLineCollection(self.plot_window, self.ax, self.bm, angles=self.angles,
                                          linewidth=self.linewidth, length=self.length,
                                          colors=self.colors, zorder=3, alpha=self.line_alpha, x_start=x_start, y_start=y_start)
        # self.collection_itms.append(new_obj)
        self.plot_window.add_collections(new_obj)
        self.bm.add_artist(new_obj)
        self.ax.add_collection(new_obj)
        self.bm.update()
        # self.ax.figure.canvas.draw_idle()

    def menu_lock_angle(self):
        self.lock_angle = True

    def menu_drag_angle(self):
        self.lock_angle = False

    def lower_color(self):
        return [word[0].lower() for word in self.colors if word[1]== 0]

    def angle_to_line(self):
        segments = []
        indices = [index for index, word in enumerate(self.colors) if word[1] == 1]
        for ind, angle in enumerate(self.angles):
            if ind in indices:
                continue
            angle_rad = np.deg2rad(angle)
            dx = self.length * np.cos(angle_rad)
            dy = self.length * np.sin(angle_rad)
            segments.append([np.array([self.x_start, self.y_start]), [self.x_start + dx, self.y_start + dy]])
            # segments.append(np.array([[self.x_start, self.y_start], [self.x_start + dx, self.y_start + dy]]))

        return segments

    def update_lines(self):
        [self.x_start, self.y_start] = self.get_segments()[0][0]
        self.ange_window = AngleWindow(anglelist=dict(zip(self.angles, self.colors)),
                                       linewidth=self.linewidth, alpha=self.line_alpha)
        self.ange_window.exec_()
        if self.ange_window.result == QDialog.Accepted:
            # self.bm.remove_artist(self)
            self.linewidth = self.ange_window.linewidth
            self.line_alpha = self.ange_window.line_alpha
            self.angles = list(self.ange_window.anglelist.keys())
            if self.angles:
                self.colors = list(self.ange_window.anglelist.values())
                # self.draw_lines_collection(self.angles, self.colors,
                #                            linewidth=self.ange_window.linewidth,
                #                            alpha=self.ange_window.line_alpha)

                segments = self.angle_to_line()
                color = self.lower_color()
                self.set_colors(color)
                self.set_linewidth(self.linewidth)
                self.set_alpha(self.line_alpha)
                self.set_segments(segments)
                # self.bm.add_artist(self)
                # self.ax.figure.canvas.draw_idle()
            else:
                self.menu_delete_angle()
            # self.bm.remove_artist(self)
            
            
            self.bm.update()
            # self.ax.figure.canvas.draw_idle()
                

    def menu_attach_angle(self, event, collection):
        update_itm = self
        update_itm.angles.extend(collection.angles)
        update_itm.colors.extend(collection.colors)
        segments = update_itm.get_segments()+collection.get_segments()
        # print(segments)
        update_itm.set_segments(segments)
        colors = np.concatenate([update_itm.get_edgecolors(), collection.get_edgecolors()])
        update_itm.set_edgecolors(colors)
        # self.collection_itms.remove(collection)
        self.plot_window.rem_collections(collection)
        self.bm.remove_artist(collection)
        collection.remove()
        self.bm.update()
        # self.ax.figure.canvas.draw_idle()

    def show_menu(self, event):
        context_menu = QMenu()
        if event.inaxes == self.ax:
            for collection in self.ax.collections:
                if collection != self:
                    pickradius = collection.get_pickradius()
                    collection.set_pickradius(pickradius*3)
                    contains, attrd = collection.contains(event)
                    collection.set_pickradius(pickradius)
                    if contains:
                        action_attach = QAction("Attach Angle")
                        action_attach.triggered.connect(lambda: self.menu_attach_angle(event, collection))
                        context_menu.addAction(action_attach)
                        break

        action_ray = QAction("Ray Angle")
        action_ray.triggered.connect(lambda: self.menu_ray_angle(event))
        context_menu.addAction(action_ray)

        action_lock = QAction("Lock Angle")
        action_lock.triggered.connect(self.menu_lock_angle)
        context_menu.addAction(action_lock)

        action_drag = QAction("Drag Angle")
        action_drag.triggered.connect(self.menu_drag_angle)
        context_menu.addAction(action_drag)

        action_del = QAction("Delete Angle")
        action_del.triggered.connect(self.menu_delete_angle)
        context_menu.addAction(action_del)

        action_copy = QAction("Copy Angle")
        action_copy.triggered.connect(self.menu_copy_angle)
        context_menu.addAction(action_copy)

        action_edit = QAction("Edit Angle")
        action_edit.triggered.connect(self.update_lines)
        context_menu.addAction(action_edit)

        context_menu.exec_(QCursor.pos())

    def connect(self):
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        if event.inaxes == self.axes:
            contains, attrd = self.contains(event)
            # self.bm.update()
            if contains:
                # self.ax.figure.canvas.draw_idle()
                if event.button == 3:
                    self.show_menu(event)
                    return
                if event.dblclick:
                    self.update_lines()
                else:
                    if not self.lock_angle:
                        self.pos = self.get_transform()
                        self.press = (event.xdata, event.ydata)


    def on_release(self, event):
        self.press = None
        self.set_segments(self.new_segments)
        self.set_transform(Affine2D() + self.ax.transData)
        # self.bm.update()

    # def on_mouse_move(self, event):
    #     pass

    def on_motion(self, event):
        if event.inaxes is None:
            return
        if self.press is not None:
            xpress, ypress = self.press
            dx = event.xdata - xpress
            dy = event.ydata - ypress
            rotation = Affine2D().translate(dx, dy)
            trans = rotation + self.pos

            self.set_transform(trans)
            self.new_segments = []

            for segment in self.get_paths():
                new_segment = rotation.transform(segment.vertices)
                self.new_segments.append(new_segment)
            self.bm.update()


class PlotWindow(QMainWindow):

    def __init__(self, df=None, persentageVal=None):
        super().__init__()
        self.DraggablePointList = []
        self.__collections = []
        self.setWindowTitle("Chart")
        self.factor = 10000
        self.Fraction = 1
        self.minPoint = 0.00001
        self.neumerator = 1
        self.denominator = 1
        self.persentageVal = persentageVal
        self.dict_label_x_with_data = {}

        self.df = df
        self.firstTime = True
        self.ange_window = None
        self.scene = QGraphicsScene()
        self.view = QGraphicsView2()

        screen_height = QDesktopWidget().screenGeometry().height()
        screen_width = QDesktopWidget().screenGeometry().width()-110
        DPI = QDesktopWidget().logicalDpiY()
        self.resize(screen_height, screen_width)
        # print((screen_width/self.dpi,screen_height/self.dpi))
        # print(DPI)
        # Set the aspect ratio of the figure
        # aspect_ratio = 19/9  # Width/Height

        # # Convert the height from pixels to inches
        # height_inches = screen_height / DPI

        # # Calculate the width based on the aspect ratio
        # width_inches = height_inches * aspect_ratio

        # Create the figure with the desired size and aspect ratio

        self.fig = plt.figure(figsize=(screen_width/DPI,screen_height/DPI))
        self.fig.subplots_adjust(left=0.06, right=0.99, top=1, bottom=0)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot()
        self.bm = BlitManager(self.canvas)
        self.cursor = BlittedCursor(ax=self.ax, bm=self.bm)
        # Replace original column with modified column
        self.df['High'] = df['High']*self.factor
        self.df['Low'] = df['Low']*self.factor
        self.df['Open'] = df['Open']*self.factor
        self.df['Close'] = df['Close']*self.factor
        top_button_layout = QHBoxLayout()
        self.back = QPushButton(self)
        self.back.setText("Back")
        self.back.clicked.connect(self.backToMain)
        self.back.setFixedWidth(150)
        self.back.setFixedHeight(30)
        top_button_layout.addWidget(self.back)
        nav_button_layout = QHBoxLayout()
        toolbar = QToolBar(self)
        self.addToolBar(toolbar)

        angleIcon = QIcon('images/free-bar-chart-icon-676-thumb.png')
        saveAct = QAction(angleIcon, 'Angles', self)
        saveAct.triggered.connect(self.angleWindow)
        fractionIcon = QIcon('images/market-share.png')
        fractionAct = QAction(fractionIcon, 'Settinds', self)
        fractionAct.triggered.connect(self.fractionWindow)

        lineIcon = QIcon('images/angle-cross.png')
        enableLine = QAction(lineIcon, 'Enable X lines ', self)
        enableLine.isCheckable()
        enableLine.triggered.connect(self._enableLine)

        RectIcon = QIcon('images/rectangle.png')
        rectangle_button = QAction(RectIcon, 'open rectangl window ', self)
        rectangle_button.triggered.connect(self._rectangle_window)

        settings_icon = QIcon('images/settings.png')
        settings_button = QAction(settings_icon, 'open grid settings window ', self)
        settings_button.triggered.connect(self._settings_grid)
       
        line_button_icon = QIcon('images/line.png')
        line_button = QAction(line_button_icon, 'new line ', self)
        line_button.triggered.connect(self._new_line)
        
        line_button_old = QAction(line_button_icon, 'old line ', self)
        line_button_old.triggered.connect(self._new_line_old)
        
        save_button_icon = QIcon('images/line.png')
        save_button = QAction(save_button_icon, 'save plot', self)
        save_button.triggered.connect(self.save_plot_data)

        load_button_icon = QIcon('images/line.png')
        load_button = QAction(load_button_icon, 'load plot', self)
        load_button.triggered.connect(self.load_plot_data)

        saveAct.setShortcut('Ctrl+V')
        toolbar.addAction(saveAct)
        toolbar.addAction(fractionAct)
        toolbar.addAction(enableLine)
        # toolbar.addAction(rectangle_button)
        toolbar.addAction(settings_button)
        # toolbar.addAction(line_button)
        toolbar.addAction(line_button_old)
        # toolbar.addAction(save_button)
        # toolbar.addAction(load_button)

        toolbar.setStyleSheet("margin-left:10px;margin-top:1px;")
        nav_button_layout.addWidget(toolbar)

        # Remove the scrollbars
        # self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.button_toolbar_press = False
        # self.toolbar = NavigationToolbar(self.canvas, self, self.bm)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.coordinates = False

        self.coordinates_label = QProgressBar(self)
        self.coordinates_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.coordinates_label.setMinimumWidth(150)
        # self.coordinates_label.setStyleSheet("QLabel { color: red; }")

        self.toolbar.addWidget(self.coordinates_label)
        self.addToolBar(self.toolbar)
        # self.fig.canvas.manager.toolbar._Button("PREVIOUS", "back_large", self.prev)
        # self.canvas.adjustSize()
        # self.plot_item = QGraphicsProxyWidget()
        # self.view.fitInView(self.plot_item, Qt.KeepAspectRatio)
        #self.canvas.resize(screen_width-160,960)
        self.scene.addWidget(self.canvas)
        self.view.setScene(self.scene)
        # self.scene.addItem(self.plot_item)
        # self.plot_item.setWidget(self.plot_widget)
        # self.scene.addItem(self.plot_item)
        # self.view.setScene(self.scene)
        # self.fig.subplots_adjust(left=0.04, right=0.99, top=1, bottom=0)

        widget = QWidget()
        layout1 = QVBoxLayout(widget)
        self.showMaximized()
        layout1.addLayout(nav_button_layout)
        layout1.addWidget(self.view)
        layout1.addLayout(top_button_layout)

        layout1.setContentsMargins(10, 0, 10, 0)
        self.setCentralWidget(widget)
        self.worker_thread = None
        self.grid_parametrs = [5, 'red', 'black', 1, 0.5, 0.5, 0.5, 'white', 1,'#3A8DDE','red','black']
        self.load_parametrs()
        self.plotMainDraph()
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_press_plot)

    def update_data(self, new_data: pd.DataFrame):
        """
        Update the candlestick chart with new data.
        """
        # Append new data, ensuring no duplicate timestamps
        self.df = pd.concat([self.df, new_data]).drop_duplicates(subset="DateTime").sort_values(by="DateTime")

        # Refresh the plot
        self.plotMainDraph()
        self.set_parametrs_ax()

    def save_plot_data(self, filename='my.pkl'):
        rectangles_data = []

        # Collect data to save (coordinates and properties for rectangles)
        for index, row in self.df.iterrows():
            heightOuter = row['High'] - row['Low']
            heightInner = abs(row['Close'] - row['Open'])
            innerMinVal = min([row['Close'], row['Open']])
            rectangles_data.append({
                'currentPos': index * self.step,
                'low': row['Low'],
                'heightOuter': heightOuter,
                'innerMinVal': innerMinVal,
                'heightInner': heightInner,
                'color': self.grid_parametrs[9] if (row['Close'] - row['Open'] >= 0) else self.grid_parametrs[10]
            })

        plot_data = {
            'rectangles': rectangles_data,  # Save rectangle data
            'grid_parametrs': self.grid_parametrs,
            'collections': self.get_collections(),  # Save lines and other collections
        }
        
        # Save data with pickle
        with open(filename, 'wb') as f:
            pickle.dump(plot_data, f)


# Method to load plot data (rectangles, collections, and parameters) and restore the plot
    def load_plot_data(self, filename='my.pkl'):
        # Load data from file
        with open(filename, 'rb') as f:
            plot_data = pickle.load(f)

        rectangles_data = plot_data['rectangles']
        self.grid_parametrs = plot_data['grid_parametrs']
        
        # Clear current plot
        self.ax.clear()

        # Restore rectangles
        for rect_data in rectangles_data:
            outer_rect = patches.Rectangle(
                (rect_data['currentPos'], rect_data['low']),
                self.step,
                rect_data['heightOuter'],
                linewidth=0.5,
                edgecolor='black',
                facecolor='none',
                zorder=2
            )
            self.ax.add_patch(outer_rect)

            inner_rect = patches.Rectangle(
                (rect_data['currentPos'], rect_data['innerMinVal']),
                self.step,
                rect_data['heightInner'],
                linewidth=0.5,
                facecolor=rect_data['color'],
                zorder=1
            )
            self.ax.add_patch(inner_rect)

        # Restore collections (e.g., lines)
        for lines_ in plot_data['collections']:
            self.ax.add_collection(lines_)



    def load_parametrs(self):
        if os.path.exists(FILE_PATH):
            with open(file=FILE_PATH,) as file:
                line = file.readline()
                self.grid_parametrs = ast.literal_eval(line)
                if len(self.grid_parametrs)< 12:
                    self.grid_parametrs.append('black')

    def on_press_plot(self, event):
        if event.inaxes == self.ax:
                if event.button == 3:
                    self.show_menu_plot(event)

    def show_menu_plot(self, event):
        pick_radius = 0.5
        context_menu = QMenu()
        # if event.inaxes == self.ax:
        collections = self.ax.collections
        for collection in collections:
            contains, attrd = collection.contains(event)
            if contains:
                return
        if event.inaxes is None:
            return

        x, y = event.xdata, event.ydata

        collection_true = []
        for collection in collections:
            segments = collection.get_segments()
            for i, (point0, point1) in enumerate(segments):
                x0, y0 = point0
                x1, y1 = point1

                dist = np.linalg.norm(np.cross([x1 - x0, y1 - y0], [x - x0, y - y0])) / np.linalg.norm([x1 - x0, y1 - y0])
                if dist < pick_radius:
                    collection_true.append(collection)
                    break
        if len(collection_true) > 1:
            action_ray = QAction("Attach")
            action_ray.triggered.connect(lambda: self.menu_attach(collection_true))
            context_menu.addAction(action_ray)
            context_menu.exec_(QCursor.pos())

    def menu_attach(self, collections):
        update_itm, collection = collections
        update_itm.angles.extend(collection.angles)
        update_itm.colors.extend(collection.colors)
        segments = update_itm.get_segments() + collection.get_segments()
        update_itm.set_segments(segments)
        colors = np.concatenate([update_itm.get_edgecolors(), collection.get_edgecolors()])
        update_itm.set_edgecolors(colors)
        self.rem_collections(collection)
        self.bm.remove_artist(collection)
        collection.remove()
        self.bm.update()

    def resizeEvent(self, event):
        new_size = event.size()
        self.canvas.figure.set_size_inches((new_size.width()-30)/self.canvas.figure.dpi,
                                           new_size.height()/self.canvas.figure.dpi)
        self.canvas.draw_idle()

    def add_collections(self, collection):
        self.__collections.append(collection)

    def rem_collections(self, collection):
        if collection in self.__collections:
            self.__collections.remove(collection)

    def get_collections(self):
        return self.__collections

    def draw_square_collection(self, parametrs):
        squares = DraggableSquareCollection(self, self.canvas, self.ax, self.bm, parametrs,
                                            match_original=True, zorder=3)
        self.add_collections(squares)
        # self.collection_itms.append(squares)
        self.ax.add_collection(squares)
        self.bm.add_artist(squares)
        self.bm.update()
        # self.canvas.draw_idle()

    def _rectangle_window(self):
        parametrs=[]
        self.rect_window = InputDialog(parametrs)
        result = self.rect_window.exec_()
        if result == QDialog.Accepted:
            self.draw_square_collection(parametrs)

    def _settings_grid(self):
        settings_window = InputDialogSettings(self.grid_parametrs)
        result = settings_window.exec_()
        if result == QDialog.Accepted:
            #self.set_parametrs_ax()
            self.grid_parametrs = settings_window.param
            self.plotMainDraph()
            self.bm.update()
            # self.canvas.draw_idle()

    def _new_line(self):
        # print(f'NewLine')
        # self.cursor.add_dict_x_labels(self.dict_label_x_with_data, self.step)
        # self.line = LineDrawer(self, self.ax, self.fig, self.canvas, self.bm, self.cursor)
        line = DraggableAnnotatedLineCollection(self.ax, self.bm, self.canvas)
        start = self.ax.get_xlim()[0] + 5
        stop = self.ax.get_ylim()[0] + 5
        line.line_collection.set_color= 'blue'
        line.add_line_with_annotations([(start, stop), (start+2, stop+2)], "Start", "End")
        line.add_to_axes()
        self.add_collections(line)
        self.bm.add_artist(line.line_collection)
        # for annotation in line.annotations:
        #     self.bm.add_artist(annotation)
        # self.ax.figure.canvas.draw_idle()
        self.bm.update()

    def _new_line_old(self):
            # print(f'NewLine')
            line = LineDrawer(self, self.ax, self.fig, self.canvas, self.bm,)
            self.add_collections(line)
            # self.bm.add_artist(line)
            # self.ax.figure.canvas.draw_idle()
            # self.bm.update()


    def _enableLine(self):
        self.cursor.visible = not self.cursor.visible
        # self.cursor.set_cross_hair_visible(self.cursor.visible)
        if self.cursor.visible:
            self.cursor.on_draw()
            self.cursor.add_dict_x_labels(self.dict_label_x_with_data, self.step)
        else:
            self.cursor.del_artists()

    def wheelEvent(self, event):
        event.ignore()

    def backToMain(self):
        self.close()

    def angleWindow(self):
        self.ange_window = AngleWindow()
        self.ange_window.exec_()
        if self.ange_window.result == QDialog.Accepted:
            if self.ange_window.anglelist:
                # list_angles, list_colors = zip(*self.ange_window.anglelist.items())
                list_angles = list(self.ange_window.anglelist.keys())
                list_colors = list(self.ange_window.anglelist.values())
                self.draw_lines_collection(list_angles, list_colors,
                                           linewidth=self.ange_window.linewidth,
                                           alpha=self.ange_window.line_alpha)
              
            # self.ange_window.ok_button.clicked.connect(self.okWindow)
            # self.angleDict=self.ange_window.getAnglelist()
            

    def fractionWindow(self):
        self.fracWindow = FractionWindow(
            fraction=self.Fraction, minPoint=self.minPoint, neumerator=self.neumerator, denominator=self.denominator)
        self.fracWindow.show()
        self.fracWindow.button.clicked.connect(self.fractionSet)

    # def showContextMenu(self, event):
    #     if event.button == 3:  # right-click
    #         pos = self.canvas.mapFromGlobal(QCursor().pos())
    #         if self.canvas.geometry().contains(pos):
    #             self.context_menu.exec_(QCursor().pos())

    def fractionSet(self):
        if self.fracWindow.on_submit() != False:
            self.Fraction = self.fracWindow.Fraction
            self.minPoint = self.fracWindow.Minpoint
            self.neumerator = self.fracWindow.neumerator
            self.denominator = self.fracWindow.denominator
            self.fracWindow.close()
            self.plotMainDraph()
            #self.set_parametrs_ax()
            # self.canvas.draw_idle()

    def draw_lines_collection(self, angles: list, colors: list, **kwargs):
        # lines_groupe = DraggableLineCollection(self,
        #                                        self.canvas,
        #                                        self.ax,
        #                                        self.bm,
        #                                        angles=angles,
        #                                        colors=colors,
        #                                        length=10*1000,
        #                                        zorder=3,
        #                                        **kwargs
        #                                        )
            
        x_start = self.ax.get_xlim()[0] + 5
        y_start = self.ax.get_ylim()[0] + 5
        
        lines_groupe = DraggableLineCollection(self, self.ax, self.bm,
                                               angles=angles,
                                               colors=colors,
                                               x_start=x_start,
                                               y_start=y_start,
                                               length=10*1000,
                                               zorder=3,
                                               **kwargs
                                               )


        # self.collection_itms.append(lines_groupe)
        self.add_collections(lines_groupe)
        self.ax.add_collection(lines_groupe)
        self.bm.add_artist(lines_groupe)
        # self.ax.figure.canvas.draw_idle()
        self.bm.update()
        
        # self.ax.figure.canvas.draw_idle()

    # def okWindow(self):
    #
    #     # if len(self.ange_window.anglelist.keys()) > 0:
    #     #     pass
    #         # lineItem = dragableController(
    #         #     ange_window=self.ange_window, scene=self.scene, parent=self, DraggablePointList=self.DraggablePointList)
    #         #
    #         # # lineItem.copyAngle.triggered.connect(self.copyAngleFunc)
    #         # lineItem.minPoint.triggered.connect(self.minPointFunc)
    #         #
    #         # # self.DraggablePointList.append(lineItem)
    #     if self.ange_window.anglelist:
    #         # list_angles, list_colors = zip(*self.ange_window.anglelist.items())
    #         list_angles = list(self.ange_window.anglelist.keys())
    #         list_colors = list(self.ange_window.anglelist.values())
    #         self.draw_lines_collection(list_angles, list_colors,
    #                                    linewidth=self.ange_window.linewidth,
    #                                    alpha=self.ange_window.line_alpha)
    #     self.ange_window.hide()

    def set_limit_ax(self, myFactor):
        # plotShape = (970, 430)
        plotShape = (220, 100)
        self.ax.set_xlim([0, plotShape[0] * (myFactor / self.Fraction)])
        self.ax.set_ylim([self.df['Low'].min(), self.df['Low'].min(
        ) + plotShape[1] * (myFactor / self.Fraction)])

        # self.ax.set_xticks(np.arange(0, self.ax.get_xlim()[
        #                    1], myFactor/self.Fraction), minor=True)
        # self.ax.set_yticks(np.arange(self.ax.get_ylim()[0], self.ax.get_ylim()[
        #                    1], myFactor/self.Fraction), minor=True)
        k = (self.ax.get_xlim()[1] - self.grid_parametrs[8] * myFactor) / self.ax.get_xlim()[1]
        y_lim_custom = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * k

        self.ax.set_xlim([self.ax.get_xlim()[0], self.ax.get_xlim()[1] - self.grid_parametrs[8] * myFactor])
        self.ax.set_ylim([self.ax.get_ylim()[0], self.ax.get_ylim()[0] + y_lim_custom])

    def set_parametrs_ax(self):
        self.ax.xaxis.set_tick_params(which='minor', width=0.5)
        self.ax.yaxis.set_tick_params(which='minor', width=0.5)

        if self.df.shape[0] >= 100:
            self.ax.xaxis.set_tick_params(which='major', width=0.5)
            self.ax.yaxis.set_tick_params(which='major', width=0.5)

        self.ax.grid(which='major', axis='both', linestyle='-',
                     color=self.grid_parametrs[1], linewidth=self.grid_parametrs[3],
                     alpha=self.grid_parametrs[4], zorder=0, )
        self.ax.grid(which='minor', axis='both', linestyle=':',
                     color=self.grid_parametrs[2], linewidth=self.grid_parametrs[5],
                     alpha=self.grid_parametrs[6], zorder=0, )

        self.canvas.figure.set_facecolor(self.grid_parametrs[7])
        self.ax.set_facecolor(self.grid_parametrs[7])

        self.ax.set_aspect('equal')
        myFactor = self.factor * self.minPoint
        self.set_limit_ax(myFactor)

        self.step = self.grid_parametrs[0] * myFactor / self.Fraction

        x_locator = np.arange(0, max(len(self.df) * myFactor / self.Fraction, self.ax.get_xlim()[1]), self.step)
        y_locator = np.arange(self.ax.get_ylim()[0], max(self.ax.get_ylim()[1], self.df['High'].max()), self.step)
        x_label = self.df['DateTime'].tolist()
        count = len(x_locator) - len(x_label[::int(self.grid_parametrs[0])])
        len_x_label_with_step = self.gen_dop_label(count)

        range_xlabels = np.arange(0, max(len(self.df) * myFactor / self.Fraction, self.ax.get_xlim()[1]),
                                  myFactor / self.Fraction)
        range_xlabels = np.round(range_xlabels, 2)

        self.dict_label_x_with_data = dict(zip(range_xlabels, len_x_label_with_step))

        len_x_label_with_step = len_x_label_with_step[::int(self.grid_parametrs[0])]
        self.ax.minorticks_on()
        self.ax.xaxis.set_major_locator(FixedLocator(x_locator))
        self.ax.yaxis.set_major_locator(FixedLocator(y_locator))
        try:
            self.ax.set_xticklabels(len_x_label_with_step, rotation=55, fontsize=8)
        except Exception as e:
            print(e)
        self.ax.xaxis.set_minor_locator(AutoMinorLocator(self.grid_parametrs[0]))
        self.ax.yaxis.set_minor_locator(AutoMinorLocator(self.grid_parametrs[0]))

    def gen_dop_label(self, count=0) -> list:
        result = []
        dop = []
        max_datetime = self.df['DateTime'].max()

        if (self.df['DateTime'].dt.hour == 0).all():
            max_datetime += pd.Timedelta(days=1)
            freq = "D"
            datetime_format = '%Y.%m.%d'
        elif (self.df['DateTime'].dt.minute == 0).all():
            max_datetime += pd.Timedelta(hours=1)
            freq = "H"
            datetime_format = '%Y.%m.%d %H'
        else:
            time_delta_minute = 1

            try:
                if len(self.df) > 1:
                    time_delta_minute = abs(self.df.iloc[0, 7] - self.df.iloc[1, 7])
                    time_delta_minute = time_delta_minute.total_seconds()/60
            except AttributeError as exp:
                if len(self.df) > 1:
                    time_delta = self.df['DateTime'].iloc[1] - self.df['DateTime'].iloc[0]
                    time_delta_minute = time_delta.total_seconds() / 60  # Convert timedelta to minutes
            
            max_datetime += pd.Timedelta(minutes=time_delta_minute)
            freq = f'{time_delta_minute}T'
            datetime_format = '%Y.%m.%d %H:%M'
        if count > 0:
            dop = pd.date_range(max_datetime, periods=count * self.grid_parametrs[0], freq=freq)

        result.extend(self.df['DateTime'].dt.strftime(datetime_format).tolist())
        if len(dop) > 0:
            result.extend(dop.strftime(datetime_format).tolist())
        return result

    def plotMainDraph(self):
        # if self.worker_thread is None or not self.worker_thread.isRunning():
        self.coordinates_label.setVisible(True)
        self.coordinates_label.setValue(0)
        self.coordinates_label.setMaximum(len(self.df)+len(self.get_collections()))
        self.ax.clear()
        self.bm.remove_all()
        currentPos = 0
        self.set_parametrs_ax()
        self.cursor.add_dict_x_labels(self.dict_label_x_with_data, self.step)

        width = self.step
        if self.grid_parametrs[0] != 0:
            width /= self.grid_parametrs[0]
        ind = 0
        for index, row in self.df.iterrows():
            ind += 1
            self.coordinates_label.setValue(ind)
            # Draw outer rectangle
            heightOuter = (row['High']-row['Low'])
            heightInner = abs(row['Close']-row['Open'])
            innerMinVal = min([row['Close'], row['Open']])

            outer_rect = patches.Rectangle((currentPos, row['Low']), width, heightOuter, linewidth=0.5,
                                           edgecolor=self.grid_parametrs[11], facecolor='none', zorder=2)
            self.ax.add_patch(outer_rect)
            # Draw inner rectangle
            inner_rect = patches.Rectangle((currentPos, innerMinVal), width, heightInner, linewidth=0.5,
                                           facecolor= self.grid_parametrs[9] if (row['Close']-row['Open'] >= 0) else self.grid_parametrs[10], zorder=1)
            self.ax.add_patch(inner_rect)
            currentPos += width

        for lines_ in self.get_collections():
            print(lines_)
            if isinstance(lines_, LineDrawer): 
                if hasattr(lines_,'childrens'):
                    for artist in lines_.childrens:
                        if not artist.get_figure():
                            artist.set_figure(self.fig)
                # lines_.an1.set_figure(self.fig)
                # lines_.an2.set_figure(self.fig)
                # self.ax.add_artist(lines_.an1)
                # self.ax.add_artist(lines_.an2)
                
                # self.bm.add_artist(lines_.an1)
                # self.bm.add_artist(lines_.an2)
                # self.bm.add_artist(lines_.marker_collection)
            # else:
            self.ax.add_collection(lines_)
            self.bm.add_artist(lines_)
            ind += 1
            self.coordinates_label.setValue(ind)
        self.bm.update()    
        self.ax.figure.canvas.draw_idle()
        self.coordinates_label.setValue(0)
        self.coordinates_label.setVisible(False)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    df = pd.read_csv('exampl/EURUSD_MN.csv', names=[
        'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y.%m.%d %H:%M')
    df['Date'] = pd.to_datetime(df['Date'], format='%Y.%m.%d')
    plot_window = PlotWindow(df=df, persentageVal=0.8)
    plot_window.show()
    sys.exit(app.exec_())
