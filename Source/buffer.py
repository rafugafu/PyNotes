import canvastk as ctk
import state


class Buffer(ctk.Frame):
    """Base frame for every kind of PyNotes buffer (editor, terminal, etc).

    Provides the shared file-info bar at the top of a buffer and runs any
    plugin-supplied init functions/code against this class and its instances.
    """

    for code in state.buffer_init_functions:
        try:
            exec(code, vars(state), locals())
        except Exception as error:
            error = str(error)
            state.root.error("Error", f"Error in buffer init functions:\n{error}")

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.active = False
        # this is intentionally evil
        _, self.infos, self.fileinforelief, self.fileinfocolumn, self.fileinfoconfig = (
            (setattr(self, "fileinfo", ctk.Frame(self)) or self.fileinfo).pack(
                padx=10, pady=10, fill="x"
            ),
            {},
            0,
            0,
            lambda relief=None, **infoconfigs: [
                (
                    self.infos[info].config(text=value)
                    if info in self.infos
                    else (
                        self.infos.update(
                            {
                                info: ctk.Label(
                                    self.fileinfo,
                                    text=value,
                                    padx=15,
                                    pady=2,
                                    **self.fileinfo_contrast_colors(),
                                    relief=relief
                                    or {0: "sunken", 1: "raised"}[
                                        setattr(
                                            self,
                                            "fileinforelief",
                                            not self.fileinforelief,
                                        )
                                        or self.fileinforelief
                                    ],
                                )
                            }
                        )
                        or self.infos[info]
                    ).grid(
                        column=(
                            setattr(self, "fileinfocolumn", self.fileinfocolumn + 1)
                            or self.fileinfocolumn
                        ),
                        row=0,
                    )
                )
                for info, value in infoconfigs.items()
            ],
        )
        self.wanttitle = ""
        for code in state.buffer_init_code:
            try:
                exec(code, vars(state), locals())
            except Exception as error:
                error = str(error)
                state.root.error("Error", f"Error in buffer init code:\n{error}")

    @staticmethod
    def fileinfo_contrast_colors():
        """The file-info bar's label colors: the palette opposite to the
        current appearance mode (dark in light themes, light in dark
        themes), so the bar always contrasts with the rest of the UI."""
        palette = (
            ctk.CANVAS_LIGHT_PALETTE
            if ctk.get_appearance_mode() == "dark"
            else ctk.CANVAS_DARK_PALETTE
        )
        return {"bg": palette["surface"], "text_color": palette["text"]}

    def refresh_fileinfo_contrast_colors(self):
        """Recolor the file-info labels after a theme change."""
        for label in self.infos.values():
            label.config(**self.fileinfo_contrast_colors())

    def setwanttitle(self, title):
        """Set this buffer's requested window-title text and refresh it."""
        import window

        self.wanttitle = title
        window.settitle()


def newbuffer(buffer, orient, *args, **kwargs):
    """Instantiate buffer (a Buffer subclass) with the given args/kwargs,
    split the active buffer's pane with it, to its right (horizontal) or
    below it (vertical) per orient, rebalance, and make it the active
    buffer."""
    import pycode
    import window

    newbuff = buffer(state.panes, *args, **kwargs)
    state.all_buffers.append(newbuff)
    pycode.pcrun(state.pycode_keybindings_cdt)
    if not state.panes.panes():
        state.panes.add(newbuff, handle=newbuff.fileinfo)
    else:
        target = state.active if state.active in state.panes.panes() else None
        state.panes.split(
            target or state.panes.panes()[-1], newbuff, orient, handle=newbuff.fileinfo
        )
    state.root.update()
    window.balance(orient)
    state.root.update()
    window.setactive(-1)
    return newbuff


def pcclosebuff(n=None):
    """Close buffer n (the active one if not given), confirming first
    via the buffer's own close() if it has unsaved changes/a running
    process. Removes it from the pane layout (which collapses any split
    left with a single pane) and rebalances. Returns False without closing
    anything if it's the last open buffer or close() was declined."""
    import pycode
    import utils
    import window

    if len(state.all_buffers) == 1:
        utils.show("cannot close only open buffer")
        return False
    if n is None:
        n = state.buffindex
    else:
        n = int(n)
    buffer = state.all_buffers[n]
    was_last_reference = (
        (buffer.view_master is None and not buffer.view_children)
        if hasattr(buffer, "view_master") and hasattr(buffer, "view_children")
        else False
    )
    if not buffer.close():
        return False
    pycode.pcrunhook("before", "close-buffer")
    if buffer in state.panes.panes():
        state.panes.remove(buffer)
        window.balance()
    if hasattr(buffer, "_cancel_all_after_ids"):
        buffer._cancel_all_after_ids()
    if was_last_reference:
        try:
            buffer.observer.stop()
            buffer.observer.join()
        except Exception:
            pass
    buffer.destroy()
    state.all_buffers.remove(buffer)
    if n <= state.buffindex:
        window.setactive(state.buffindex - 1, force=True)
    utils.show("closed buffer")
    pycode.pcrunhook("after", "close-buffer")
    return True
