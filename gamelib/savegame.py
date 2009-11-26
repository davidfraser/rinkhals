"""Utilities and widgets for saving and restoring games."""

import xmlrpclib
import os
import StringIO
import base64
import zlib

from pgu import gui
import pygame

import config
import version

def read_savegame(fullpath):
    """Open a save game file."""
    try:
        xml = zlib.decompress(open(fullpath, "rb").read())
        params, methodname = xmlrpclib.loads(xml)
        if methodname != "foxassault":
            raise SaveGameError("File does not appear to be a "
                "Fox Assault save game.")
        save_version = params[0]
        if save_version != version.SAVE_GAME_VERSION:
            raise SaveGameError("Incompatible save game version.")

        data = params[1]

        try:
            snapshot = decode_snapshot(params[2])
        except Exception, e:
            snapshot = None

    except Exception, e:
        raise SaveGameError("Failed to load game: %s" % (e,))

    return data, snapshot

def write_savegame(fullpath, data, snapshot):
    """Write a save game file."""
    try:
        snapshot_data = encode_snapshot(snapshot)
        params = (version.SAVE_GAME_VERSION, data, snapshot_data)
        xml = xmlrpclib.dumps(params, "foxassault")
        open(fullpath, "wb").write(zlib.compress(xml))
    except Exception, e:
        raise SaveGameError("Failed to save game: %s" % (e,))

def encode_snapshot(snapshot):
    """Encode a snapshot."""
    snapshot_file = StringIO.StringIO()
    pygame.image.save(snapshot, snapshot_file)
    data = snapshot_file.getvalue()
    data = base64.standard_b64encode(data)
    return data

def decode_snapshot(data):
    """Decode a snapshot."""
    data = base64.standard_b64decode(data)
    snapshot_file = StringIO.StringIO(data)
    snapshot = pygame.image.load(snapshot_file, "snapshot.tga")
    return snapshot


class SaveGameError(Exception):
    pass


class BaseSaveRestoreDialog(gui.Dialog):
    """Save game dialog."""

    def __init__(self, title_txt, button_txt, allow_new, cls="dialog"):
        self.value = None
        self.save_folder = config.config.save_folder

        self.save_games = {}
        self._populate_save_games()

        if allow_new:
            self.name_input = gui.Input()
        else:
            self.name_input = None

        td_style = {
            'padding_left': 4,
            'padding_right': 4,
            'padding_top': 2,
            'padding_bottom': 2,
        }

        self.save_list = gui.List(width=350, height=250)
        games = self.save_games.keys()
        games.sort()
        for name in games:
            self.save_list.add(name, value=name)
        self.save_list.set_vertical_scroll(0)
        self.save_list.connect(gui.CHANGE, self._save_list_change)

        self.image_container = gui.Container()

        button_ok = gui.Button(button_txt)
        button_ok.connect(gui.CLICK, self._click_ok)

        button_cancel = gui.Button("Cancel")
        button_cancel.connect(gui.CLICK, self._click_cancel)

        body = gui.Table()
        body.tr()
        body.td(self.save_list, style=td_style, colspan=2)
        body.td(self.image_container, style=td_style, colspan=2)
        body.tr()
        if self.name_input:
            body.td(gui.Label("Save as:"), style=td_style, align=1)
            body.td(self.name_input, style=td_style)
        else:
            body.td(gui.Spacer(0, 0), style=td_style, colspan=2)
        body.td(button_ok, style=td_style, align=1)
        body.td(button_cancel, style=td_style, align=1)

        title = gui.Label(title_txt, cls=cls + ".title.label")
        gui.Dialog.__init__(self, title, body)

    def get_fullpath(self):
        """Return the fullpath of the select save game file or None."""
        if self.value is None:
            return None
        return os.path.join(self.save_folder, self.value + ".xml")

    def _populate_save_games(self):
        """Read list of save games."""
        for filename in os.listdir(self.save_folder):
            fullpath = os.path.join(self.save_folder, filename)
            root, ext = os.path.splitext(filename)
            if not os.path.isfile(fullpath):
                continue
            if ext != ".xml":
                continue
            self.save_games[root] = self._create_image_widget(fullpath)

    def _create_image_widget(self, fullpath):
        """Create an image showing the contents of a save game file."""
        try:
            data, screenshot = read_savegame(fullpath)
        except SaveGameError:
            return gui.Label("Bad Save Game")

        if screenshot is None:
            return gui.Label("No screenshot")

        return gui.Image(screenshot)

    def _save_list_change(self):
        if self.name_input:
            self.name_input.value = self.save_list.value

        for w in self.image_container.widgets:
            self.image_container.remove(w)

        image_widget = self.save_games[self.save_list.value]
        self.image_container.add(image_widget, 0, 0)

    def _click_ok(self):
        if self.name_input:
            self.value = self.name_input.value
        else:
            self.value = self.save_list.value
        if self.value:
            self.send(gui.CHANGE)
            self.close()

    def _click_cancel(self):
        self.value = None
        self.send(gui.CHANGE)
        self.close()


class SaveDialog(BaseSaveRestoreDialog):
    """Save game dialog."""

    def __init__(self, gameboard):
        BaseSaveRestoreDialog.__init__(self, "Save Game ...", "Save", allow_new=True)
        self.connect(gui.CHANGE, self._save, gameboard)

    def _save(self, gameboard):
        filename = self.get_fullpath()
        if filename is None:
            return

        data = gameboard.save_game()
        snapshot = gameboard.snapshot()

        try:
            write_savegame(filename, data, snapshot)
        except Exception, e:
            print "Failed to save game: %s" % (e,)


class RestoreDialog(BaseSaveRestoreDialog):
    """Restore game dialog."""

    def __init__(self, gameboard):
        BaseSaveRestoreDialog.__init__(self, "Load Game ...", "Load", allow_new=False)
        self.connect(gui.CHANGE, self._restore, gameboard)

    def _restore(self, gameboard):
        filename = self.get_fullpath()
        if filename is None:
            return

        try:
            data, screenshot = read_savegame(filename)
        except Exception, e:
            print "Failed to load game: %s" % (e,)
            return

        gameboard.restore_game(data)
