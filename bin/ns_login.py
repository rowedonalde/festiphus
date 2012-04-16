#ns_login.py
#Festiphus nameserver login dialog class

"""Prompts user for address of nameserver (if other than default)
and name to use on given nameserver. Checks nameserver to
ensure that the name has not already been taken, too.
"""

from Tkinter import *

class Login_Dialog(Toplevel):


    def __init__(self, parent,
                 title = 'Login to the FesTiPhus Network'):
        
        ##Create a dialog window slaved to the main app window:
        Toplevel.__init__(self, parent)
        
        if title:
            self.title(title)
            
        self.parent = parent
        
        self.result = None
        
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx = 5, pady = 5)
        
        self.buttonbox()
        
        #Prevent entry in the main window:
        self.grab_set()
        
        if not self.initial_focus
