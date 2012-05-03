#festiphus.py
#Main script for Festiphus, ported to Tkinter for GUI support

from Tkinter import *
import tkMessageBox
import tkSimpleDialog
import ftplib
from pyftpdlib import ftpserver
from threading import Thread
import os
import httplib

#Server setting constants:
SERVER_IP = ''
SERVER_PORT = 3001

#nameserver setting constants:
NS_DOMAIN = 'my.cs.lmu.edu:4000'
NS_REGISTER = '/reg'
NS_GETIP = '/myip'
NS_GETREMOTE = '/whereis'

#GUI Grid constants:
CLIENT_LABEL_ROW = 0
CLIENT_ROW = 1
SERVER_LABEL_ROW = 2
SERVER_ROW = 3
BROWSER_LABEL_ROW = 4
BROWSER_ROW = 5

#instance for a Festiphus session:
class Festiphus(Frame):
    ###############LOCAL##################
    #Refresh local browser based on current working dir:
    def refresh_local_browser(self):
        #refresh the label above the local browser:
        self.current_local_dir.set("Local:\n" + os.getcwd())
        
        #clear out the current list:
        self.local_browser.delete(0, END)
        
        ##Display the files and dirs in the current dir:
        file_list = os.listdir(os.getcwd())
        
        #if this isn't the root dir, put a dir link to up one level:
        if os.getcwd() != '/':
            self.local_browser.insert(0, '..')
        
        for name in file_list:
            #Add a slash to the end of the name if it's a dir:
            if os.path.isdir(name):
                name += '/'
            #Put name on the file list:    
            self.local_browser.insert(END, name)
    
    #Handles interaction with the local browser.
    #Determines whether the selected item is a file or directory
    #and routes to the correct method.
    def local_handler(self):
        #Get the currently selected item:
        cur_selected_index = self.local_browser.curselection()
        #print "cur_selected:", cur_selected
        cur_selected = self.local_browser.get(cur_selected_index[0])
        
        #If the current item ends in a slash, it's a directory,
        #so change the local working directory and refresh the display:
        if cur_selected[-1] == '/' or cur_selected == '..':
            os.chdir(cur_selected)
            self.refresh_local_browser()
        #Otherwise, it's a file, so upload it if possible:
        else:
            self.current_session.storbinary("STOR " + cur_selected, open(cur_selected))
    
    
    ###############REMOTE#################
    
    
    ###############Client#################
    
    #FTP sessions in this instance of Festiphus
    #At first, I'll support 1, but this should be able to grow
    sessions = []
    
    #The currently active session in the window:
    current_session = None
    
    #Register with the nameserver:
    def register(self):
        #First, check to make sure that the name is available:
        name_is_available = False
        h1 = httplib.HTTPConnection(self.domain)
        h1.request('GET', NS_REGISTER + '/' + self.username)
        res = h1.getresponse()
        res.read()
        if res.status == 200:
            name_is_available = True
        
        while not name_is_available:
            self.username = tkSimpleDialog.askstring('Connect to the FesTiPhus network',
                                                 'Sorry, but that name is taken. Please select Another.')
            h1.request('GET', NS_REGISTER + '/' + self.username)
            res = h1.getresponse()
            res.read()
            if res.status == 200:
                name_is_available = True
        
        
        #when the user has picked a good name, push it:
        
        h1.request('POST', NS_REGISTER + '/' + self.username + '/' + str(SERVER_PORT))
        res = h1.getresponse()
        print res.status
        

    #Initiate an FTP connection:
    def open_connection(self, host, port, name, password):
        new_conn = ftplib.FTP()
        new_conn.connect(host, port)
        new_conn.login(name, password)
        self.sessions.append(new_conn)
        self.refresh_remote_browser(new_conn)
        
        #for right now, the active session is just this one:
        self.current_session = new_conn

    #Use the input to trigger an open_connection:
    def submit_connection(self):
        name = self.name_input.get()
        
        #First, get the user's address and server port:
        h1 = httplib.HTTPConnection(self.domain)
        h1.request('GET', NS_GETREMOTE + '/' + name)
        res = h1.getresponse()
        remote_address = res.read().partition(':')
        host = remote_address[0]
        port = remote_address[2]
    
        #host = self.host_input.get()
        #port = self.port_input.get()
        
        password = self.password_input.get()
        self.open_connection(host, port, name, password)

    #Refresh the remote file browser and the directory name:
    def refresh_remote_browser(self, conn):
        #Set the new current directory:
        self.current_remote_dir.set("Remote:\n" + conn.pwd())
        
        #clear out the current list:
        self.remote_browser.delete(0, END)

        ##display the directory contents:
        #retrieve an array of just the file names:
        simple_file_list = conn.nlst()
        
        ##Determine what is a dir vs. what is a file:
        #Get a more detailed array from which we can determine whether a
        #listing is a file or a directory:
        long_file_list = []
        conn.dir(long_file_list.append)
        
        #if this isn't the root dir, put a dir link to up one level:
        if conn.pwd() != '/':
            self.remote_browser.insert(0, '..')
        
        #List all the files and directories:
        for index, name in enumerate(simple_file_list):
            #If the current name is that of a directory, add a slash:
            if long_file_list[index][0] == 'd':
                name += '/'
            self.remote_browser.insert(END, name)
        
    #Move the working directory to the given dir in the given connection:
    def remote_cd(self, directory, conn):
        #move to the given dir:
        conn.cwd(directory)
        
        #refresh the file browser:
        self.refresh_remote_browser(conn)
    
    #Use the input to change the directory:
    def submit_remote_directory(self):
        #A list of the indices that are currently selected in the file browser:
        cur_selected = self.remote_browser.curselection()
        
        #The relative name of the first selected item:
        target = self.remote_browser.get(cur_selected[0])
        
        #If target ends in a slash, it's a directory:
        if target[-1] == '/' or target == '..':
            #Move to the given dir:
            self.remote_cd(target, self.current_session)
        #Otherwise, it's a file, so download it:
        else:
            #If a file by the name doesn't already exist, open
            #a blank file by the name of the one to be downloaded:
            new_file = open(target, 'w')
            
            self.current_session.retrbinary("RETR " + target, new_file.write)
    
    
    #################Server#################
    #Initializes the server
    #This is going to have to run in a different thread, since the mainloop
    #needs to keep running
    def start_server(self):
        #Set up auths for the server:
        self.authorizer = ftpserver.DummyAuthorizer()
        #Right now, just set up a user with the following vars
        #This user can read and move around--that's pretty much it
        #Set up the handler and provide it with the previous authorizer:
        handler = ftpserver.FTPHandler
        
        ##set to work behind a NAT:
        #Get external address from nameserver:
        #h1 = httplib.HTTPConnection(NS_DOMAIN)
        h1 = httplib.HTTPConnection(self.domain)
        h1.request('GET', NS_GETIP)
        #print self.ns_connection
        #self.ns_connection.request('GET', NS_GETIP)
        res = h1.getresponse()
        #res = self.ns_connection.getresponse()
        #h1.close()
        handler.masquerade_address = res.read()
        print 'Current public IP:', handler.masquerade_address
        #Set Passive data connection port constraints:
        handler.passive_ports = [3000]
        
        handler.authorizer = self.authorizer
        address = (SERVER_IP, SERVER_PORT)
        
        #connect the handler to the address and fire up the server:
        self.ftpd = ftpserver.FTPServer(address, handler)
        self.ftpd.serve_forever()
    
    #Add a new user to this server: 
    def add_user(self):
        #add the user based on the second row of entries:
        new_name = self.new_name_input.get()
        new_pass = self.new_pass_input.get()
        self.authorizer.add_user(new_name, new_pass,
                                 self.app_start_dir+'/ftproot',
                                 perm = 'elrw')
        
        #clear out the boxes:
        self.new_name_input.delete(0, END)
        self.new_pass_input.delete(0, END)
        

    ################GUI######################
    #Build the widgets
    def createWidgets(self):
        
        ##Client Control
        #host entry:
        #self.host_input = Entry(self)
        #self.host_input.grid(column = 0, row = CLIENT_ROW)
        #label:
        #self.host_input_label = Label(self, text = "Host:")
        #self.host_input_label.grid(column = 0, row = CLIENT_LABEL_ROW)
        
        #port entry:
        #self.port_input = Entry(self)
        #self.port_input.grid(column = 1, row = CLIENT_ROW)
        #label:
        #self.port_input_label = Label(self, text = "Port:")
        #self.port_input_label.grid(column = 1, row = CLIENT_LABEL_ROW)

        #name entry:
        self.name_input = Entry(self)
        self.name_input.grid(column = 0, row = CLIENT_ROW)
        #label:
        self.name_input_label = Label(self, text = "Remote User's Name:")
        self.name_input_label.grid(column = 0, row = CLIENT_LABEL_ROW)

        #password entry:
        self.password_input = Entry(self, show = '*')
        self.password_input.grid(column = 1, row = CLIENT_ROW)
        #label:
        self.password_input_label = Label(self, text = "Password:")
        self.password_input_label.grid(column = 1, row = CLIENT_LABEL_ROW)
        
        #connect button:
        self.connect_button = Button(self, text = 'Connect',
                                     command = self.submit_connection)
        self.connect_button.grid(column = 2, row = CLIENT_ROW)
        
        ##Server Control
        #new name entry:
        self.new_name_input = Entry(self)
        self.new_name_input.grid(column = 0, row = SERVER_ROW)
        #label:
        self.new_name_input_label = Label(self, text = "New User Name:")
        self.new_name_input_label.grid(column = 0, row = SERVER_LABEL_ROW)
        
        #new password entry:
        self.new_pass_input = Entry(self)
        self.new_pass_input.grid(column = 1, row = SERVER_ROW)
        #label:
        self.new_pass_input_label = Label(self, text = "New User Password:")
        self.new_pass_input_label.grid(column = 1, row = SERVER_LABEL_ROW)
        
        #add new user button:
        self.new_user_button = Button(self, text = 'Add New User',
                                      command = self.add_user)
        self.new_user_button.grid(column = 2, row = SERVER_ROW)
        
        
        ##local file browser:
        #scrollbar:
        self.local_browser_scrollbar = Scrollbar(self)
        
        #window:
        self.local_browser = Listbox(self,
                                     yscrollcommand = self.local_browser_scrollbar.set)
        self.local_browser.grid(column = 0, row = BROWSER_ROW)
        
        #initialize scrollbar:
        self.local_browser_scrollbar.grid(column = 1, row = BROWSER_ROW,
                                          sticky = N+S+W)
        self.local_browser_scrollbar.config(command = self.local_browser.yview)
        
        #current directory label:
        self.current_local_dir = StringVar() #local_dir_label will follow this
        self.local_dir_label = Label(self, textvariable = self.current_local_dir)
        self.local_dir_label.grid(row = BROWSER_LABEL_ROW, column = 0)
        
        #Enable double-click selection:
        self.local_browser.bind("<Double-1>", 
                                 (lambda event: self.local_handler()))
        

        ##remote file browser:
        #scrollbar:
        self.remote_browser_scrollbar = Scrollbar(self)
        
        #window:
        self.remote_browser = Listbox(self, 
                                      yscrollcommand = self.remote_browser_scrollbar.set)
        self.remote_browser.grid(column = 2, row = BROWSER_ROW)
        
        #initialize scrollbar:
        self.remote_browser_scrollbar.grid(column = 3, row = BROWSER_ROW,
                                           sticky = N+S+W)
        self.remote_browser_scrollbar.config(command = self.remote_browser.yview)
        
        #current directory label:
        self.current_remote_dir = StringVar() #remote_dir_label will follow this
        self.remote_dir_label = Label(self, textvariable = self.current_remote_dir)
        self.remote_dir_label.grid(row = BROWSER_LABEL_ROW, column = 2)
        
        #Enable double-click selection:
        #For some reason this needs to be a lambda per
        #http://codeidol.com/community/python/listboxes-and-scrollbars/17568/
        self.remote_browser.bind("<Double-1>", 
                                 (lambda event: self.submit_remote_directory()))

    
    ###################Fire it up!#################
    def __init__(self, master = None):
    
        ##Set up local variables:
        #Start location:
        self.app_start_dir = os.getcwd()
        #User home dir:
        self.local_user_home = os.environ['HOME']
        os.chdir(self.local_user_home)
        
        ##Initialize GUI
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.refresh_local_browser()
        
        ##Prompt for domain and username
        self.domain = tkSimpleDialog.askstring('Connect to the FesTiPhus network',
                                               'What is the address of the nameserver?',
                                               initialvalue = NS_DOMAIN)
        self.username = tkSimpleDialog.askstring('Connect to the FesTiPhus network',
                                                 'What is your username?')
        
                                               
        ##Set up server
        self.server_thread = Thread(target = self.start_server)
        self.server_thread.daemon = True
        #Start the server:
        self.server_thread.start()
        
        #register with ns:
        self.register()
            

app = Festiphus()
app.master.title("FesTiPhus")
app.mainloop()
