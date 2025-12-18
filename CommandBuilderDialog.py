import subprocess
import json
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QCompleter
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox
from PyQt5 import QtWidgets 

class CommandBuilderDialog(QDialog):
    def __init__(self, x, y, command_def_file="commands.json"):
        super().__init__()
        self.setWindowTitle("Commandes")
        self.setWindowFlags(Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(900, 800)
        self.move(x, y)

        self.option_widgets = {}
        self.commands = self.load_command_definitions(command_def_file)

        content = QWidget()
        content.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 180);
                border-radius: 12px;
                color: white;
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: rgba(255, 255, 255, 30);
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 6px;
                padding: 4px;
                color: white;
            }
            QComboBox {
                background-color: rgba(255, 255, 255, 30);
                border: 1px solid rgba(255, 255, 255, 50);
                border-radius: 6px;
                padding: 4px;
                color: white;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 30);
                border: 1px solid rgba(255, 255, 255, 60);
                border-radius: 6px;
                padding: 6px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 60);
            }

            /* Scrollbars */
            QScrollBar:vertical {
                background: rgba(50, 50, 50, 180);
                width: 18px;
                margin: 20px 0 20px 0;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(200, 200, 200, 180);
                min-height: 40px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 220);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 20px;
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                background: rgba(50, 50, 50, 180);
                height: 18px;
                margin: 0 20px 0 20px;
                border-radius: 8px;
            }
            QScrollBar::handle:horizontal {
                background: rgba(200, 200, 200, 180);
                min-width: 40px;
                border-radius: 8px;
            }
            QScrollBar::handle:horizontal:hover {
                background: rgba(255, 255, 255, 220);
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 20px;
                background: none;
                border: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid white;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: white;
                image: url(:/qt-project.org/styles/commonstyle/images/checkbox_checked.png);
            }
            QCheckBox::indicator:unchecked {
                background-color: transparent;
            }
        """)

        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(10)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Entrez une commande...")
        completer = QCompleter(self.commands.keys())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.command_input.setCompleter(completer)
        self.command_input.editingFinished.connect(self.update_options_ui)
        completer.activated.connect(lambda text: self.command_input.setText(text) or self.update_options_ui())

        # Zone pour afficher la commande complète + bouton "Copier"
        self.command_widget = QWidget()
        self.command_layout = QHBoxLayout(self.command_widget)
        self.command_layout.setContentsMargins(0, 0, 0, 0)

        self.command_show = QLineEdit()
        self.command_show.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 50);
                border: 1px solid #ccc;
                border-radius: 5px;
                font-weight: bold;
                color: white;
                padding: 6px;
            }
        """)
        self.command_show.setMaximumHeight(40)
        self.command_show.editingFinished.connect(self.set_options_ui_from_preview)

        copy_button = QPushButton("Copier")
        copy_button.setFixedHeight(30)

        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(self.command_show.text()))

        self.input_fields = {}

        self.command_layout.addWidget(self.command_show)
        self.command_layout.addWidget(copy_button)

        # Invisible par défaut
        self.command_widget.hide()

        self.options_container = QWidget()
        self.options_layout = QVBoxLayout(self.options_container)
        self.options_layout.setSpacing(8)

        # Ajouter le widget de commande au layout AVANT la scroll_area
        self.content_layout.addWidget(self.command_input)
        self.content_layout.addWidget(self.command_widget)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.options_container)
        self.scroll_area.setStyleSheet("QScrollArea { background: transparent; }")
        self.content_layout.addWidget(self.scroll_area)

        self.execute_button = QPushButton("Exécuter")
        self.execute_button.setFixedHeight(32)
        self.execute_button.clicked.connect(self.handle_execute)
        self.content_layout.addWidget(self.execute_button)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(content)

        self.update_options_ui()


    def compact_shell_command(self, command: str) -> str:
        parts = command.strip().split()
        if not parts:
            return ""

        cmd = parts[0]
        short_flags = []
        long_flags = []
        long_options = []
        other_args = []

        i = 1
        while i < len(parts):
            part = parts[i]

            # Option longue
            if part.startswith("--"):
                long_options.append(part)
            # Option courte seule (ex: -a)
            elif part.startswith("-") and len(part) == 2:
                short_flags.append(part[1])
            # Option longue seule avec tiret simple (ex: -depth)
            elif part.startswith("-") and len(part) > 2:
                long_flags.append(part)
            # ex: -lh
            elif part.startswith("-") and not part.startswith("--"):
                short_flags.extend(list(part[1:]))
            else:
                other_args.append(part)
            i += 1

        # Reconstruire la commande
        result = [cmd]
        if short_flags:
            result.append(f"-{''.join(short_flags)}")
        result.extend(long_options)
        result.extend(long_flags)
        result.extend(other_args)
        return " ".join(result)

    def load_command_definitions(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def set_options_ui_from_preview(self):
        current_command = self.command_show.text().strip()
        if not current_command:
            return

        # 2) Construction de l’ensemble des flags présents dans la commande
        tokens = current_command.split()[1:]      # on ignore le premier « mot » (la commande elle-même)
        found_checkbox_flags: set[str] = set()
        found_checkbox_flags_full: set[str] = set()
        found_select_flags: set[str] = set()

        for token in tokens:
            # --flag-long
            if token.startswith('--'):
                if "=" in token:
                    found_select_flags.add(token)
                else:
                    found_checkbox_flags.add(token)
            # -abc  -> -a -b -c
            elif token.startswith('-') and len(token) > 1:
                found_checkbox_flags_full.add(token)
                for ch in token[1:]:
                    found_checkbox_flags.add(f'-{ch}')
            elif token.startswith('-') and len(token) > 1:
                found_checkbox_flags.add(f'-{token[1:]}')

        # 3) Activation des cases à cocher correspondantes
        for _label, (meta, widget) in self.option_widgets.items():
            # ex. '-l' ou '--help'
            flag = meta.get('flag')
            if flag in found_checkbox_flags_full and isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(True)
            elif flag not in found_checkbox_flags_full and isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(False)
            if flag in found_checkbox_flags and isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(True)
            if flag not in found_checkbox_flags and isinstance(widget, QtWidgets.QCheckBox):
                widget.setChecked(False)
            if "=" in flag:
                flag = flag.replace("[", "").replace("]", "")
                decomposed_flag = flag.split("=")
                # ex: 'myflag'
                composed_flag = decomposed_flag[0]

                # On cherche l'entrée complète dans found_select_flags, ex: "myflag=value"
                matching_flag = next((item for item in found_select_flags if item.startswith(composed_flag + "=")), None)

                if matching_flag and isinstance(widget, QtWidgets.QComboBox):
                    value = matching_flag.split("=")[1]
                    index = widget.findText(value)
                    widget.setCurrentIndex(index if index >= 0 else 0)

                elif not matching_flag and isinstance(widget, QtWidgets.QComboBox):
                    widget.setCurrentIndex(0)

    def update_options_ui(self):

        for i in reversed(range(self.options_layout.count())):
            widget = self.options_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        # for i in reversed(range(self.content_layout.count())):
        #     widget = self.content_layout.itemAt(i).widget()
        # if widget:
        #     widget.deleteLater()
        self.option_widgets.clear()

        cmd = self.command_input.text().strip()

        if not cmd or cmd not in self.commands:
            self.command_widget.hide()
            return

        # Commande reconnue → on affiche la zone de prévisualisation
        self.command_show.setText(cmd)
        self.command_widget.show()

        # Affichage de la description
        if self.commands[cmd].get("description"):
            description = QLabel(self.commands[cmd]["description"].strip().replace("\n\n", ""))
            description.setWordWrap(True)
            description.setStyleSheet("""
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-weight: bold;
                color: black;
            """)
            self.options_layout.addWidget(description)

        if self.commands[cmd].get("input") and len(self.commands[cmd]["input"]) > 0:
            for input_name in self.commands[cmd]["input"]:
                if input_name not in self.input_fields:
                    input_label = QLabel(input_name)
                    input_line = QLineEdit()
                    input_line.setFixedWidth(350)
                    self.content_layout.addWidget(input_label)
                    self.content_layout.addWidget(input_line)

                    # on stocke le champ
                    self.input_fields[input_name] = input_line 

                    input_line.textChanged.connect(self.update_command_preview)

        # Création des options
        for option in self.commands[cmd]["options"]:
            cleaned_flag = str(option['flag']).split(";")[0]
            label_text = f"{cleaned_flag} : {option['label']}"
            field_type = option["type"]

            if field_type == "text":
                label = QLabel(label_text)
                line = QLineEdit()
                line.setFixedWidth(350)
                if "default" in option:
                    line.setText(option["default"])
                line.textChanged.connect(self.update_command_preview)
                self.options_layout.addWidget(label)
                self.options_layout.addWidget(line)
                self.option_widgets[label_text] = (option, line)

            elif field_type == "checkbox":
                checkbox = QCheckBox(label_text)
                checkbox.stateChanged.connect(self.update_command_preview)
                self.options_layout.addWidget(checkbox)
                self.option_widgets[label_text] = (option, checkbox)

            elif field_type == "select":
                combo = QComboBox()
                combo.setFixedWidth(350)
                items = option["flag"].split(";")
                combo.addItems(items[1:])
                combo.currentIndexChanged.connect(self.update_command_preview)
                self.options_layout.addWidget(QLabel(label_text))
                self.options_layout.addWidget(combo)
                self.option_widgets[label_text] = (option, combo)
        
        # Affichage de la ending
        if self.commands[cmd].get("ending"):
            ending = QLabel(self.commands[cmd]["ending"].strip().replace("\n\n", ""))
            ending.setWordWrap(True)
            ending.setStyleSheet("""
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-weight: bold;
                color: black;
            """)
            self.options_layout.addWidget(ending)

        # self.activateWindow()
        # self.raise_()
        # self.setFocus()
        if os.environ.get("XDG_SESSION_TYPE") != "wayland":
            self.activateWindow()
            self.raise_()
            self.setFocus()

    def update_command_preview(self):
        cmd = self.command_input.text().strip()
        if cmd not in self.commands:
            self.command_show.setText("")
            return
        # options = self.commands[cmd]["options"]
        parts = [cmd]

        for label, (meta, widget) in self.option_widgets.items():
            flag = meta["flag"]
            if meta["type"] == "text":
                value = widget.text().strip()
                if value:
                    if flag == "path":
                        parts.append(value)
                    else:
                        flag = flag.replace("[", "").replace("]", "")
                        decomposed_flag = flag.split("=")
                        composed_flag = f"{decomposed_flag[0]}="
                        parts += [f"{composed_flag}{value}"]

            elif meta["type"] == "checkbox":
                if widget.isChecked():
                    parts += flag.split(" ")

            elif meta["type"] == "select":
                flag = flag.replace("[", "").replace("]", "")
                flag_array = flag.split(";")
                decomposed_flag = flag_array[0].split("=")
                composed_flag = f"{decomposed_flag[0]}="
                value = widget.currentText().strip()
                if value:
                    parts += [f"{composed_flag}{value}"]

        command_str = " ".join(parts)
        compact_command = self.compact_shell_command(command_str)
        inputs = " ".join(
            field.text().strip()
            for field in self.input_fields.values()
            if field.text().strip()
        )
        self.command_show.setText(f"{compact_command} {inputs}")

    def handle_execute(self):
        cmd = self.command_input.text().strip()
        # options = self.commands[cmd]["options"]
        parts = [cmd]

        for label, (meta, widget) in self.option_widgets.items():
            flag = meta["flag"]
            if meta["type"] == "text":
                value = widget.text().strip()
                if value:
                    if flag == "path":
                        parts.append(value)
                    else:
                        flag = flag.replace("[", "").replace("]", "")
                        decomposed_flag = flag.split("=")

                        # Garder uniquement la partie avant le "=" suivie du "="
                        composed_flag = f"{decomposed_flag[0]}="
                        parts += [f"{composed_flag}{value}"]
            elif meta["type"] == "checkbox":
                if widget.isChecked():
                    parts += flag.split(" ")

            elif meta["type"] == "select":
                flag = flag.replace("[", "").replace("]", "")
                flag_array = flag.split(";")
                decomposed_flag = flag_array[0].split("=")
                composed_flag = f"{decomposed_flag[0]}="
                value = widget.currentText().strip()
                if value:
                    parts += [f"{composed_flag}{value}"]

        command_str = " ".join(parts)
        inputs = " ".join(
            field.text().strip()
            for field in self.input_fields.values()
            if field.text().strip()
        )
        final_command = f"{command_str} {inputs}"
        compact_command = self.compact_shell_command(final_command.strip())
        self.run_in_gnome_terminal(compact_command)

    def run_in_gnome_terminal(self, command):
        command_array = str(command).split(" ")
        full_command = command
        if "ls" in str(command).strip() and "/" not in str(command).strip():
            actual_path = subprocess.run("pwd", shell=True, capture_output=True, text=True)
            full_command = f"{command} {actual_path.stdout.strip()}"
        subprocess.Popen([
            'xterm',
            '-hold',
            '-fa', 'Monospace',
            '-fs', '12',
            '-T', full_command,
            '-e', command
        ], stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    x = 100
    y = 100
    dialog = CommandBuilderDialog(x, y)
    dialog.exec_()

    sys.exit(0)
