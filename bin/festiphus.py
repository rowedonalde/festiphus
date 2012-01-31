#festiphus.py
#Main script for Festiphus

import pygtk
pygtk.require('2.0')
import gtk
import ftplib

#instance for a Festiphus session:
class Festiphus:
    
    #FTP sessions in this instance of Festiphus
    #At first, I'll support 1, but this should be able to grow
    sessions = []
    
    #Initiate an FTP connection:
    def open_connection(self, address, name):
        new_conn = ftplib.FTP(address, name)
        self.sessions.append(new_conn)
        self.refresh_file_browser(new_conn)
        
    #Use the input to trigger an open_connection:
    def submit_connection(self, widget, data = None):
        address = self.host_input.get_text()
        name = self.name_input.get_text()
        self.open_connection(address, name)
    
    #Use these to close the app window:
    def delete_event(self, widget, event, data = None):
        print "delete event occurred"
        return False     
    def destroy(self, widget, data = None):
        gtk.main_quit()
        
    #Populates the file browser:
    #Right now it's pretty non-interactive: it just shows the
    #response code from the LIST request
    def refresh_file_browser(self, session):
        #Get the contents (essentially run ls):
        contents = session.retrlines('LIST')
        
        #Display the contents:
        self.file_browser.set_text(contents)
    
    def __init__(self):
        #the window it takes place in:
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)
        
        #Destroyer listener. Closes the app window:
        self.window.connect("destroy", self.destroy)
        
        #Host input, Name input, and connect button:
        self.host_input = gtk.Entry()
        self.name_input = gtk.Entry()
        self.connect_button = gtk.Button("Connect")
        
        #Set the callback for the Connect Button:
        self.connect_button.connect('clicked', self.submit_connection, None)
        
        #hbox for host/name/connect:
        self.conn_box = gtk.HBox(False, 0)
        self.conn_box.pack_start(self.host_input)
        self.conn_box.pack_start(self.name_input)
        self.conn_box.pack_start(self.connect_button)
        
        #show host/name/connect inputs:
        self.host_input.show()
        self.name_input.show()
        self.connect_button.show()
        self.conn_box.show()
        
        #File Browser:
        #Right now it's just text describing the files
        self.file_browser = gtk.Label('')
        self.file_browser.show()
        
        #Since the window can only hold 1 widget directly, put the file
        #browser and the conn_box in an hbox:
        self.container = gtk.VBox(False, 0)
        self.container.pack_start(self.conn_box)
        self.container.pack_start(self.file_browser)
        self.window.add(self.container)
        self.container.show()
        
        #Show the window:
        self.window.show()
        
    #Necessary to run:
    def main(self):
        gtk.main()
        
#Fire the whole thing up:
if __name__ == '__main__':
    fest = Festiphus()
    fest.main()
