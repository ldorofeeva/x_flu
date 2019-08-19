# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 09:05:09 2019

@author: elisa
"""
import sys, os
import numpy as np
import h5py
import re
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from scipy.interpolate import griddata

class GUI:
    def __init__(self, master):
        # specify NeXus file format
        # To-do: change this section after getting a sample file
        self.Nexus_spec = dict(
            ftype=('.hdf5', '.nxs', '.nex'),
            grp_prefix='entry',
            grp='entry1',
            subgrp='data',
            ds_x='xp',
            ds_y='yp',
            ds_signal='sdd3'
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
        self.signal = None
        
        self.xi = self.yi = self.zi = None

        self.reinterpolate = True
        self.file_loaded = False
        self.entry_loaded = False
               
        # get x-ray energy lines
        self.xrelines_names = np.loadtxt(os.path.join('data', 'pertxre_lines.csv'),delimiter=',',dtype=object, usecols=(0,1))
        self.xrelines_vals = np.loadtxt(os.path.join('data', 'pertxre_lines.csv'),delimiter=',',dtype=int, usecols=2)
        # "Draw" interface row-wise
        ttk.Label(self.frame, text="Select file").grid(column=1, row=1, columnspan=3, sticky=(W,S))

        self.fname = StringVar()
        self.fname_entry = ttk.Entry(self.frame, textvariable=self.fname, width=100)
        self.fname_entry.grid(column=1, row=2, columnspan=10, sticky=(W,E))
        self.fname_entry.configure(state='readonly')
        self.fopen_button = ttk.Button(self.frame, text="...", command=self.fopen, width=4).grid(column=11, row=2, sticky=W)
        
        ttk.Label(self.frame, text="Select entry").grid(column=1, row=3, columnspan=3, sticky=(W,S))
        self.nxs_entry = StringVar()
        self.select_nxs_entry = ttk.Combobox(self.frame, textvariable=self.nxs_entry)
        self.select_nxs_entry.grid(column=1, row=4, columnspan=3, sticky=W)
        self.select_nxs_entry['values'] = ()
        self.nxs_entry.trace_add("write",self.load_entry)         
        
        ttk.Separator(self.frame, orient=HORIZONTAL).grid(column=1, row=5, columnspan=11, ipady=10)
        
        self.ereg_lbl = ttk.Label(self.frame, text="Energy region")
        self.ereg_lbl.grid(column=1, row=6, columnspan=5, sticky=(W,S))
        self.e_from = StringVar()
        ttk.Label(self.frame, text="from").grid(column=1, row=7, sticky=E)
        self.e_from_entry = ttk.Entry(self.frame, width=7, textvariable=self.e_from)
        self.e_from_entry.grid(column=2, row=7, sticky=(E,W))
        self.e_from.trace_add("write", self.display_lines)

        self.e_to = StringVar()
        ttk.Label(self.frame, text="to").grid(column=3, row=7, sticky=E )
        self.e_to_entry = ttk.Entry(self.frame, width=8, textvariable=self.e_to)
        self.e_to_entry.grid(column=4, row=7, sticky=(E,W))
        ttk.Label(self.frame, text="eV", width=15).grid(column=5, row=7, sticky=W )
        self.e_to.trace_add("write", self.display_lines)
        
        self.lines_in_erange_lbl = ttk.Label(self.frame, text=" ", width=60)
        self.lines_in_erange_lbl.grid(column=1, row=8, columnspan=5)

        ttk.Separator(self.frame, orient=HORIZONTAL).grid(column=1, row=9, columnspan=5)
        
        # choose colormap
        self.cmframe = ttk.Frame(self.frame)
        self.cmframe.grid(column=1, row=10, columnspan=7, rowspan=2, sticky=(W,S))
        self.cmap = StringVar()
        ttk.Label(self.cmframe, text="Colour map").grid(column=1, row=1, columnspan=4, sticky=(W,S))
        self.img_hc = PhotoImage(file=os.path.join('img', 'heatcool.png'))
        self.img_jet = PhotoImage(file=os.path.join('img', 'jet.png'))
        self.img_hsv = PhotoImage(file=os.path.join('img', 'hsv.png'))
        self.img_g = PhotoImage(file=os.path.join('img', 'greys.png'))
        self.heatcool = ttk.Radiobutton(self.cmframe, text='HeatCool', image=self.img_hc, variable=self.cmap, value='seismic')
        self.heatcool.grid(column=1, row=2)
        self.jet = ttk.Radiobutton(self.cmframe, text='Jet', image=self.img_jet, variable=self.cmap, value='jet')
        self.jet.grid(column=2, row=2)
        self.hsv = ttk.Radiobutton(self.cmframe, text='HSV', image=self.img_hsv, variable=self.cmap, value='hsv')
        self.hsv.grid(column=3, row=2)
        self.greys = ttk.Radiobutton(self.cmframe, text='Greyscale', image=self.img_g, variable=self.cmap, value='Greys')
        self.greys.grid(column=4, row=2)
        self.cmap.set('jet')

        #Advanced settings - choose patching or interpolation
        self.advframe = ttk.Frame(self.frame)
        self.advframe.grid(column=8, row=6, columnspan=6, rowspan=4, sticky=E)
        
        self.adv_settings = StringVar()
        self.adv_check = ttk.Checkbutton(self.advframe, text='Advanced settings', command=self.set_advanced_view, variable=self.adv_settings, onvalue='on', offvalue='off')
        self.adv_check.grid(column=1, row=1, columnspan=6, sticky=W)
        self.adv_settings.set('off')
        
        self.vtype = StringVar()
        self.patch = ttk.Radiobutton(self.advframe, text='Patch', variable=self.vtype, value='patch', command=self.set_advanced_view)
        self.patch.grid(column=1, row=2, columnspan=3, sticky=W, ipadx=3)
        self.interp = ttk.Radiobutton(self.advframe, text='Interpolate', variable=self.vtype, value='interp', command=self.set_advanced_view)
        self.interp.grid(column=4, row=2, columnspan=3, sticky=W)
        self.vtype.set('interp')
        
        # settings for patch
        self.patch_size = StringVar()
        self.pslabel = ttk.Label(self.advframe, text="Patch size")
        self.pslabel.grid(column=1, row=3, sticky=W)
        self.patch_size_entry = ttk.Entry(self.advframe, width=10, textvariable=self.patch_size)
        self.patch_size_entry.grid(column=2, row=3, sticky=W)
        self.patch_size.set(str(0.05))
        self.pslabel2 = ttk.Label(self.advframe, text="mm")
        self.pslabel2.grid(column=3, row=3, sticky=W)
        
        
        # settings for interpolation
        self.grid_step = StringVar()
        self.gslabel = ttk.Label(self.advframe, text="Grid step")
        self.gslabel.grid(column=4, row=3, sticky=W)
        self.grid_step_entry = ttk.Entry(self.advframe, width=10, textvariable=self.grid_step)
        self.grid_step_entry.grid(column=5, row=3, sticky=(W, E))
        self.grid_step.set(str(0.025))
        self.grid_step.trace_add("write", self.set_reinterpolate)
        self.gslabel2 = ttk.Label(self.advframe, text="mm")
        self.gslabel2.grid(column=6, row=3, sticky=W)
        
        self.itype = StringVar()
        self.itlabel = ttk.Label(self.advframe, text="Method")
        self.itlabel.grid(column=4, row=4, sticky=W)
        self.itchoices = { 'nearest', 'linear' }
        self.itype.set('nearest') 
        self.itype.trace_add("write", self.set_reinterpolate)
        self.itype_menu = OptionMenu(self.advframe, self.itype, *self.itchoices) 
        self.itype_menu.grid(column=5, row=4, columnspan=2, sticky=(W, E))
        
        self.adv_wgt_grp = { self.interp, self.patch }
        self.int_wgt_grp = { self.gslabel, self.grid_step_entry, self.gslabel2, self.itlabel, self.itype_menu }
        self.ptch_wgt_grp = { self.pslabel, self.patch_size_entry, self.pslabel2 }
        
        for el in {*self.adv_wgt_grp, *self.int_wgt_grp, *self.ptch_wgt_grp}:
            el.configure(state=DISABLED)
        
            
        #render button
        self.render_button = ttk.Button(self.frame, text="Render", command=self.render)
        self.render_button.grid(column=12, row=13, columnspan=2, sticky=E, ipadx=2, ipady=2)

        # add padding around iface elements
        for child in self.frame.winfo_children(): child.grid_configure(padx=2, pady=2)
        self.advframe.grid_configure(padx=10)
        self.render_button.grid_configure(pady=10)
        for child in self.cmframe.winfo_children(): child.grid_configure(padx=2, pady=2)
        for child in self.advframe.winfo_children(): child.grid_configure(padx=2, pady=2)
        
        # set focus on erange lower limit
        self.e_from_entry.focus()

        # call render on pressing "Enter"
        self.master.bind('<Return>', self.render)

    def fopen(self, *args):
        try:
            fname_val = filedialog.askopenfilename()
            if not os.path.isfile(fname_val):
                messagebox.showinfo(message=f'Unable to open file: {fname_val} - no such file')
                return
            #do not reload same file
            if self.fname.get()==fname_val: 
                return
            if not fname_val.endswith(self.Nexus_spec['ftype']):
                messagebox.showinfo(message='File format not supported')
                self.file_loaded = False
            else:
                self.reinterpolate = True
                with h5py.File(fname_val, "r") as h5f:
                    # load entry names
                    grps = ()
                    for k in h5f.keys():
                        dsinf = str(h5f[k])
                        enames = re.search(f'{self.Nexus_spec["grp_prefix"]}([0-9]+)', dsinf)
                        if enames: 
                            ename=enames.group(0)
                            grps = grps + (ename,) 
                # check the correctness of datasets naming
                if len(grps) == 0:
                    messagebox.showinfo(message='File does not correspond NeXus format. Please select another file')
                    return
                
                self.fname_entry.configure(state=NORMAL)
                self.fname.set(fname_val)
                self.fname_entry.configure(state='readonly')
                self.select_nxs_entry['values'] = grps
                #grp = grps[0]
                #self.nxs_entry.set(grp)
                self.file_loaded = True
                
        except ValueError:
            pass
        
    def load_entry(self, *args):
        self.reinterpolate = True
        fname_val = self.fname.get()
        with h5py.File(fname_val, "r") as h5f:
            grp = self.nxs_entry.get()
            self.xs = h5f[grp + '/' + self.Nexus_spec['subgrp'] + '/' + self.Nexus_spec['ds_x']][:]
            self.ys = h5f[grp + '/' + self.Nexus_spec['subgrp'] + '/' + self.Nexus_spec['ds_y']][:]
            self.signal = h5f[grp + '/' + self.Nexus_spec['subgrp'] + '/' + self.Nexus_spec['ds_signal']][:]
            # check the shape of datasets, if wrong
            if not self.signal.shape[0] == self.xs.shape[0] == self.ys.shape[0]:
                messagebox.showinfo(message=f'Datasets shape do not correspond, group {grp}')
                self.entry_loaded = False 
                return
            idx0 = 0
            idx1 = 10*(len(self.signal[0])-1)
            self.ereg_lbl['text'] = self.ereg_lbl['text'] + f' (from {idx0} to {idx1} eV)'
        self.entry_loaded = True
        
    def set_advanced_view(self, *args):        
        adv_s_val = self.adv_settings.get()
        if adv_s_val=='on':
            for el in self.adv_wgt_grp:
                el.configure(state=NORMAL)
            vtype_val = self.vtype.get()
            if vtype_val == 'interp':
                for el in self.int_wgt_grp:
                    el.configure(state=NORMAL)
                for el in self.ptch_wgt_grp:
                    el.configure(state=DISABLED)
            else:
                for el in self.int_wgt_grp:
                    el.configure(state=DISABLED)
                for el in self.ptch_wgt_grp:
                    el.configure(state=NORMAL)
        else:
            for el in {*self.adv_wgt_grp, *self.int_wgt_grp, *self.ptch_wgt_grp}:
                el.configure(state=DISABLED)
                
       
    def set_reinterpolate(self, *args):
        self.reinterpolate = True
    
    def display_lines(self, *args):
        try:
            e_from_val = float(self.e_from.get())
            e_to_val = float(self.e_to.get())
            
            idx0 = int(e_from_val/10)
            if idx0<0: idx0=0
            idx1 = int(e_to_val/10)
            if idx1<0: idx1=0
            
            if e_to_val >= e_from_val:
                matches = np.where(np.logical_and(self.xrelines_vals>=e_from_val, self.xrelines_vals<=e_to_val))[0]
                s=''
                if 0 < len(matches) <= 3:
                    s = ' : ' + '; '.join(el[0]+'('+el[1]+')'  for el in self.xrelines_names[matches])
                self.lines_in_erange_lbl['text'] = f'{len(matches)} lines in vicinity {s}'
            else:
                self.lines_in_erange_lbl['text'] = ''
        except ValueError:
            pass
        
    def render(self, *args):
        try:
            if not self.file_loaded:
                messagebox.showinfo(message='Please select file')
                return
            if not self.entry_loaded:
                messagebox.showinfo(message='Please select entry')
                return
            #check if file and entry selected
            e_from_val = float(self.e_from.get())
            e_to_val = float(self.e_to.get())

            if e_from_val > e_to_val:
                messagebox.showinfo(message='Lower energy limit is higher than upper energy limit. Please enter a correct energy range.')
                return

            idx0 = int(e_from_val/10)
            if idx0<0: idx0=0
            idx1 = int(e_to_val/10)
            if idx1<0: idx1=0
            
            self.e_from.set(str(idx0*10))
            self.e_to.set(str(idx1*10))

            xmin = round(min(self.xs),3)
            xmax = round(max(self.xs),3)
            ymin = round(min(self.ys),3)
            ymax = round(max(self.ys),3)
            
            if self.vtype.get()=='interp':
            # interpolate on grid 
                grid_step_val = float(self.grid_step.get())
                if self.reinterpolate:
                    self.xi = np.arange(xmin,xmax+grid_step_val,grid_step_val)
                    self.yi = np.arange(ymin,ymax+grid_step_val,grid_step_val)
                    self.xi,self.yi = np.meshgrid(self.xi,self.yi)
                    
                    self.zi = griddata((self.xs,self.ys),self.signal,(self.xi,self.yi),method=self.itype.get())
                    
                    self.reinterpolate = False
                    
                fig, ax = plt.subplots()
                if idx1==idx0:
                    im = ax.pcolormesh(self.xi, self.yi, self.zi[:,:,idx0], cmap=self.cmap.get())
                else:
                    im = ax.pcolormesh(self.xi, self.yi, self.zi[:,:,idx0:idx1].sum(axis=2), cmap=self.cmap.get())
                ax.axis([xmin, xmax, ymin, ymax])
                ax.set_xlabel('X, μm'), ax.set_ylabel('Y, μm')
                fig.colorbar(im, ax=ax)
                plt.show()            
                plt.close()
            else:
            #patching
                shift = 0.5
                xs0 = np.zeros(len(self.xs))
                xs0[0] = self.xs[0]
                for i in range(1, len(self.xs)):
                    xs0[i] = self.xs[i] + shift * (self.xs[i] - self.xs[i - 1])
                # get array of intensities for energies within region
                sdd = self.signal[:,idx0:idx1].sum(axis=1)
    
                fig, ax = plt.subplots()
                xy = zip(xs0, self.ys)
                # construct Rects
                patch_size_val = float(self.patch_size.get())
                patches = [Rectangle(xyi, width=patch_size_val,height=patch_size_val) for xyi in xy]
                p = PatchCollection(patches, cmap=self.cmap.get())
                p.set_array(sdd)
                ax.add_collection(p)
                ax.axis([xmin, xmax, ymin, ymax])
                ax.set_xlabel('X, μm'), ax.set_ylabel('Y, μm')
                plt.colorbar(p)
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
