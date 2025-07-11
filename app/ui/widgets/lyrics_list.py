from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, 
                            QListWidgetItem, QAbstractItemView, QLabel, QApplication)
from PyQt5.QtCore import Qt, QMimeData, QByteArray, QDataStream, QIODevice, pyqtSignal, QSize
from PyQt5.QtGui import QDrag, QColor, QMouseEvent

class LyricsList(QWidget):
    # Signal emitted when items are reordered
    itemsReordered = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.drag_start_position = None
        
    def setup_ui(self):
        print("Setting up LyricsList UI...")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Lyrics list with drag and drop enabled
        print("Creating QListWidget...")
        self.lyric_list = QListWidget()
        print("Setting up QListWidget properties...")
        self.lyric_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lyric_list.setDragEnabled(True)
        self.lyric_list.setAcceptDrops(True)
        self.lyric_list.setDropIndicatorShown(True)
        self.lyric_list.setDefaultDropAction(Qt.MoveAction)
        self.lyric_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.lyric_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lyric_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lyric_list.setDragDropOverwriteMode(False)
        
        # Print debug info
        print(f"Drag enabled: {self.lyric_list.dragEnabled()}")
        print(f"Accept drops: {self.lyric_list.acceptDrops()}")
        print(f"Drag drop mode: {self.lyric_list.dragDropMode()}")
        print(f"Default drop action: {self.lyric_list.defaultDropAction()}")
        
        # Connect signals
        print("Connecting signals...")
        self.lyric_list.model().rowsMoved.connect(self._on_rows_moved)
        
        # Install event filter to handle mouse press events
        print("Installing event filter...")
        self.lyric_list.viewport().installEventFilter(self)
        print("Event filter installed")
        
        # Add lyrics button
        self.add_lyrics_btn = QPushButton("Add Lyrics")
        
        # Add widgets to layout
        layout.addWidget(self.lyric_list, 1)
        layout.addWidget(self.add_lyrics_btn)
        
    def connect_signals(self, context_menu_handler, add_lyrics_handler):
        """Connect external signal handlers to the widget's signals"""
        self.lyric_list.customContextMenuRequested.connect(context_menu_handler)
        self.add_lyrics_btn.clicked.connect(add_lyrics_handler)
        
    def clear(self):
        """Clear the lyrics list"""
        self.lyric_list.clear()
        
    def mousePressEvent(self, event):
        """Handle mouse press events to enable dragging"""
        print("Mouse press event detected")
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            print(f"Left button pressed at position: {self.drag_start_position}")
            
            # Forward the event to the list widget
            pos = self.lyric_list.viewport().mapFrom(self, event.pos())
            if pos.isValid():
                event = QMouseEvent(
                    event.type(), pos, event.button(), 
                    event.buttons(), event.modifiers()
                )
                QApplication.sendEvent(self.lyric_list.viewport(), event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events to enable dragging"""
        if not (event.buttons() & Qt.LeftButton):
            print("Mouse move event ignored - left button not pressed")
            return
            
        # Forward the event to the list widget
        pos = self.lyric_list.viewport().mapFrom(self, event.pos())
        if pos.isValid():
            event = QMouseEvent(
                event.type(), pos, event.button(), 
                event.buttons(), event.modifiers()
            )
            QApplication.sendEvent(self.lyric_list.viewport(), event)
            
        drag_distance = (event.pos() - self.drag_start_position).manhattanLength()
        min_drag_distance = QApplication.startDragDistance()
        print(f"Drag distance: {drag_distance}, Minimum: {min_drag_distance}")
        if drag_distance < min_drag_distance:
            print("Drag distance too small, not starting drag")
            return
            
        item = self.lyric_list.itemAt(self.drag_start_position)
        print(f"Item at position: {item}")
        if not item:
            print("No item at drag start position")
            return
            
        # Only allow dragging for non-section items
        data = item.data(Qt.UserRole) or {}
        print(f"Item data: {data}")
        if data.get('is_section_header', False):
            print("Item is a section header, dragging disabled")
            return
            
        # Start drag operation
        print("Starting drag operation")
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(item.text())
        print(f"Dragging item with text: {item.text()}")
        
        # Store the source index
        byte_array = QByteArray()
        stream = QDataStream(byte_array, QIODevice.WriteOnly)
        stream.writeInt(self.lyric_list.row(item))
        mime_data.setData('application/x-qabstractitemmodeldatalist', byte_array)
        
        drag.setMimeData(mime_data)
        drag.setHotSpot(event.pos() - self.lyric_list.visualItemRect(item).topLeft())
        
        # Start the drag operation
        print("Executing drag operation...")
        result = drag.exec_(Qt.MoveAction | Qt.CopyAction, Qt.MoveAction)
        print(f"Drag operation completed with result: {result}")
        if result == Qt.MoveAction:
            print("Move action was successful")
        else:
            print("Move action was not successful")
        
    def add_item(self, text, data=None, is_section_header=False):
        """
        Add an item to the lyrics list
        
        Args:
            text (str): The display text for the item
            data (any, optional): Any additional data to store with the item
            is_section_header (bool): Whether this is a section header
        """
        if is_section_header or (hasattr(data, 'get') and data.get('is_section_header', False)):
            # Create a section header item
            section_item = QListWidgetItem()
            section_item.setFlags(Qt.NoItemFlags)
            section_item.setSizeHint(QSize(0, 24))
            
            section_widget = QLabel(f"<b>{text or 'No Section'}</b>")
            section_widget.setStyleSheet("""
                background-color: #f1f3f5;
                padding: 2px 8px;
                border-radius: 2px;
                margin: 1px 0;
                font-size: 12px;
            """)
            
            self.lyric_list.addItem(section_item)
            self.lyric_list.setItemWidget(section_item, section_widget)
            
            # Store the section data
            if data is None:
                data = {}
            data['is_section_header'] = True
            section_item.setData(Qt.UserRole, data)
            return section_item
        else:
            # Regular lyric item
            item = QListWidgetItem(text)
            if data is not None:
                item.setData(Qt.UserRole, data)
            
            # Enable dragging and selection
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            item.setData(Qt.UserRole + 1, 'lyric')  # Add a custom role to identify lyric items
            
            # Set alternating row colors
            if self.lyric_list.count() % 2 == 0:
                item.setBackground(QColor(250, 250, 250))
            else:
                item.setBackground(QColor(255, 255, 255))
                
            self.lyric_list.addItem(item)
            return item
        
    def current_index(self):
        """Get the current selected index"""
        return self.lyric_list.currentRow()
        
    def get_items_data(self):
        """Get a list of all items' data"""
        items_data = []
        for i in range(self.lyric_list.count()):
            item = self.lyric_list.item(i)
            items_data.append({
                'text': item.text(),
                'data': item.data(Qt.UserRole)
            })
        return items_data
        
    def set_items_data(self, items_data):
        """Set items from a list of data"""
        self.lyric_list.clear()
        for item_data in items_data:
            is_section = item_data.get('data', {}).get('is_section_header', False)
            self.add_item(
                text=item_data['text'], 
                data=item_data.get('data'),
                is_section_header=is_section
            )
        
    def _on_rows_moved(self, parent, start, end, destination, row):
        """Handle when rows are moved via drag and drop"""
        print(f"Rows moved: start={start}, end={end}, destination={row}")
        print("Emitting itemsReordered signal")
        self.itemsReordered.emit()
        
    def get_all_items_data(self):
        """Get data for all items in the current order"""
        items_data = []
        for i in range(self.lyric_list.count()):
            item = self.lyric_list.item(i)
            if item:
                data = item.data(Qt.UserRole) or {}
                is_section = data.get('is_section_header', False)
                items_data.append({
                    'text': item.text(),
                    'data': data,
                    'is_section_header': is_section
                })
        return items_data
        
    def set_current_index(self, index):
        """Set the current selected index"""
        if 0 <= index < self.lyric_list.count():
            self.lyric_list.setCurrentRow(index)
            
    def get_section_at_index(self, index):
        """Get the section name for the item at the given index"""
        if index < 0 or index >= self.lyric_list.count():
            return None
            
        # Find the nearest section header above this item
        for i in range(index, -1, -1):
            item = self.lyric_list.item(i)
            if item:
                data = item.data(Qt.UserRole) or {}
                if data.get('is_section_header', False):
                    # Get the text from the section widget
                    widget = self.lyric_list.itemWidget(item)
                    if widget and hasattr(widget, 'text'):
                        return widget.text().replace('<b>', '').replace('</b>', '').strip()
        return None
