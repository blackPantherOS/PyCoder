import os
import sys
import re
import codecs
import traceback
import logging
# FIXME QtXml is no longer supported.
from PyQt6 import QtCore, QtXml
from PyQt6.Qsci import QsciScintilla

from Extensions_Qt6.Workspace import WorkSpace


def textEncoding(bb):
    """ Get the encoding used to encode a file.
    Accepts the bytes of the file. Returns the codec name. If the
    codec could not be determined, uses UTF-8.
    """

    # Get first two lines
    parts = bb.split(b'\n', 2)

    # Init to default encoding
    encoding = 'UTF-8'

    # Determine encoding from first two lines
    for i in range(len(parts) - 1):

        # Get line
        try:
            line = parts[i].decode('ASCII')
        except Exception:
            continue

        # Search for encoding directive

        # Has comment?
        if line and line[0] == '#':

            # Matches regular expression given in PEP 0263?
            expression = "coding[:=]\s*([-\w.]+)"
            result = re.search(expression, line)
            if result:

                # Is it a known encoding? Correct name if it is
                candidate_encoding = result.group(1)
                try:
                    c = codecs.lookup(candidate_encoding)
                    candidate_encoding = c.name
                except Exception:
                    pass
                else:
                    encoding = candidate_encoding

    # Done
    return encoding


def lineEnding(text):
    c_win = text.count("\r\n")
    c_mac = text.count("\r") - c_win
    c_lin = text.count("\n") - c_win

    if c_win > c_mac and c_win > c_lin:
        mode = QsciScintilla.EolWindows
    elif c_mac > c_win and c_mac > c_lin:
        mode = QsciScintilla.EolMac
    else:
        mode = QsciScintilla.EolMode.EolUnix

    return mode


class FindInstalledPython(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    # Find all python executables
    def __str__(self):
        return f"FindInstalledPython instance with interpreters: {self.python_executables()}"

    def python_executables(self):
        try:
            if sys.platform.startswith('win'):
                return self.windows()
            else:
                return self.posix()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))

            return []

    def windows(self):

        import winreg

        # Open base key
        base = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        try:
            key = winreg.OpenKey(
                base, 'SOFTWARE\\Python\\PythonCore', 0, winreg.KEY_READ)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))

            return []

        # Get info about subkeys
        nsub, nval, modified = winreg.QueryInfoKey(key)

        # Query Python versions from registry
        versionList = []
        for i in range(nsub):
            try:
                # Get name and subkey
                name = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(
                    key, name + '\\InstallPath', 0, winreg.KEY_READ)
                # Get install location and store
                location = winreg.QueryValue(subkey, '')
                versionList.append(os.path.normpath(location))
                # Close
                winreg.CloseKey(subkey)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(
                    repr(traceback.format_exception(exc_type, exc_value,
                             exc_traceback)))

        # Close keys
        winreg.CloseKey(key)
        winreg.CloseKey(base)

        # Query Python versions from file system
        for rootname in ['C:/', 'C:/Program Files', 'C:/Program Files (x86)']:
            if not os.path.isdir(rootname):
                continue
            for dir_item in os.listdir(rootname):
                if dir_item.lower().startswith('python'):
                    path = os.path.normpath(os.path.join(rootname, dir_item))
                    if path not in versionList:
                        versionList.append(path)

        # Append "python.exe" and check if that file exists
        versions3 = []

        for path in versionList:
            exe_name = os.path.join(path, 'python.exe')
            if os.path.isfile(exe_name):
                versions3.append(exe_name)

        return versions3

    def posix(self):
        found = []
        for searchpath in ['/usr/bin', '/usr/local/bin', '/opt/local/bin']:
            # Get files
            try:
                files = os.listdir(searchpath)
            except:
                continue

            # Search for python executables
            for fname in sorted(files):
                full_path = os.path.join(searchpath, fname)
                if os.path.islink(full_path):
                    link_target = os.readlink(full_path)
                    match = re.match(r'pythonOLD(\d.*)', fname)
                    if match:
                        found.append(full_path)
                    elif fname.startswith('python3') and not fname.count('config') and not '-' in fname and not '_' in fname:
                        found.append(full_path)

        # Sort the list to ensure the correct order
        # found.sort(key=lambda x: ('python3' in x, x))
        # Done
        return found

    #def formatted_str(self):
    #    return "Custom formatting for FindInstalledPython"

