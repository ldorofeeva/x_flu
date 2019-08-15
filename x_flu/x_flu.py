# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 09:05:09 2019

@author: elisa
"""
import sys, os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
import h5py
import matplotlib.pyplot as plt
import numpy as np

class GUI:
    def __init__(self, master):
        # specify NeXus file format
        # To-do: change this section after getting a sample file
        self.Nexus_spec = dict(
            ftype=('.hdf5', '.nxs', '.nex'),
            ds_x='x_values',
            ds_y='y_values',
            ds_e='energy_values',
            ds_i='intensity_values'
            )
        
        #initialize tk window parameters
        self.master = master
        self.master.title("X_flu")
        self.frame = ttk.Frame(self.master, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(N, W, E, S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        
        #initialize vars
        self.eps = 2 * sys.float_info.epsilon #reqired for proper float comparison
        self.xs = None
        self.ys = None
        self.energs = None
        self.intens = None

        self.fname = StringVar()
        self.e_from = StringVar()
        self.e_to = StringVar()
        self.cmap = StringVar()
        
        # "Draw" interface row-wise
        ttk.Label(self.frame, text="Select file").grid(column=1, row=1, columnspan=3, sticky=W)
        
        self.fname_entry = ttk.Entry(self.frame, width=80, textvariable=self.fname) #To-do: make readonly
        self.fname_entry.grid(column=1, row=2, columnspan=4, sticky=W)
        self.fopen_button = ttk.Button(self.frame, text="...", command=self.fopen).grid(column=5, row=2, sticky=E)
        
        ttk.Label(self.frame, text="Energy region").grid(column=1, row=3, columnspan=3, sticky=W)
        
        ttk.Label(self.frame, text="from").grid(column=1, row=4, sticky=E)
        self.e_from_entry = ttk.Entry(self.frame, width=20, textvariable=self.e_from)
        self.e_from_entry.grid(column=2, row=4, sticky=(W, E))
        
        ttk.Label(self.frame, text="to").grid(column=3, row=4, sticky=E )
        self.e_to_entry = ttk.Entry(self.frame, width=20, textvariable=self.e_to)
        self.e_to_entry.grid(column=4, row=4, sticky=(W, E))
        
        
        ttk.Label(self.frame, text="Colour map").grid(column=1, row=5, columnspan=3, sticky=W)
        self.img_hc = PhotoImage(file=os.path.join('img', 'heatcool.png'))
        self.img_jet = PhotoImage(file=os.path.join('img', 'jet.png'))
        self.img_hsv = PhotoImage(file=os.path.join('img', 'hsv.png'))
        self.img_g = PhotoImage(file=os.path.join('img', 'greys.png'))
        self.heatcool = ttk.Radiobutton(self.frame, text='HeatCool', image=self.img_hc, variable=self.cmap, value='seismic')
        self.heatcool.grid(column=1, row=6)
        self.jet = ttk.Radiobutton(self.frame, text='Jet', image=self.img_jet, variable=self.cmap, value='jet')
        self.jet.grid(column=2, row=6)
        self.hsv = ttk.Radiobutton(self.frame, text='HSV', image=self.img_hsv, variable=self.cmap, value='hsv')
        self.hsv.grid(column=3, row=6)
        self.greys = ttk.Radiobutton(self.frame, text='Greyscale', image=self.img_g, variable=self.cmap, value='Greys')
        self.greys.grid(column=4, row=6)
        self.cmap.set('seismic')
        
        self.render_button = ttk.Button(self.frame, text="Render", command=self.render).grid(column=5, row=7, sticky=E)
        
        # add padding around iface elements
        for child in self.frame.winfo_children(): child.grid_configure(padx=5, pady=5)
        
        # set focus on erange lower limit
        self.e_from_entry.focus()
        
        # call render on pressing "Enter"
        self.master.bind('<Return>', self.render)
    
    def fopen(self, *args):
        try:
            self.fname_val = filedialog.askopenfilename()
            if self.fname_val.endswith(self.Nexus_spec['ftype']):              
                with h5py.File(self.fname_val, "r") as f:
                    # check the correctness of datasets naming 
                    if not all(ds in f for ds in [self.Nexus_spec[dsn] for dsn in ['ds_x','ds_y','ds_e','ds_i']]):
                        messagebox.showinfo(message='File does not correspond NeXus format. Please check your file')
                        return
                    
                    self.xs = f[self.Nexus_spec['ds_x']][:]
                    self.ys = f[self.Nexus_spec['ds_y']][:]
                    self.energs = f[self.Nexus_spec['ds_e']][:]
                    self.intens = f[self.Nexus_spec['ds_i']][:]
            
                # check the shape of datasets, if wrong 
                if not self.intens.shape == (self.xs.shape[0], self.ys.shape[0], self.energs.shape[0]):
                    messagebox.showinfo(message='Datasets shape do not correspond. Please check your file')
                    return
                self.fname_entry.delete(0, 'end')
                self.fname_entry.insert(0, self.fname_val)
                
                # optional - fill ergange with min and max energies from file
                self.e_from_entry.insert(0, str(self.energs.min()))
                self.e_to_entry.insert(0, str(self.energs.max()))
            else:
                messagebox.showinfo(message='File format not supported')
        except ValueError:
            pass

        
    def render(self, *args):
        try:
            self.fname_val = self.fname_entry.get()
            e_from_val = float(self.e_from_entry.get())
            e_to_val = float(self.e_to_entry.get())
                
            if e_from_val > e_to_val:
                messagebox.showinfo(message='Lower energy limit is higher than upper energy limit. Please enter a correct energy range.')
                return
            if not os.path.isfile(self.fname_val):
                messagebox.showinfo(message=f'Unable to open file: {self.fname_val} - no such file')
                return
            
            # get array of indices for energies within region 
            e_idx = np.where(np.logical_and((self.energs-e_from_val)>=-self.eps, (e_to_val - self.energs)>=self.eps))[0]
            # check if there is data in the region
            if not len(e_idx):
                messagebox.showinfo(message=f"No data for selected energy range. Please try energies from {np.amin(self.energs)} to {np.amax(self.energs)}." )
                return
            
            #get combined intensity of the region
            intens_2d = self.intens[:,:,e_idx].sum(axis=2).T
            
            X, Y = np.meshgrid(self.xs, self.ys)
            
            fig, ax = plt.subplots()
            im = ax.pcolormesh(X, Y, intens_2d, cmap=self.cmap.get())
            ax.set_xlabel('X, μm'), ax.set_ylabel('Y, μm')
            fig.colorbar(im, ax=ax)
            plt.show()
            plt.close()
            
        except ValueError:
            messagebox.showinfo(message='File name or energy range is empty or incorrect')
            pass
                
def main(): 
    root = Tk()
    GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()      
