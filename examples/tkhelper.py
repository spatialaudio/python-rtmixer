"""Key event debouncer for tkinter."""


class TkKeyEventDebouncer(object):
    """Swallow repeated keyboard events if key is pressed and held.

    See https://gist.github.com/vtsatskin/8e3c0c636339b2228138

    """

    _deferred_key_release = None

    def __init__(self, root=None, on_key_press=None, on_key_release=None):
        if root is None:
            root = self
        if on_key_press is not None:
            self.on_key_press = on_key_press
        if on_key_release is not None:
            self.on_key_release = on_key_release
        self.root = root
        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<KeyRelease>', self._on_key_release)

    def _on_key_press(self, event):
        if self._deferred_key_release:
            self.root.after_cancel(self._deferred_key_release)
            self._deferred_key_release = None
        else:
            self.on_key_press(event)

    def _on_key_release(self, event):
        self._deferred_key_release = self.root.after_idle(
            self._on_key_release2, event)

    def _on_key_release2(self, event):
        self._deferred_key_release = None
        self.on_key_release(event)