class UseData(QtCore.QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

        # usedata lists
        self.SETTINGS = {}
        self.OPENED_PROJECTS = []
        self.supportedFileTypes = ["python", ".xml", ".css", ".html"]

        # default shortcuts
        self.DEFAULT_SHORTCUTS = {
            'Ide': {
                "Go-to-Line": "Alt+G",
                "New-File": "Ctrl+N",
                "Open-File": "Ctrl+O",
                "Save-File": "Ctrl+S",
                "Save-All": "Ctrl+Shift+S",
                "Print": "Ctrl+P",
                "Run-File": "F4",
                "Run-Project": "F5",
                "Build": "Ctrl+Shift+B",
                "Stop-Execution": "F6",
                "Fullscreen": "F8",
                "Find": "Ctrl+F",
                "Replace": "Ctrl+H",
                "Find-Next": "Ctrl+G",
                "Find-Previous": "Shift+F3",
                "Help": "F2",
                "Python-Manuals": "F1",
                "Split-Horizontal": "F10",
                "Split-Vertical": "F9",
                "Remove-Split": "F11",
                "Reload-File": "F7",
                "Change-Tab": "F12",
                "Change-Tab-Reverse": "Ctrl+Tab",
                "Change-Split-Focus": "Ctrl+M",
                "Fold-Code": "",
                "Snippets": "Ctrl+K",
                "Toggle-Indentation-Guide": "Alt+I",
                "Toggle-Breakpoint": "Alt+B",
                "Select-to-Matching-Brace": "",
                "Next-Bookmark": "",
                "Previous-Bookmark": "",
                "Comment": "Ctrl+E",
                "Uncomment": "Alt+E",
                "Show-Completion": "Ctrl+Space",
                },
            'Editor': {'Move-To-End-Of-Document': ['Ctrl+End', 2318],
                       'Zoom-Out': ['Ctrl+-', 2334],
                       'Extend-Rectangular-Selection-Left-One-Character': ['Alt+Shift+Left', 2428],
                       'Move-Down-One-Paragraph': ['Ctrl+]', 2413],
                       'Move-To-Start-Of-Document': ['Ctrl+Home', 2316],
                       'Extend-Selection-To-Start-Of-Display-Line': ['', 2346],
                       'De-indent-One-Level': ['Shift+Tab', 2328],
                       'Delete-Right-To-End-Of-Next-Word': ['', 2518],
                       'Extend-Selection-Down-One-Line': ['Shift+Down', 2301],
                       'Scroll-Vertically-To-Centre-Current-Line': ['', 2619],
                       'Toggle-Insert-or-Overtype': ['Ins', 2324],
                       'Extend-Rectangular-Selection-Up-One-Line': ['Alt+Shift+Up', 2427],
                       'Extend-Rectangular-Selection-Down-One-Line': ['Alt+Shift+Down', 2426],
                       'Extend-Selection-Left-One-Character': ['Shift+Left', 2305],
                       'Select-All': ['Ctrl+A', 2013],
                       'Convert-Selection-To-Upper-Case': ['Ctrl+Shift+U', 2341],
                       'Insert-Newline': ['Return', 2329],
                       'Move-Right-One-Word-Part': ['Ctrl+\\', 2392],
                       'Move-To-First-Visible-Character-In-Document-Line': ['Home', 2331],
                       'Extend-Rectangular-Selection-To-First-Visible-Character-In-Document-Line': ['Alt+Shift+Home', 2431],
                       'Extend-Selection-Down-One-Page': ['Shift+PgDown', 2323],
                       'Move-Selected-Lines-Down-One-Line': ['', 2621],
                       'Move-Right-One-Word': ['Ctrl+Right', 2310],
                       'Move-Up-One-Page': ['PgUp', 2320],
                       'Extend-Rectangular-Selection-To-Start-Of-Document-Line': ['', 2430],
                       'Extend-Selection-Left-One-Word': ['Ctrl+Shift+Left', 2309],
                       'Scroll-View-Down-One-Line': ['Ctrl+Down', 2342],
                       'Extend-Selection-Left-One-Word-Part': ['Ctrl+Shift+/', 2391],
                       'Duplicate-Selection': ['Ctrl+D', 2469],
                       'Cut-Selection': ['Ctrl+X', 2177],
                       'Extend-Selection-Down-One-Paragraph': ['Ctrl+Shift+]', 2414],
                       'Extend-Selection-To-End-Of-Previous-Word': ['', 2440],
                       'Extend-Selection-To-Start-Of-Document-Line': ['', 2313],
                       'Move-Selected-Lines-Up-One-Line': ['', 2620],
                       'Stuttered-Move-Up-One-Page': ['', 2435],
                       'Extend-Selection-Right-One-Character': ['Shift+Right', 2307],
                       'Cancel': ['Esc', 2325],
                       'Scroll-View-Up-One-Line': ['Ctrl+Up', 2343],
                       'Cut-Current-Line': ['Ctrl+L', 2337],
                       'Stuttered-Extend-Selection-Down-One-Page': ['', 2438],
                       'Extend-Selection-To-End-Of-Display-Or-Document-Line': ['', 2452],
                       'Move-Up-One-Paragraph': ['Ctrl+[', 2415],
                       'Move-Left-One-Word': ['Ctrl+Left', 2308],
                       'Formfeed': ['', 2330],
                       'Undo-Last-Command': ['Ctrl+Z', 2176],
                       'Delete-Line-To-Left': ['Ctrl+Shift+Backspace', 2395],
                       'Delete-Word-To-Left': ['Ctrl+Backspace', 2335],
                       'Extend-Rectangular-Selection-To-End-Of-Document-Line': ['Alt+Shift+End', 2432],
                       'Move-To-End-Of-Display-Or-Document-Line': ['', 2451],
                       'Delete-Current-Character': ['Del', 2180],
                       'Stuttered-Move-Down-One-Page': ['', 2437],
                       'Move-Right-One-Character': ['Right', 2306],
                       'Move-To-End-Of-Previous-Word': ['', 2439],
                       'Extend-Selection-To-First-Visible-Character-In-Document-Line': ['Shift+Home', 2332],
                       'Move-Down-One-Line': ['Down', 2300],
                       'Scroll-To-Start-Of-Document': ['', 2628],
                       'Extend-Selection-To-Start-Of-Display-Or-Document-Line': ['', 2450],
                       'Move-Down-One-Page': ['PgDown', 2322],
                       'Move-To-End-Of-Document-Line': ['End', 2314],
                       'Delete-Word-To-Right': ['Ctrl+Del', 2336],
                       'Convert-Selection-To-Lower-Case': ['Ctrl+U', 2340],
                       'Extend-Selection-Up-One-Paragraph': ['Ctrl+Shift+[', 2416],
                       'Move-Up-One-Line': ['Up', 2302],
                       'Extend-Selection-To-Start-Of-Document': ['Ctrl+Shift+Home', 2317],
                       'Delete-Current-Line': ['Ctrl+Shift+L', 2338],
                       'Paste': ['Ctrl+V', 2179],
                       'Extend-Selection-Right-One-Word-Part': ['Ctrl+Shift+\\', 2393],
                       'Extend-Selection-To-First-Visible-Character-In-Display-Or-Document-Line': ['', 2454],
                       'Extend-Selection-To-End-Of-Next-Word': ['', 2442],
                       'Move-Left-One-Character': ['Left', 2304],
                       'Redo-Last-Command': ['Ctrl+Y', 2011],
                       'Move-Left-One-Word-Part': ['Ctrl+/', 2390],
                       'Stuttered-Extend-Selection-Up-One-Page': ['', 2436],
                       'Delete-Line-To-Right': ['Ctrl+Shift+Del', 2396],
                       'Extend-Rectangular-Selection-Right-One-Character': ['Alt+Shift+Right', 2429],
                       'Transpose-Current-And-Previous-Lines': ['Ctrl+T', 2339],
                       'Indent-One-Level': ['Tab', 2327],
                       'Extend-Selection-Right-One-Word': ['Ctrl+Shift+Right', 2311],
                       'Copy-Selection': ['Ctrl+C', 2178],
                       'Extend-Selection-To-End-Of-Display-Line': ['', 2315],
                       'Extend-Selection-To-End-Of-Document-Line': ['Shift+End', 2315],
                       'Extend-Rectangular-Selection-Up-One-Page': ['Alt+Shift+PgUp', 2433],
                       'Extend-Rectangular-Selection-Down-One-Page': ['Alt+Shift+PgDown', 2434],
                       'Move-To-Start-Of-Document-Line': ['', 2312],
                       'Delete-Previous-Character': ['Backspace', 2326],
                       'Delete-Previous-Character-If-Not-At-Start-Of-Line': ['', 2344],
                       'Zoom-In': ['Ctrl++', 2333],
                       'Move-To-Start-Of-Display-Or-Document-Line': ['', 2349],
                       'Move-To-First-Visible-Character-Of-Display-In-Document-Line': ['', 2453],
                       'Extend-Selection-Up-One-Line': ['Shift+Up', 2303],
                       'Copy-Current-Line': ['Ctrl+Shift+T', 2455],
                       'Move-To-Start-Of-Display-Line': ['Alt+Home', 2345],
                       'Move-To-End-Of-Next-Word': ['', 2441],
                       'Duplicate-The-Current-Line': ['', 2404],
                       'Move-To-End-Of-Display-Line': ['Alt+End', 2347],
                       'Extend-Selection-To-End-Of-Document': ['Ctrl+Shift+End', 2319],
                       'Extend-Selection-Up-One-Page': ['Shift+PgUp', 2321],
                       'Scroll-To-End-Of-Document': ['', 2629]}
            }

        self.CUSTOM_SHORTCUTS = {'Ide': {}, 'Editor': {}}

        config_path = os.path.expanduser("~/.config/pycoder")
        config_file = "settings.ini"
        settings_file_path = os.path.join(config_path, config_file)

        if not os.path.exists(config_path):
            print("Dir not found! Create..")
            os.makedirs(config_path, exist_ok=True)

        if not os.path.exists(settings_file_path):
            print(f"Copying {config_file} from current directory to {settings_file_path}")
            self.copySettingsFromCurrentDirectory(settings_file_path)

        # load configuration from file
        tempList = []
        try:
            file = open(settings_file_path, "r")
        except:
            file = open("settings.ini", "r")

        for i in file.readlines():
            if i.strip() == '':
                pass
            else:
                tempList.append(tuple(i.strip().split('=')))
        file.close()
        self.settings = dict(tempList)

        self.loadAppData()
        self.loadUseData()

        self.SETTINGS["InstalledInterpreters"] = self.getPythonExecutables()

    def copySettingsFromCurrentDirectory(self, destination_path):
        try:
            # Read the content of the source file
            with open("settings.ini", "r") as source_file:
                content = source_file.read()

            # Write the content to the destination path
            with open(destination_path, "w") as destination_file:
                destination_file.write(content)
            print(f"Settings copied successfully")

        except Exception as e:
            print(f"Error copying settings.ini: {e}")

    def loadAppData(self):
        self.workspaceDir = self.settings["workspace"]
        if not os.path.exists(self.workspaceDir):
            newWorkspace = WorkSpace()
            if newWorkspace.created:
                self.workspaceDir = newWorkspace.path
                self.settings["workspace"] = self.workspaceDir
            else:
                sys.exit()
        self.appPathDict = {
            "logfile": os.path.join(self.workspaceDir, "LOG.txt"),
            "snippetsdir": os.path.join(self.workspaceDir, "Snippets"),
            "librarydir": os.path.join(self.workspaceDir, "Library"),
            "projectsdir": os.path.join(self.workspaceDir, "Projects"),
            "settingsdir": os.path.join(self.workspaceDir, "Settings"),
            "stylesdir": os.path.join(self.workspaceDir, "Settings", "ColorSchemes"),
            "usedata": os.path.join(self.workspaceDir, "Settings", "usedata.xml"),
            "modules": os.path.join(self.workspaceDir, "Settings", "modules.xml"),
            "keymap": os.path.join(self.workspaceDir, "Settings", "keymap.xml")
            }

    def loadUseData(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument()
        try:
            file = open(self.appPathDict["usedata"], "r")
            dom_document.setContent(file.read())
            file.close()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))
            return

        elements = dom_document.documentElement()
        node = elements.firstChild()

        settingsList = []
        while node.isNull() is False:
            property = node.toElement()
            sub_node = property.firstChild()
            while sub_node.isNull() is False:
                sub_prop = sub_node.toElement()
                if node.nodeName() == "openedprojects":
                    path = sub_prop.text()
                    if os.path.exists(path):
                        self.OPENED_PROJECTS.append(path)
                elif node.nodeName() == "settings":
                    settingsList.append((tuple(sub_prop.text().split('=', 1))))
                sub_node = sub_node.nextSibling()
            node = node.nextSibling()

        self.SETTINGS.update(dict(settingsList))
        # for compatibility with older versions of PyCoder
        settingsKeys = self.SETTINGS.keys()
        if "MarkOperationalLines" not in settingsKeys:
            self.SETTINGS["MarkOperationalLines"] = "False"

        if "UI" not in settingsKeys:
            self.SETTINGS["UI"] = "Custom"

        self.loadKeymap()
        self.loadModulesForCompletion()

    def saveModulesForCompletion(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument("modules")

        modules = dom_document.createElement("modules")
        dom_document.appendChild(modules)

        for i, v in self.libraryDict.items():
            tag = dom_document.createElement(i)
            modules.appendChild(tag)
            tag.setAttribute("use", str(v[1]))

            for subModule in v[0]:
                item = dom_document.createElement("item")
                tag.appendChild(item)

                t = dom_document.createTextNode(subModule)
                item.appendChild(t)

        try:
            file = open(self.appPathDict["modules"], "w")
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(dom_document.toString())
            file.close()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))

    def loadModulesForCompletion(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument()
        try:
            file = open(self.appPathDict["modules"], "r")
            dom_document.setContent(file.read())
            file.close()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))
            return

        element = dom_document.documentElement()
        node = element.firstChild()

        self.libraryDict = {}
        while node.isNull() is False:
            property = node.toElement()
            sub_node = property.firstChild()

            moduleName = node.nodeName()
            use = property.attribute('use')

            itemList = []
            while sub_node.isNull() is False:
                sub_prop = sub_node.toElement()
                itemList.append(sub_prop.text())

                sub_node = sub_node.nextSibling()
            self.libraryDict[moduleName] = [itemList, use]
            node = node.nextSibling()

    def saveUseData(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument("usedata")

        usedata = dom_document.createElement("usedata")
        dom_document.appendChild(usedata)

        root = dom_document.createElement("openedprojects")
        usedata.appendChild(root)

        for i in self.OPENED_PROJECTS:
            tag = dom_document.createElement("project")
            root.appendChild(tag)

            t = dom_document.createTextNode(i)
            tag.appendChild(t)

        root = dom_document.createElement("settings")
        usedata.appendChild(root)

        s = 0
        for key, value in self.SETTINGS.items():
            if key == "InstalledInterpreters":
                continue
            tag = dom_document.createElement("key")
            root.appendChild(tag)

            t = dom_document.createTextNode(key + '=' + value)
            tag.appendChild(t)
            s += 1

        usedata = dom_document.createElement("usedata")
        dom_document.appendChild(usedata)

        try:    
            file = open(self.appPathDict["usedata"], "w")
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(dom_document.toString())
            file.close()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))
            return

        self.settings["running"] = 'False'
        self.saveSettings()
        self.saveModulesForCompletion()

    def loadKeymap(self):
        if self.settings["firstRun"] == "True":
            self.CUSTOM_SHORTCUTS = self.DEFAULT_SHORTCUTS
            return
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument()
        try:
            file = open(self.appPathDict["keymap"], "r")
            x = dom_document.setContent(file.read())
            file.close()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))
            return

        elements = dom_document.documentElement()
        node = elements.firstChild()
        while node.isNull() is False:
            property = node.toElement()
            sub_node = property.firstChild()
            group = node.nodeName()
            while sub_node.isNull() is False:
                sub_prop = sub_node.toElement()
                tag = sub_prop.toElement()
                name = tag.tagName()
                shortcut = tag.attribute("shortcut")
                if group == "Editor":
                    keyValue = int(tag.attribute("value"))
                    self.CUSTOM_SHORTCUTS[
                        group][name] = [shortcut, keyValue]
                else:
                    self.CUSTOM_SHORTCUTS[
                        group][name] = shortcut

                sub_node = sub_node.nextSibling()

            node = node.nextSibling()

    def getLastOpenedDir(self):
        if os.path.exists(self.SETTINGS["LastOpenedPath"]):
            pass
        else:
            self.SETTINGS["LastOpenedPath"] = QtCore.QDir().homePath()
        return self.SETTINGS["LastOpenedPath"]

    def saveLastOpenedDir(self, path):
        if self.SETTINGS["LastOpenedPath"] == path:
            pass
        else:
            self.SETTINGS["LastOpenedPath"] = path

    def saveSettings(self):

        config_path = os.path.expanduser("~/.config/pycoder")
        config_file = "settings.ini"
        settings_file_path = os.path.join(config_path, config_file)

        if not os.path.exists(settings_file_path):
            print(f"Copying {config_file} from current directory to {settings_file_path}")
            self.copySettingsFromCurrentDirectory(settings_file_path)

        file = open(settings_file_path, "w")
        for key, value in self.settings.items():
            file.write('\n' + key + '=' + value)
        file.close()

    def readFile(self, fileName):
        file = open(fileName, 'rb')
        bb = file.read()
        file.close()
        encoding = textEncoding(bb)

        file = open(fileName, 'r')
        text = file.read()
        file.close()

        ending = lineEnding(text)

        return text, encoding, ending

    def getPythonExecutables(self):
        pythonExecutables = FindInstalledPython()
        #print(str(pythonExecutables))
        interpreters = pythonExecutables.python_executables()

        return interpreters
