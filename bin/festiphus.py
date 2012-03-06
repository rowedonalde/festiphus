#festiphus.py
#Main script for Festiphus, ported to Tkinter for GUI support

from Tkinter import *
import tkMessageBox
import ftplib
from pyftpdlib import ftpserver
from threading import Thread

SERVER_IP = '127.0.0.1'
SERVER_PORT = 3001

#instance for a Festiphus session:
class Festiphus(Frame):

    ###############Client#################
    #FTP sessions in this instance of Festiphus
    #At first, I'll support 1, but this should be able to grow
    sessions = []
    
    #The currently active session in the window:
    current_session = None

    #Initiate an FTP connection:
    def open_connection(self, host, port, name, password):
        new_conn = ftplib.FTP()
        new_conn.connect(host, port)
        new_conn.login(name, password)
        self.sessions.append(new_conn)
        self.refresh_file_browser(new_conn)
        
        #for right now, the active session is just this one:
        self.current_session = new_conn

    #Use the input to trigger an open_connection:
    def submit_connection(self):
        host = self.host_input.get()
        port = self.port_input.get()
        name = self.name_input.get()
        password = self.password_input.get()
        self.open_connection(host, port, name, password)

    #Refresh the file browser and the directory name:
    def refresh_file_browser(self, conn):
        #Set the new current directory:
        self.current_dir.set(conn.pwd())
        
        #clear out the current list:
        self.file_browser.delete(0, END)

        #display the directory contents:
        self.file_list = conn.nlst() #debating whether this should be in class
        #if this isn't the root dir, put a dir link to up one level:
        if conn.pwd() != '/':
            self.file_browser.insert(0, '..')
        for f in self.file_list:
            self.file_browser.insert(END, f)
        
    #Move the working directory to the given dir in the given connection:
    def cd(self, directory, conn):
        #move to the given dir:
        conn.cwd(directory)
        
        #refresh the file browser:
        self.refresh_file_browser(conn)
    
    #Use the input to change the directory:
    def submit_directory(self):
        #A list of the indices that are currently selected in the file browser:
        cur_selected = self.file_browser.curselection()
        
        #The relative name of the first selected item:
        #TODO: make sure it's a dir and not a file
        #target_dir = self.current_session.pwd() + '/' + cur_selected[0]
        target_dir = self.file_browser.get(cur_selected[0])
        
        #test--alert the name of the target_dir:
        tkMessageBox.showinfo("new dir name", target_dir)
        
        #Move to the given dir:
        self.cd(target_dir, self.current_session)
    
    
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
        self.authorizer.add_user(new_name, new_pass, 'ftproot')
        
        #Alert that the new user has been added:
        tkMessageBox.showinfo('Alert', 'New user added')
    

    ################GUI######################
    #Build the widgets
    def createWidgets(self):

        ##Client Control
        #host entry:
        self.host_input = Entry(self)
        self.host_input.grid(column = 0, row = 0)
        
        #port entry:
        self.port_input = Entry(self)
        self.port_input.grid(column = 1, row = 0)

        #name entry:
        self.name_input = Entry(self)
        self.name_input.grid(column = 2, row = 0)

        #password entry:
        self.password_input = Entry(self, show = '*')
        self.password_input.grid(column = 3, row = 0)
        
        #connect button:
        self.connect_button = Button(self, text = 'Connect',
                                     command = self.submit_connection)
        self.connect_button.grid(column = 4, row = 0)
        
        ##Server Control
        #new name entry:
        self.new_name_input = Entry(self)
        self.new_name_input.grid(column = 0, row = 1)
        
        #new password entry:
        self.new_pass_input = Entry(self)
        self.new_pass_input.grid(column = 1, row = 1)
        
        #add new user button:
        self.new_user_button = Button(self, text = 'Add New User',
                                      command = self.add_user)
        self.new_user_button.grid(column = 2, row = 1)

        #current directory:
        self.current_dir = StringVar() #dir_label will follow this
        self.dir_label = Label(self, textvariable = self.current_dir)
        self.dir_label.grid(row = 2)

        ##file browser:
        #window:
        self.file_browser = Listbox(self)
        self.file_browser.grid(columnspan = 4, column = 0, row = 2)
        
        #change dir button:
        self.change_dir_button = Button(self, text = 'Change Directory',
                                        command = self.submit_directory)
        self.change_dir_button.grid(column = 4, row = 2)
    
    ###################Fire it up!#################
    def __init__(self, master = None):
    
        #Put the server in its own thread:
        #class Server_Thread(Thread):
        #    def __init__(self, parent):
        #        self.parent = parent
        #
        #    def run(self):
        #        parent.start_server()
        
        
        self.server_thread = Thread(target = self.start_server)
        self.server_thread.daemon = True
        #self.server_thread = Server_Thread()
        #self.server_thread.__init__(self)
        #Start the server:
        self.server_thread.start()
        
        
        #Initialize GUI
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
            

app = Festiphus()
app.master.title("Festiphus")
app.mainloop()
