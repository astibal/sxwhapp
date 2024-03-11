import logging
import os

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QAction, QFileDialog, QMessageBox

from ui.config import Config
from ui.mdviewer import MarkdownViewer, Text
from ui.tab_content import ContentWidget
from ui.tab_workbench import WorkbenchTab
from ui.tab_log import LogWidget
from ui.settings_dialog import SettingsDialog

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(MainWindow.make_title_str())
        self.setGeometry(100, 100, 1200, 800)


        with Config.lock:
            tls_failed = Config.config['use_tls'] and not Config.ssl_context

        if tls_failed:
            m = QMessageBox(QMessageBox.Icon.Warning, "Error setting TLS server",
                            "Server running in plaintext!!\n\n"
                            "Check your configuration, please")
            m.exec()
            log.error("Error setting TLS server: fallback, running in plaintext!")

        project_menu = self.menuBar().addMenu('Options')
        open_project_menu = QAction('Project Directory', self)
        project_menu.addAction(open_project_menu)
        open_project_menu.triggered.connect(self.open_project_dir)

        setting_action = QAction("General settings (requires restart)", self)
        setting_action.setToolTip("General settings (requires restart)")
        setting_action.triggered.connect(self.show_settings_dialog)
        project_menu.addAction(setting_action)

        help_menu = self.menuBar().addMenu('Help')
        help_menu_content = QAction("Content", self)
        help_menu.addAction(help_menu_content)
        help_menu_content.triggered.connect(self.help_content)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)

        self.content_widget = ContentWidget()
        self.tab_widget.addTab(self.content_widget, 'Content')

        self.workbench_widget = WorkbenchTab()
        self.tab_widget.addTab(self.workbench_widget, 'Workbench')

        self.log_widget = LogWidget()
        self.tab_widget.addTab(self.log_widget, 'Logs')

        self.setCentralWidget(self.tab_widget)

    @staticmethod
    def make_title_str():
        return f'Smithproxy WebHook Application - {Config.config["project_path"]}'

    def open_project_dir(self):
        parent_dir = os.path.dirname(Config.config['project_path'])
        directory = QFileDialog.getExistingDirectory(None, "Select Directory", directory=parent_dir)

        # do not continue if Cancelled
        if not directory:
            return

        with Config.lock:
            Config.config['project_path'] = directory

        Config.save_config()

        self.content_widget.on_script_slot_button(1)
        self.setWindowTitle(MainWindow.make_title_str())

    def help_content(self):
        self.help_viewer = MarkdownViewer()
        self.help_viewer.setMarkdown(Text.Help_ContentTab.markdown)
        self.help_viewer.show()
        self.help_viewer.raise_()
        self.help_viewer.activateWindow()

    def show_settings_dialog(self):
        dialog = SettingsDialog()
        dialog.exec_()