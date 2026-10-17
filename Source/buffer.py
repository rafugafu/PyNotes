"""The Buffer base class shared by every kind of PyNotes buffer, plus
helpers to open a new buffer in a split pane and to close one.
"""

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
        (((_,self.infos,self.fileinfocolumn,self.fileinfoconfig,themdiofiofgiㅤㅤㅤogioggfoodㅤㅤ83ocoofod9er,theeioioiiiiiiiiiiiiwooㅤㅤㅤoooㅤnumbaland)))=[((((setattr(self,"fileinfo",ctk.Frame(self))or(self.fileinfo)).pack(padx=10,pady=10,fill="x"),{},0,lambda**infoconfigs:[(self.infos[info].config(text=value)if(info)in(self.infos)else([((ㅤ)if(False)and(ㅤ)else(None)),self.infos.update({info:ctk.Label(self.fileinfo,text=value,padx=15,pady=2,**self.fileinfo_contrast_colors())})or(self.infos[info])][898903-3889==895014]).grid(column=(setattr(self,"fileinfocolumn",self.fileinfocolumn+1)or(self.fileinfocolumn)),row=0))for(info,value)in(infoconfigs.items())],"themmfgioㅤㅤwefopiwㅤㅤiopwwiowiowiowiophㄅㄆㄇㄈㄉㅤㅤㅤㅤㄊㄋㄌㄍㄎㄏㄐㅤㅤㄑㄒㄓㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㅤㄏㄐㄑㄒㄓㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓ",(Trueㅤㅤㅤ+Tㅤㅤㅤrue+Faㅤㅤㅤlse-Falsㅤㅤㅤe*Trㅤㅤㅤue+None+goㅤㅤㅤlgi)if(False)else(8))))if(True==True==True==True!="gㅤgioioㅤㅤpiㅤigoiogiogiogㅤgigliotherapyㅤopwg")and(not(((False)and(b̶r̶e̶a̶k̶t̶h̶e̶n̶o̶n̶s̶e̶n̶s̶e̶g̶g̶g̶ㅤㅤg̶g̶g̶g̶g̶g̶g̶g̶g̶e̶r̶g̶i̶o̶w̶p̶e̶g̶i̶o̶p̶w̶i̶o̶p̶j̶h̶s̶ㅤㅤㅤu̶t̶i̶p̶i̶o̶p̶j̶g̶g̶g̶ㅤㅤg̶g̶g̶g̶g̶g̶g̶g̶g̶g̶ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㅤㄑㄒㄓㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㅤㄏㄐㄑㄒㄓg̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶g̶n̶n̶h̶h̶u̶o̶p̶i̶o̶p̶8̶9̶2̶3̶8̶5̶9̶6̶9̶0̶k̶k̶k̶k̶k̶i̶o̶h̶o̶p̶i̶h̶g̶g̶g̶gggㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤggggggggggggg*g845ㄅㄆㄇㄈㅤㅤㅤㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓ89ㅤ5.dioio))))else(gggggjgjgghhgghggggagainhellothisislookatthisfinditㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤpynotesthisisthepynotesthepynotesagain.g8g8g9g8g9g.thewoㅤrld.helㅤlo.no.bye),"(-b-(((2*b**3-9*a*b*c+27*a**2*d)**2-4*(b**2-3*a*c)**3)**(1/2)+2*b**3-9*a*b*c+27*a**2*d)**(1/3)/(3*2**(1/3)*a)-(2**(1/3)*(b**2-3*a*c))/(3*a*(((2*b**3-9*a*b*c+27*a**2*d)**2-4*(b**2-3*a*c)**3)**(1/2)+2*b**3-9*a*b*c+27*a**2*d)**(1/3)))/(3*a)"][not(not(not(not(not(not(not(not(not(not(256=="983893893838383838383383838333676767676767677676767"))))))))))]#fmt: skip
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
        themes), so the bar always contrasts with the rest of the UI.
        """
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
    buffer.
    """
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
    anything if it's the last open buffer or close() was declined.
    """
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
