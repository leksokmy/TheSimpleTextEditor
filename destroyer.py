
from tkinter import *
from tkinter.messagebox import askyesno

def onDeleteRequest():
    print('Got wm delete')
    root.destroy()                  
def doRootDestroy(event):
    print('Got event <destroy>')   
    if event.widget == text:
        print('for text')
def doTextDestroy(event):
    print('Got text <destroy>')

root = Tk()
text = Text(root, undo=1, autoseparators=1)
text.pack()
root.bind('<Destroy>', doRootDestroy)     
root.protocol('WM_DELETE_WINDOW', onDeleteRequest)
Button(root, text='Destroy', command=root.destroy).pack()
Button(root, text='Quit',    command=root.quit).pack()    
mainloop()
print('After mainloop')  
