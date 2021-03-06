from tkinter import *
import tkinter.messagebox
import tkinter.filedialog
from tkinter import ttk
import USBCanAnalyzerV7
import Settings, Database
import datetime
import os 

class CanViewGui:

    # Menu Handlers
    def export_report(self):
        file_save_str = ""
        file_save_str += "time,id,data,\r\n"
        for child in self.tree.get_children():
            file_save_str +=self.tree.item(child)["text"] + "," + self.tree.item(child)["values"][0] + "," + self.tree.item(child)["values"][1] + "\r\n"
            
        f = tkinter.filedialog.asksaveasfile(mode='w', defaultextension='.csv', filetypes=[('CSV file','*.csv'), ('All files','*.*')], initialdir=os.getcwd(), title="Save Messages to CSV", initialfile='can_msg_log.csv')
        if(f is None):
            return
        f.write(file_save_str)
        f.close()
        return

    def load_database(self):
        fname = tkinter.filedialog.askopenfilename( defaultextension='.xml', filetypes=[('Database XML file','*.xml'), ('All files','*.*')], initialdir=os.getcwd(), title="Open Database", initialfile='db.xml')
        if(fname is None):
            return
        else:
            self.msg_db.loadDb(fname)
        
        
    #Can message pane interaction
    def insert_can_msg_display(self, time, id, can_data, name, subentries):
        new_elem = self.tree.insert('', 0, text= str(time), values=(id, can_data,name))
        for name in subentries:
            datastr = "  ->" + name + " : " + subentries[name]
            self.tree.insert(new_elem, 'end', text="", values=("","",datastr))
        self.tree.counter = self.tree.counter + 1

    def clear_can_msg_display(self):
        self.tree.delete(*self.tree.get_children()) 

    #CAN TX options interaction
    def handle_tx_press(self):
        try:
            id_bytes=bytes.fromhex(self.idEntry.get())
        except:
            tkinter.messagebox.showinfo("Error", "ID " + self.idEntry.get() + " could not be parsed to a hexadecimal number" )
            return

        try:
            data_bytes=bytes.fromhex(self.dataEntry.get())
        except:
            tkinter.messagebox.showinfo("Error", "Data " + self.dataEntry.get() + " could not be parsed to a hexadecimal number" )
            return

        self.candevice.send(id_bytes, data_bytes)
        return

    # Handle user change of settings
    def openSettings(self):
        #Open dialog to have user input new settings
        self.settings.openGUI(self.master)

        #Push those settings into the subclasses
        self.candevice.set_config(int(self.settings.can_baud_rate),
                                  bool(self.settings.can_use_extended_frame),
                                  str(self.settings.can_serial_comport.split()[0]),
                                  int(self.settings.can_serial_baud)
        )

    #Test Classes
    def insert_test_packet(self):
        self.insert_can_msg_display("0.025","0x0C152A6F", "AA F0 B1 C5 89 6F 3D 4C", "My Message", {"val1": "25.9", "val2": "-34.3"})


    # Main Class
    def __init__(self, master, can_device):
        self.master = master
        self.candevice = can_device
        self.master.title("Can Viewer")

        #settings module
        self.settings = Settings.Settings()

        #database module
        self.msg_db = Database.dbProcessor()

        #Top-level GUI objects
        self.menubar = Menu(self.master)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.txContainer = Frame(self.master)
        self.rxContainer = Frame(self.master)


        #Top level file menu/options
        self.filemenu.add_command(label="Load Database", command=self.load_database)
        self.filemenu.add_command(label="Export Report", command=self.export_report)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Settings", command=self.openSettings)
        self.filemenu.add_command(label="Test", command=self.insert_test_packet)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.master.quit)

        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.menubar.add_command(label="Go Online", command=self.candevice.open)
        self.menubar.add_command(label="Go Offline", command=self.candevice.close)
        self.menubar.add_command(label="Clear", command=self.clear_can_msg_display)

        #TX pane
        self.sendButtom = Button(self.txContainer, text="Send", command=self.handle_tx_press)
        self.idEntryContainer = Frame(self.txContainer)
        self.dataEntryContainer = Frame(self.txContainer)
        self.idEntryLabel = Label(self.idEntryContainer, text="ID")
        self.dataEntryLabel = Label(self.dataEntryContainer, text="Data")
        self.idEntry = Entry(self.idEntryContainer,width=10)
        self.dataEntry = Entry(self.dataEntryContainer, width=26)

        #RX pane with treeview and scrollbar
        self.tree = ttk.Treeview(self.rxContainer)
        self.vsb = ttk.Scrollbar(self.rxContainer, orient="vertical", command=self.tree.yview)

        self.tree.counter = 0
        self.tree['columns'] = ('Time (s)', 'ID', 'Data')
        self.tree.heading('#0', text='Time', anchor=tkinter.CENTER)
        self.tree.heading('#1', text='CAN ID', anchor=tkinter.CENTER)
        self.tree.heading('#2', text='CAN Data', anchor=tkinter.CENTER)
        self.tree.heading('#3', text='Name', anchor=tkinter.CENTER)
        self.tree.column('#0', stretch=tkinter.YES, minwidth=85, width=85)
        self.tree.column('#1', stretch=tkinter.YES, minwidth=85, width=85)
        self.tree.column('#2', stretch=tkinter.YES, minwidth=170, width=170)
        self.tree.column('#3', stretch=tkinter.YES, minwidth=130, width=130)
        self.tree.configure(yscrollcommand=self.vsb.set)

        # LAYOUT
        self.master.config(menu=self.menubar)

        self.idEntryLabel.pack(side=LEFT, fill='none')
        self.dataEntryLabel.pack(side=LEFT, fill='none')
        self.idEntry.pack(side=RIGHT, fill='none')
        self.dataEntry.pack(side=RIGHT, fill='none')
        self.idEntryContainer.pack(side=LEFT, fill='y')
        self.dataEntryContainer.pack(side=LEFT, fill='y')
        self.sendButtom.pack(side=RIGHT, fill='none')
        self.txContainer.pack(side=TOP, fill='none',expand=FALSE)

        self.vsb.pack(side=RIGHT, fill='y')
        self.tree.pack(side=LEFT, fill='both',expand=TRUE)
        self.rxContainer.pack(side=BOTTOM, fill='both',expand=TRUE)


    def gui_run(self):
        #Kick off the background update task
        self.periodic_update()

        #Kick off the gui. Blocks till closed.
        self.master.mainloop()
        return

    def periodic_update(self):
        msg_list = self.candevice.receive()

        for msg in msg_list:
            timestr = str(msg.get_rx_time_delta_start().total_seconds())
            msg_interpretation = self.msg_db.getInfo(msg.id, msg.data)
            if(msg_interpretation != None):
                name_str  = msg_interpretation['name']
                data_dict = msg_interpretation['data']
            else:
                name_str  = ""
                data_dict = {}
                
            self.insert_can_msg_display(timestr,msg.get_id_string(), msg.get_data_string(), name_str, data_dict)

        self.master.after(10, self.periodic_update)
        return




#############################################################
# MAIN Code execution starts here
#############################################################
if __name__ == "__main__":
    
    interface = USBCanAnalyzerV7.DeviceInterface()

    my_gui = CanViewGui(Tk(), interface)
    my_gui.gui_run() 

    #after gui closes...
    interface.close()
    