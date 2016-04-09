
import sys, os                                  
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

#Edited 453 - 598 grepThreadConsumer ---- setKnownEncoding




class TextEditor:                        
    startfiledir = '.'                
    editwindows  = []                    

    if __name__ == '__main__':
        from textConfig import (              
            opensAskUser, opensEncoding,
            savesUseKnownEncoding, savesAskUser, savesEncoding)
    else:
        from .textConfig import (              
            opensAskUser, opensEncoding,
            savesUseKnownEncoding, savesAskUser, savesEncoding)

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

    def __init__(self, loadFirst='', loadEncode=''):
        if not isinstance(self, GuiMaker):
            raise TypeError('TextEditor needs a GuiMaker mixin')
        self.setFileName(None)
        self.lastfind   = None
        self.openDialog = None
        self.saveDialog = None
        self.knownEncoding = None                
        self.text.focus()                          
        if loadFirst:
            self.update()                        
            self.onOpen(loadFirst, loadEncode)

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

    def onOpen(self, loadFirst='', loadEncode=''):

        if self.text_edit_modified(): 
            if not askyesno('SimpleEditor', 'Text has changed: discard changes?'):
                return

        file = loadFirst or self.my_askopenfilename()
        if not file: 
            return
        
        if not os.path.isfile(file):
            showerror('SimpleEditor', 'Could not open file ' + file)
            return
        text = None   
        if loadEncode:
            try:
                text = open(file, 'r', encoding=loadEncode).read()
                self.knownEncoding = loadEncode
            except (UnicodeError, LookupError, IOError):    
                pass

        # try user input, prefill with next choice as default
        if text == None and self.opensAskUser:
            self.update()  
            askuser = askstring('SimpleEditor', 'Enter Unicode encoding for open',
                                initialvalue=(self.opensEncoding or 
                                              sys.getdefaultencoding() or ''))
            if askuser:
                try:
                    text = open(file, 'r', encoding=askuser).read()
                    self.knownEncoding = askuser
                except (UnicodeError, LookupError, IOError):
                    pass
        if text == None and self.opensEncoding:
            try:
                text = open(file, 'r', encoding=self.opensEncoding).read()
                self.knownEncoding = self.opensEncoding
            except (UnicodeError, LookupError, IOError):
                pass

        if text == None:
            try:
                text = open(file, 'r', encoding=sys.getdefaultencoding()).read()
                self.knownEncoding = sys.getdefaultencoding()
            except (UnicodeError, LookupError, IOError):
                pass
        if text == None:
            try:
                text = open(file, 'rb').read()         
                text = text.replace(b'\r\n', b'\n')    # for display, saves
                self.knownEncoding = None
            except IOError:
                pass

        if text == None:
            showerror('SimpleEditor', 'Could not decode and open file ' + file)
        else:
            self.setAllText(text)
            self.setFileName(file)
            self.text.edit_reset()            
            self.text.edit_modified(0)       

    def onSave(self):
        self.onSaveAs(self.currfile)  # may be None

    def onSaveAs(self, forcefile=None):

        filename = forcefile or self.my_asksaveasfilename()
        if not filename:
            return

        text = self.getAllText()     
        encpick = None                # even if read/inserted as bytes 

        # try known encoding at latest Open or Save, if any
        if self.knownEncoding and (                                  # enc known?
           (forcefile     and self.savesUseKnownEncoding >= 1) or    # on Save?
           (not forcefile and self.savesUseKnownEncoding >= 2)):     # on SaveAs?
            try:
                text.encode(self.knownEncoding)
                encpick = self.knownEncoding
            except UnicodeError:
                pass

        if not encpick and self.savesAskUser:
            self.update()  # else dialog doesn't appear in rare cases
            askuser = askstring('SimpleEditor', 'Enter Unicode encoding for save',
                                initialvalue=(self.knownEncoding or 
                                              self.savesEncoding or 
                                              sys.getdefaultencoding() or ''))
            if askuser:
                try:
                    text.encode(askuser)
                    encpick = askuser
                except (UnicodeError, LookupError):    # LookupError:  bad name 
                    pass                               
        if not encpick and self.savesEncoding:
            try:
                text.encode(self.savesEncoding)
                encpick = self.savesEncoding
            except (UnicodeError, LookupError):
                pass

        # try platform default (utf8 on windows)
        if not encpick:
            try:
                text.encode(sys.getdefaultencoding())
                encpick = sys.getdefaultencoding()
            except (UnicodeError, LookupError):
                pass
        if not encpick:
            showerror('SimpleEditor', 'Could not encode for file ' + filename)
        else:
            try:
                file = open(filename, 'w', encoding=encpick)
                file.write(text)
                file.close()
            except:
                showerror('SimpleEditor', 'Could not write file ' + filename)
            else:
                self.setFileName(filename)          
                self.text.edit_modified(0)       
                self.knownEncoding = encpick        
                                                    
    def onNew(self):
        if self.text_edit_modified():    
            if not askyesno('SimpleEditor', 'Text has changed: discard changes?'):
                return
        self.setFileName(None)
        self.clearAllText()
        self.text.edit_reset()                
        self.text.edit_modified(0)             
        self.knownEncoding = None              #

    def onQuit(self):
        assert False, 'onQuit must be defined in window-specific sublass' 

    def text_edit_modified(self):
        return self.text.edit_modified()

    def onUndo(self):                         
        try:                                   
            self.text.edit_undo()               # exception if stacks empty
        except TclError:                        # menu tear-offs for quick undo
            showinfo('SimpleEditor', 'Nothing to undo')

    def onRedo(self):                           
        try:
            self.text.edit_redo()
        except TclError:
            showinfo('SimpleEditor', 'Nothing to redo')

    def onCopy(self):                           # get text selected by mouse, etc.
        if not self.text.tag_ranges(SEL):      
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
                self.text.mark_set(INSERT, '%d.0' % line)      # goto line
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
            if not where:                                      
                showerror('SimpleEditor', 'String not found')
            else:
                pastkey = where + '+%dc' % len(key)           
                self.text.tag_remove(SEL, '1.0', END)        
                self.text.tag_add(SEL, where, pastkey)       
                self.text.mark_set(INSERT, pastkey)          
                self.text.see(where)                         

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
        if self.text.tag_ranges(SEL):                     
            self.text.delete(SEL_FIRST, SEL_LAST)          
            self.text.insert(INSERT, changeto)           
            self.text.see(INSERT)
            self.onFind(findtext)                          
            self.text.update()                           

    def onGrep(self):
        from PP4E.Gui.ShellGui.formrows import makeFormRow
        popup = Toplevel()
        popup.title('SimpleEditor - grep')
        var1 = makeFormRow(popup, label='Directory root',   width=18, browse=False)
        var2 = makeFormRow(popup, label='Filename pattern', width=18, browse=False)
        var3 = makeFormRow(popup, label='Search string',    width=18, browse=False)
        var1.set('.')      
        var2.set('*.py')  
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


    def setBg(self, color):
        self.text.config(bg=color)                # to set manually from code
    def setFg(self, color):
        self.text.config(fg=color)                # 'black', hexstring
    def setFont(self, font):
        self.text.config(font=font)               # ('family', size, 'style')

    def setHeight(self, lines):                   # default = 24h x 80w
        self.text.config(height=lines)            # may also be from textCongif.py
    def setWidth(self, chars):
        self.text.config(width=chars)

    def clearModified(self):
        self.text.edit_modified(0)                # clear modified flag
    def isModified(self):
        return self.text_edit_modified()          # changed since last reset?

    def help(self):
        showinfo('About SimpleEditor', helptext % ((Version,)*2))


