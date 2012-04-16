#ns_login_simple.py
#Festiphus nameserver login dialog class
#
#Extends tkSimpleDialog.Dialog for layout
#per ex. 10.3 on
#http://www.pythonware.com/library/tkinter/introduction/dialog-windows.htm

"""Prompts user for address of nameserver (if other than default)
and name to use on given nameserver. Checks nameserver to
ensure that the name has not already been taken, too.
"""

from Tkinter import *
import tkSimpleDialog
import tkMessageBox
import httplib

#Nameserver access constants/attributes:
NS_DEFAULT_DOMAIN = 'my.cs.lmu.edu:4000'
NS_REGISTER = '/reg'
ns_domain = StringVar()
ns_domain.set(NS_DEFAULT_DOMAIN)
ns_username = StringVar()
ns_username.set('')

#GUI constants:
NS_DOMAIN_ROW = 0
NS_USERNAME_ROW = 1

class Login_Dialog(tkSimpleDialog.Dialog):

    #Set the title of this Dialog:
    self.title = 'Login to the FesTiPhus Network'
    
    #Build the layout for this dialog:
    def body(self, master):
    
        Label(master, text = 'Nameserver:').grid(row = NS_DOMAIN_ROW)
        Label(master, text = 'Username:').grid(row = NS_USERNAME_ROW)
        
        self.domain_entry = Entry(master, textvariable = ns_domain)
        self.username_entry = Entry(master, textvariable = ns_username)
        
        self.domain_entry.grid(row = NS_DOMAIN_ROW, column = 1)
        self.username_entry.grid(row = NS_USERNAME_ROW, column = 1)
        
        #Set initial focus to username_entry:
        return self.username_entry
        
        
    #Validate domain and username:
    def validate(self):
        #TODO: actually check format of username and domain
        
        #Check to see whether 
    
