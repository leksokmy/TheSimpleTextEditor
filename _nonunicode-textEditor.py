import sys, os                             s
from tkinter import *                             
from tkinter.filedialog   import Open, SaveAs
from tkinter.messagebox   import showinfo, showerror, askyesno
from tkinter.simpledialog import askstring, askinteger
from tkinter.colorchooser import askcolor
from PP4E.Gui.Tools.guimaker import *        

try:
    import textConfig                        
    configs = textConfig.__dict__           
except:
    configs = {}

START     = '1.0'                       
SEL_FIRST = SEL + '.first'                 
SEL_LAST  = SEL + '.last'               

FontScale = 0                              
if sys.platform[:3] != 'win':             
    FontScale = 3

class TextEditor:                 
    startfiledir = '.'   
    editwindows = []     

    ftypes = [('All files',     '*'),             
              ('Text files',   '.txt'),             
              ('Python files', '.py')]                
    colors = [{'fg':'black',      'bg':'white'},      
              {'fg':'yellow',     'bg':'black'},    
              {'fg':'white',      'bg':'blue'},     
              {'fg':'black',      'bg':'beige'},    
              {'fg':'yellow',     'bg':'purple'},
              {'fg':'black',      'bg':'brown'},
              {'fg':'lightgreen', 'bg':'darkgreen'},
              {'fg':'darkblue',   'bg':'orange'},
              {'fg':'orange',     'bg':'darkblue'}]

    fonts  = [('courier',    9+FontScale, 'normal'),  
              ('courier',   12+FontScale, 'normal'),
              ('courier',   10+FontScale, 'bold'),    
              ('courier',   10+FontScale, 'italic'),  
              ('times',     10+FontScale, 'normal'), 
              ('helvetica', 10+FontScale, 'normal'),
              ('ariel',     10+FontScale, 'normal'),
              ('system',    10+FontScale, 'normal'),
              ('courier',   20+FontScale, 'normal')]

    def __init__(self, loadFirst=''):
        if not isinstance(self, GuiMaker):
            raise TypeError('TextEditor needs a GuiMaker mixin')
        self.setFileName(None)
        self.lastfind   = None
        self.openDialog = None
        self.saveDialog = None
        self.text.focus()                        
        if loadFirst:
            self.update()                    
            self.onOpen(loadFirst)

    def start(self):                            
        self.menuBar = [                           
            ('File', 0,                             
                 [('Open...',    0, self.onOpen),  
                  ('Save',       0, self.onSave),  
                  ('Save As...', 5, self.onSaveAs),
                  ('New',        0, self.onNew),
                  'separator',
                  ('Quit...',    0, self.onQuit)]
            ),
            ('Edit', 0,
                 [('Undo',       0, self.onUndo),
                  ('Redo',       0, self.onRedo),
                  'separator',
                  ('Cut',        0, self.onCut),
                  ('Copy',       1, self.onCopy),
                  ('Paste',      0, self.onPaste),
                  'separator',
                  ('Delete',     0, self.onDelete),
                  ('Select All', 0, self.onSelectAll)]
            ),
            ('Search', 0,
                 [('Goto...',    0, self.onGoto),
                  ('Find...',    0, self.onFind),
                  ('Refind',     0, self.onRefind),
                  ('Change...',  0, self.onChange),
                  ('Grep...',    3, self.onGrep)]
            ),
            ('Tools', 0,
                 [('Pick Font...', 6, self.onPickFont),
                  ('Font List',    0, self.onFontList),
                  'separator',
                  ('Pick Bg...',   3, self.onPickBg),
                  ('Pick Fg...',   0, self.onPickFg),
                  ('Color List',   0, self.onColorList),
                  'separator',
                  ('Info...',      0, self.onInfo),
                  ('Clone',        1, self.onClone),
                  ('Run Code',     0, self.onRunCode)]
            )]
        self.toolBar = [
            ('Save',  self.onSave,   {'side': LEFT}),
            ('Cut',   self.onCut,    {'side': LEFT}),
            ('Copy',  self.onCopy,   {'side': LEFT}),
            ('Paste', self.onPaste,  {'side': LEFT}),
            ('Find',  self.onRefind, {'side': LEFT}),
            ('Help',  self.help,     {'side': RIGHT}),
            ('Quit',  self.onQuit,   {'side': RIGHT})]

    def makeWidgets(self):                         
        name = Label(self, bg='black', fg='white')
        name.pack(side=TOP, fill=X)                
                                                  
        vbar  = Scrollbar(self)
        hbar  = Scrollbar(self, orient='horizontal')
        text  = Text(self, padx=5, wrap='none')        
        text.config(undo=1, autoseparators=1)         

        vbar.pack(side=RIGHT,  fill=Y)
        hbar.pack(side=BOTTOM, fill=X)              
        text.pack(side=TOP,    fill=BOTH, expand=YES) 

        text.config(yscrollcommand=vbar.set)    
        text.config(xscrollcommand=hbar.set)
        vbar.config(command=text.yview)        
        hbar.config(command=text.xview)        
        startfont = configs.get('font', self.fonts[0])
        startbg   = configs.get('bg',   self.colors[0]['bg'])
        startfg   = configs.get('fg',   self.colors[0]['fg'])
        text.config(font=startfont, bg=startbg, fg=startfg)
        if 'height' in configs: text.config(height=configs['height'])
        if 'width'  in configs: text.config(width =configs['width'])
        self.text = text
        self.filelabel = name

    def my_askopenfilename(self):   
        if not self.openDialog:
           self.openDialog = Open(initialdir=self.startfiledir,
                                  filetypes=self.ftypes)
        return self.openDialog.show()

    def my_asksaveasfilename(self):    
        if not self.saveDialog:
           self.saveDialog = SaveAs(initialdir=self.startfiledir,
                                    filetypes=self.ftypes)
        return self.saveDialog.show()

    def onOpen(self, loadFirst=''):
        doit = (not self.text_edit_modified() or   
                askyesno('SimpleEditor', 'Text has changed: discard changes?'))
        if doit:
            file = loadFirst or self.my_askopenfilename()
            if file:
                try:
                    text = open(file, 'r').read()
                except:
                    showerror('SimpleEditor', 'Could not open file ' + file)
                else:
                    self.setAllText(text)
                    self.setFileName(file)
                    self.text.edit_reset()          
                    self.text.edit_modified(0)      

    def onSave(self):
        self.onSaveAs(self.currfile)  # may be None

    def onSaveAs(self, forcefile=None):
        file = forcefile or self.my_asksaveasfilename()
        if file:
            text = self.getAllText()
            try:
                open(file, 'w').write(text)
            except:
                showerror('SimpleEditor', 'Could not write file ' + file)
            else:
                self.setFileName(file)            
                self.text.edit_modified(0)        
                                                   
    def onNew(self):
        doit = (not self.text_edit_modified() or  
                askyesno('SimpleEditor', 'Text has changed: discard changes?'))
        if doit:
            self.setFileName(None)
            self.clearAllText()
            self.text.edit_reset()                
            self.text.edit_modified(0)            

    def onQuit(self):
        assert False, 'onQuit must be defined in window-specific sublass' 

    def text_edit_modified(self):
        return self.text.edit_modified()


    def onUndo(self):                          
        try:                                  
            self.text.edit_undo()              
        except TclError:                      
            showinfo('SimpleEditor', 'Nothing to undo')

    def onRedo(self):                   
        try:
            self.text.edit_redo()
        except TclError:
            showinfo('SimpleEditor', 'Nothing to redo')

    def onCopy(self):                           # get text selected by mouse, etc.
        if not self.text.tag_ranges(SEL):       # save in cross-app clipboard
            showerror('SimpleEditor', 'No text selected')
        else:
            text = self.text.get(SEL_FIRST, SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(text)

    def onDelete(self):                         # delete selected text, no save
        if not self.text.tag_ranges(SEL):
            showerror('SimpleEditor', 'No text selected')
        else:
            self.text.delete(SEL_FIRST, SEL_LAST)

    def onCut(self):
        if not self.text.tag_ranges(SEL):
            showerror('SimpleEditor', 'No text selected')
        else:
            self.onCopy()                       # save and delete selected text
            self.onDelete()

    def onPaste(self):
        try:
            text = self.selection_get(selection='CLIPBOARD')
        except TclError:
            showerror('SimpleEditor', 'Nothing to paste')
            return
        self.text.insert(INSERT, text)          # add at current insert cursor
        self.text.tag_remove(SEL, '1.0', END)
        self.text.tag_add(SEL, INSERT+'-%dc' % len(text), INSERT)
        self.text.see(INSERT)                   # select it, so it can be cut

    def onSelectAll(self):
        self.text.tag_add(SEL, '1.0', END+'-1c')   # select entire text
        self.text.mark_set(INSERT, '1.0')          # move insert point to top
        self.text.see(INSERT)                      # scroll to top
        
    def onGoto(self, forceline=None):
        line = forceline or askinteger('SimpleEditor', 'Enter line number')
        self.text.update()
        self.text.focus()
        if line is not None:
            maxindex = self.text.index(END+'-1c')
            maxline  = int(maxindex.split('.')[0])
            if line > 0 and line <= maxline:
                self.text.mark_set(INSERT, '%d.0' % line)   
                self.text.tag_remove(SEL, '1.0', END)          # delete selects
                self.text.tag_add(SEL, INSERT, 'insert + 1l')  # select line
                self.text.see(INSERT)                          # scroll to line
            else:
                showerror('SimpleEditor', 'Bad line number')

    def onFind(self, lastkey=None):
        key = lastkey or askstring('SimpleEditor', 'Enter search string')
        self.text.update()
        self.text.focus()
        self.lastfind = key
        if key:                                                   
            nocase = configs.get('caseinsens', True)          
            where = self.text.search(key, INSERT, END, nocase=nocase)
            if not where:                                          # don't wrap
                showerror('SimpleEditor', 'String not found')
            else:
                pastkey = where + '+%dc' % len(key)           # index past key
                self.text.tag_remove(SEL, '1.0', END)         # remove any sel
                self.text.tag_add(SEL, where, pastkey)        # select key
                self.text.mark_set(INSERT, pastkey)           # for next find
                self.text.see(where)                          # scroll display

    def onRefind(self):
        self.onFind(self.lastfind)

    def onChange(self):
        new = Toplevel(self)
        new.title('SimpleEditor - change')
        Label(new, text='Find text?', relief=RIDGE, width=15).grid(row=0, column=0)
        Label(new, text='Change to?', relief=RIDGE, width=15).grid(row=1, column=0)
        entry1 = Entry(new)
        entry2 = Entry(new)
        entry1.grid(row=0, column=1, sticky=EW)
        entry2.grid(row=1, column=1, sticky=EW)

        def onFind():                         # use my entry in enclosing scope   
            self.onFind(entry1.get())         # runs normal find dialog callback

        def onApply():
            self.onDoChange(entry1.get(), entry2.get())

        Button(new, text='Find',  command=onFind ).grid(row=0, column=2, sticky=EW)
        Button(new, text='Apply', command=onApply).grid(row=1, column=2, sticky=EW)
        new.columnconfigure(1, weight=1)      # expandable entries

    def onDoChange(self, findtext, changeto):
        # on Apply in change dialog: change and refind
        if self.text.tag_ranges(SEL):                      # must find first
            self.text.delete(SEL_FIRST, SEL_LAST)          
            self.text.insert(INSERT, changeto)             # deletes if empty
            self.text.see(INSERT)
            self.onFind(findtext)                          # goto next appear
            self.text.update()                             # force refresh

    def onGrep(self):
        from PP4E.Gui.ShellGui.formrows import makeFormRow
        popup = Toplevel()
        popup.title('SimpleEditor - grep')
        var1 = makeFormRow(popup, label='Directory root',   width=18, browse=False)
        var2 = makeFormRow(popup, label='Filename pattern', width=18, browse=False)
        var3 = makeFormRow(popup, label='Search string',    width=18, browse=False)
        var1.set('.')      # current dir
        var2.set('*.py')   # initial values
        Button(popup, text='Go',
           command=lambda: self.onDoGrep(var1.get(), var2.get(), var3.get())).pack()

    def onDoGrep(self, dirname, filenamepatt, grepkey):
        import threading, queue
        mypopup = Tk()
        mypopup.title('SimpleEditor - grepping')
        status = Label(mypopup, text='Grep thread searching for: %r...' % grepkey)
        status.pack(padx=20, pady=20)
        mypopup.protocol('WM_DELETE_WINDOW', lambda: None)  # ignore X close
        myqueue = queue.Queue()
        threadargs = (filenamepatt, dirname, grepkey, myqueue)
        threading.Thread(target=self.grepThreadProducer, args=threadargs).start()
        self.grepThreadConsumer(grepkey, myqueue, mypopup)

    def grepThreadProducer(self, filenamepatt, dirname, grepkey, myqueue):
        from PP4E.Tools.find import find
        matches = []
        for filepath in find(pattern=filenamepatt, startdir=dirname):
            try:
                for (linenum, linestr) in enumerate(open(filepath)):
                    if grepkey in linestr:
                        message = '%s@%d  [%s]' % (filepath, linenum + 1, linestr)
                        matches.append(message)
            except UnicodeDecodeError:
                print('Unicode error in:', filepath)
        myqueue.put(matches)

    def grepThreadConsumer(self, grepkey, myqueue, mypopup):
        import queue
        try:
            matches = myqueue.get(block=False)
        except queue.Empty:
            self.after(250, self.grepThreadConsumer, grepkey, myqueue, mypopup)
        else:
            mypopup.destroy()     # close status
            self.update()         # erase it now
            if not matches:
                showinfo('SimpleEditor', 'Grep found no matches for: %r' % grepkey)
            else:
                self.grepMatchesList(matches, grepkey)

    def grepMatchesList(self, matches, grepkey):
        # populate list after successful matches
        from PP4E.Gui.Tour.scrolledlist import ScrolledList
        print('Matches for %s: %s' % (grepkey, len(matches)))

        # catch list double-click
        class ScrolledFilenames(ScrolledList):
            def runCommand(self, selection):  
                file, line = selection.split('  [', 1)[0].split('@')
                editor = TextEditorMainPopup(loadFirst=file, winTitle=' grep match')
                editor.onGoto(int(line))
                editor.text.focus_force()   

        popup = Tk()
        popup.title('SimpleEditor - grep matches: %r' % grepkey)
        ScrolledFilenames(parent=popup, options=matches)

    def onFontList(self):
        self.fonts.append(self.fonts[0])           # pick next font in list
        del self.fonts[0]                          # resizes the text area
        self.text.config(font=self.fonts[0])

    def onColorList(self):
        self.colors.append(self.colors[0])         # pick next color in list
        del self.colors[0]                         # move current to end
        self.text.config(fg=self.colors[0]['fg'], bg=self.colors[0]['bg'])

    def onPickFg(self):
        self.pickColor('fg')                       # added on 10/02/00

    def onPickBg(self):                            # select arbitrary color
        self.pickColor('bg')                       # in standard color dialog

    def pickColor(self, part):                     # this is too easy
        (triple, hexstr) = askcolor()
        if hexstr:
            self.text.config(**{part: hexstr})

    def onInfo(self):
        text  = self.getAllText()                  # added on 5/3/00 in 15 mins
        bytes = len(text)                          # words uses a simple guess:
        lines = len(text.split('\n'))              # any separated by whitespace
        words = len(text.split())                  # 3.x: bytes is really chars
        index = self.text.index(INSERT)            # str is unicode code points
        where = tuple(index.split('.'))
        showinfo('SimpleEditor Information',
                 'Current location:\n\n' +
                 'line:\t%s\ncolumn:\t%s\n\n' % where +
                 'File text statistics:\n\n' +
                 'chars:\t%d\nlines:\t%d\nwords:\t%d\n' % (bytes, lines, words))

    def onClone(self):                  
        """
        open a new edit window without changing one already open
        inherits quit and other behavior of window that it clones
        """
        new = Toplevel()                # a new edit window in same process
        myclass = self.__class__        # instance's (lowest) class object
        myclass(new)                    # attach/run instance of my class

    def onRunCode(self, parallelmode=True):
        def askcmdargs():
            return askstring('SimpleEditor', 'Commandline arguments?') or ''

        from PP4E.launchmodes import System, Start, StartArgs, Fork
        filemode = False
        thefile  = str(self.getFileName())
        if os.path.exists(thefile):
            filemode = askyesno('SimpleEditor', 'Run from file?')
        if not filemode:                                    # run text string
            cmdargs   = askcmdargs()
            namespace = {'__name__': '__main__'}            # run as top-level
            sys.argv  = [thefile] + cmdargs.split()         # could use threads
            exec(self.getAllText() + '\n', namespace)       # exceptions ignored
        elif self.text_edit_modified():                 
            showerror('SimpleEditor', 'Text changed: save before run')
        else:
            cmdargs = askcmdargs()
            mycwd   = os.getcwd()                           # cwd may be root
            dirname, filename = os.path.split(thefile)      # get dir, base
            os.chdir(dirname or mycwd)                      # cd for filenames
            thecmd  = filename + ' ' + cmdargs              
            if not parallelmode:                            # run as file
                System(thecmd, thecmd)()                    # block editor
            else:
                if sys.platform[:3] == 'win':               # spawn in parallel
                    run = StartArgs if cmdargs else Start
                    run(thecmd, thecmd)()                   # or always Spawn
                else:
                    Fork(thecmd, thecmd)()                  # spawn in parallel
            os.chdir(mycwd)                                 # go back to my dir

    def onPickFont(self):
        from PP4E.Gui.ShellGui.formrows import makeFormRow
        popup = Toplevel(self)
        popup.title('SimpleEditor - font')
        var1 = makeFormRow(popup, label='Family', browse=False)
        var2 = makeFormRow(popup, label='Size',   browse=False)
        var3 = makeFormRow(popup, label='Style',  browse=False)
        var1.set('courier')
        var2.set('12')              # suggested vals
        var3.set('bold italic')     # see pick list for valid inputs
        Button(popup, text='Apply', command=
               lambda: self.onDoFont(var1.get(), var2.get(), var3.get())).pack()

    def onDoFont(self, family, size, style):
        try:  
            self.text.config(font=(family, int(size), style))
        except:
            showerror('SimpleEditor', 'Bad font specification')

    def isEmpty(self):
        return not self.getAllText()

    def getAllText(self):
        return self.text.get('1.0', END+'-1c')  # extract text as a string
    def setAllText(self, text):
        self.text.delete('1.0', END)            # store text string in widget
        self.text.insert(END, text)             # or '1.0'
        self.text.mark_set(INSERT, '1.0')       # move insert point to top
        self.text.see(INSERT)                   # scroll to top, insert set
    def clearAllText(self):
        self.text.delete('1.0', END)            # clear text in widget

    def getFileName(self):
        return self.currfile
    def setFileName(self, name):                # also: onGoto(linenum)
        self.currfile = name  # for save
        self.filelabel.config(text=str(name))

    def setBg(self, color):
        self.text.config(bg=color)              # to set manually from code
    def setFg(self, color):
        self.text.config(fg=color)              # 'black', hexstring
    def setFont(self, font):
        self.text.config(font=font)             # ('family', size, 'style')

    def setHeight(self, lines):                 # default = 24h x 80w
        self.text.config(height=lines)          # may also be from textCongif.py
    def setWidth(self, chars):
        self.text.config(width=chars)

    def clearModified(self):
        self.text.edit_modified(0)              # clear modified flag
    def isModified(self):
        return self.text_edit_modified()        # changed since last reset?

    def help(self):
        showinfo('About SimpleEditor', helptext % ((Version,)*2))


class TextEditorMain(TextEditor, GuiMakerWindowMenu):
    def __init__(self, parent=None, loadFirst=''):    
        GuiMaker.__init__(self, parent)                 
        TextEditor.__init__(self, loadFirst)             # GuiMaker frame packs self
        self.master.title('SimpleEditor ' + Version)       
        self.master.iconname('SimpleEditor')
        self.master.protocol('WM_DELETE_WINDOW', self.onQuit)
        TextEditor.editwindows.append(self)

    def onQuit(self):                              # on a Quit request in the GUI
        close = not self.text_edit_modified()      # check self, ask?, check others
        if not close:
            close = askyesno('SimpleEditor', 'Text changed: quit and discard changes?')
        if close:
            windows = TextEditor.editwindows
            changed = [w for w in windows if w != self and w.text_edit_modified()]
            if not changed:
                GuiMaker.quit(self) # quit ends entire app regardless of widget type
            else:
                numchange = len(changed)
                verify = '%s other edit window%s changed: quit and discard anyhow?'
                verify = verify % (numchange, 's' if numchange > 1 else '')
                if askyesno('SimpleEditor', verify):
                    GuiMaker.quit(self)

class TextEditorMainPopup(TextEditor, GuiMakerWindowMenu):
    def __init__(self, parent=None, loadFirst='', winTitle=''):
        self.popup = Toplevel(parent)                  
        GuiMaker.__init__(self, self.popup)             # use main window menus
        TextEditor.__init__(self, loadFirst)            # a frame in a new popup
        assert self.master == self.popup
        self.popup.title('SimpleEditor ' + Version + winTitle)
        self.popup.iconname('SimpleEditor')
        self.popup.protocol('WM_DELETE_WINDOW', self.onQuit)
        TextEditor.editwindows.append(self)

    def onQuit(self):
        close = not self.text_edit_modified()
        if not close:
            close = askyesno('SimpleEditor', 'Text changed: quit and discard changes?')
        if close: 
            self.popup.destroy()                       # kill this window only
            TextEditor.editwindows.remove(self)        # (plus any child windows)

#
# when editor embedded in another window
#

class TextEditorComponent(TextEditor, GuiMakerFrameMenu):
    def __init__(self, parent=None, loadFirst=''):     # use Frame-based menus
        GuiMaker.__init__(self, parent)                # all menus, buttons on
        TextEditor.__init__(self, loadFirst)           # GuiMaker must init 1st

    def onQuit(self):
        close = not self.text_edit_modified()
        if not close:
            close = askyesno('SimpleEditor', 'Text changed: quit and discard changes?')
        if close:
            self.destroy()   # erase self Frame but do not quit enclosing app

class TextEditorComponentMinimal(TextEditor, GuiMakerFrameMenu):
    def __init__(self, parent=None, loadFirst='', deleteFile=True):
        self.deleteFile = deleteFile
        GuiMaker.__init__(self, parent)                # GuiMaker frame packs self
        TextEditor.__init__(self, loadFirst)           # TextEditor adds middle

    def start(self):
        TextEditor.start(self)                         # GuiMaker start call
        for i in range(len(self.toolBar)):             # delete quit in toolbar
            if self.toolBar[i][0] == 'Quit':           # delete file menu items,
                del self.toolBar[i]                    # or just disable file
                break
        if self.deleteFile:
            for i in range(len(self.menuBar)):
                if self.menuBar[i][0] == 'File':
                    del self.menuBar[i]
                    break
        else:
            for (name, key, items) in self.menuBar:
                if name == 'File':
                    items.append([1,2,3,4,6])

def testPopup():
    root = Tk()
    TextEditorMainPopup(root)
    TextEditorMainPopup(root)
    Button(root, text='More', command=TextEditorMainPopup).pack(fill=X)
    Button(root, text='Quit', command=root.quit).pack(fill=X)
    root.mainloop()

def main():                                           # may be typed or clicked
    try:                                              # or associated on Windows
        fname = sys.argv[1]                           # arg = optional filename
    except IndexError:                                # build in default Tk root
        fname = None
    TextEditorMain(loadFirst=fname).pack(expand=YES, fill=BOTH)
    mainloop()

if __name__ == '__main__':                            # when run as a script
    #testPopup()
    main()                                            # run .pyw for no DOS box