class TextEditorMain(TextEditor, GuiMakerWindowMenu):
    def __init__(self, parent=None, loadFirst='', loadEncode=''):
        GuiMaker.__init__(self, parent)                  
        TextEditor.__init__(self, loadFirst, loadEncode) 
        self.master.title('SimpleEditor ' + Version)          
        self.master.iconname('SimpleEditor')
        self.master.protocol('WM_DELETE_WINDOW', self.onQuit)
        TextEditor.editwindows.append(self)

    def onQuit(self):                             
        close = not self.text_edit_modified()     
        if not close:
            close = askyesno('SimpleEditor', 'Text changed: quit and discard changes?')
        if close:
            windows = TextEditor.editwindows
            changed = [w for w in windows if w != self and w.text_edit_modified()]
            if not changed:
                GuiMaker.quit(self) 
            else:
                numchange = len(changed)
                verify = '%s other edit window%s changed: quit and discard anyhow?'
                verify = verify % (numchange, 's' if numchange > 1 else '')
                if askyesno('SimpleEditor', verify):
                    GuiMaker.quit(self)

class TextEditorMainPopup(TextEditor, GuiMakerWindowMenu):
    def __init__(self, parent=None, loadFirst='', winTitle='', loadEncode=''):
        # create own window
        self.popup = Toplevel(parent)
        GuiMaker.__init__(self, self.popup)              
        TextEditor.__init__(self, loadFirst, loadEncode)  # a frame in a new popup
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

    def onClone(self): 
        TextEditor.onClone(self, makewindow=False)     # I make my own pop-up

class TextEditorComponent(TextEditor, GuiMakerFrameMenu):
    def __init__(self, parent=None, loadFirst='', loadEncode=''):     
        # use Frame-based menus
        GuiMaker.__init__(self, parent)                   # all menus, buttons on
        TextEditor.__init__(self, loadFirst, loadEncode) 

    def onQuit(self):
        close = not self.text_edit_modified()
        if not close:
            close = askyesno('SimpleEditor', 'Text changed: quit and discard changes?')
        if close:
            self.destroy()   

class TextEditorComponentMinimal(TextEditor, GuiMakerFrameMenu):
    def __init__(self, parent=None, loadFirst='', deleteFile=True, loadEncode=''):
        self.deleteFile = deleteFile
        GuiMaker.__init__(self, parent)                  
        TextEditor.__init__(self, loadFirst, loadEncode) 

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
    try:                                             
        fname = sys.argv[1]                           
    except IndexError:                             
        fname = None
    TextEditorMain(loadFirst=fname).pack(expand=YES, fill=BOTH)  
    mainloop()

if __name__ == '__main__':                            
    main()                                          
