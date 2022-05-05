'''The ABQ Data Entry application'''
from cgitb import text
from datetime import datetime
from pathlib import Path
import csv
import tkinter as tk
from tkinter import ttk

class BoundText(tk.Text):
    """A Text widget with a bound variable"""
    def __init__(self, *args, textvariable=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._variable = textvariable
        if self._variable:
            self.insert('1.0', self._variable.get())
            self._variable.trace_add('write', self._set_content)
            self.bind('<<Modified>>', self._set_var)

    def _set_content(self, *_):
        """Set the text contents to the variable"""
        self.delete('1.0', tk.END)
        self.insert('1.0', self._variable.get())

    
    def _set_var(self, *_):
        """Set the variable to the text contents"""
        if self.edit_modified():
            content = self.get('1.0', 'end-1chars')
            self._variable.set(content)
            self.edit_modified(False)


class LabelInput(tk.Frame):
    """A widget containing a label and input together"""
    def __init__(
        self, parent, label, var, input_class=ttk.Entry,
        input_args=None, label_args=None, **kwargs
    ):
        super().__init__(parent, **kwargs)
        input_args = input_args or {}
        label_args = label_args or {}
        self.variable = var
        self.variable.label_widget = self

        if input_class in (ttk.Checkbutton, ttk.Button):
            input_args['text'] = label
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))

        if input_class in (ttk.Checkbutton, ttk.Button, ttk.Radiobutton):
            input_args["variable"] = self.variable
        else:
            input_args['textvariable'] = self.variable

        if input_class == ttk.Radiobutton:
            self.input = tk.Frame(self)
            print(input_args)
            for v in input_args.pop('values', []):
                button = ttk.Radiobutton(
                    self.input, value=v, text=v, **input_args
                )
                button.pack(
                    side=tk.LEFT, ipadx=10, ipady=2, expand=True, fill='x'
                )
        else:
            self.input = input_class(self, **input_args)


        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)
    
    def grid(self, sticky=(tk.W + tk.E), **kwargs):
        """Override grid to add default sticky values"""
        super().grid(sticky=sticky, **kwargs)


class DataRecordForm(ttk.Frame):
    """The input form for our widgets"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._vars = {
            'Date': tk.StringVar(),
            'Time': tk.StringVar(),
            'Technician': tk.StringVar(),
            'Lab': tk.StringVar(),
            'Plot': tk.StringVar(),
            'Seed Sample': tk.StringVar(),
            'Humidity': tk.DoubleVar(),
            'Light': tk.DoubleVar(),
            'Temperature': tk.DoubleVar(),
            'Equipment Fault': tk.BooleanVar(),
            'Plants': tk.IntVar(),
            'Blossoms': tk.IntVar(),
            'Fruit': tk.IntVar(),
            'Min Height': tk.DoubleVar(),
            'Max Height': tk.DoubleVar(),
            'Med Height': tk.DoubleVar(),
            'Notes': tk.StringVar()
        }
        r_info = self._add_frame('Record Information')
        LabelInput(
            r_info, 'Date', var=self._vars['Date']
        ).grid(row=0, column=0)
        LabelInput(
            r_info,'Time', input_class=ttk.Combobox,
            var=self._vars['Time'],
            input_args={'values': ["8:00", '12:00', '16:00', '20:00']}
        ).grid(row=0, column=1)
        LabelInput(
            r_info, 'Technician', var=self._vars['Technician']
        ).grid(row=0, column=2)
        LabelInput(
            r_info, 'Lab', input_class=ttk.Radiobutton,
            var=self._vars['Lab'],
            input_args={'values': ['A', 'B', 'C']}
        ).grid(row=1, column=0)
        LabelInput(
            r_info, 'Plot', input_class=ttk.Combobox,
            var=self._vars['Plot'],
            input_args={'values': list(range(1,21))}
        ).grid(row=1, column=1)
        LabelInput(
            r_info, 'Seed Sample', var=self._vars['Seed Sample']
        ).grid(row=1, column=2)
        
        e_info = self._add_frame('Environment Data')
        LabelInput(
            e_info, 'Humidity (g/m\u00b3)',
            input_class=ttk.Spinbox, var=self._vars['Humidity'],
            input_args={'from_': 0.5, 'to': 52.0, 'increment': .01}
        ).grid(row=0, column=0)
        LabelInput(
            e_info, 'Light (klx)', input_class=ttk.Spinbox,
            var=self._vars['Light'],
            input_args={'from_': 0, 'to': 100, 'increment': .01}
        ).grid(row=0, column=1)
        LabelInput(
            e_info, 'Temperature \u00b0\u0043', 
            input_class=ttk.Spinbox, var=self._vars['Temperature'],
            input_args={'from_': 4, 'to': 40, 'increment': .01}
        ).grid(row=0, column=2)
        LabelInput(
            e_info, 'Equipment Fault',
            input_class=ttk.Checkbutton,
            var=self._vars['Equipment Fault']
        ).grid(row=1, column=1, columnspan=3)

        p_info = self._add_frame('Plant Data')
        LabelInput(
            p_info, 'Plants', input_class=ttk.Spinbox,
            var=self._vars['Plants'],
            input_args={'from_': 0, 'to': 20}
        ).grid(row=0, column=0)
        LabelInput(
            p_info, 'Blossoms', input_class=ttk.Spinbox,
            var=self._vars['Blosssoms'],
            input_args={'from_': 0, 'to': 1000}
        ).grid(row=0, column=2)
        LabelInput(
            p_info, 'Min Height (cm)',
            input_class=ttk.Spinbox, var=self._vars['Min Height'],
            input_args={'from_': 0, 'to': 1000, 'increment': .01}
        ).grid(row=1, column=0)
        LabelInput(
            p_info, 'Max Height (cm)', input_class=ttk.Spinbox,
            var=self._vars['Med Height'],
            input_args={'from_': 0, 'to': 1000, 'increment': .01}
        ).grid(row=1, column=2)
        LabelInput(
            self, 'Notes', input_class=BoundText,
            var=self._vars['Notes'],
            input_args={'width': 75, 'height': 10}
        ).grid(sticky=tk.W, row=3, column=0)
        buttons = tk.Frame(self)
        buttons.grid(sticky=tk.W + tk.E, row=4)
        self.savebutton = ttk.Button(
            buttons, text='Save', command=self.master._on_save
        )
        self.savebutton.pack(side=tk.RIGHT)
        self.resetbutton = ttk.Button(
            buttons, text='Reset', command=self.reset
        )
        self.resetbutton.pack(side=tk.RTGHT)

    def _add_frame(self, label, cols=3):
        """Add a LabelFrame to the form"""
        frame = ttk.LabelFrame(self, text=label)
        frame.grid(sticky=tk.W + tk.E)
        for i in range(cols):
            frame.columnconfigure(i, weight=1)
        return frame

    def reset(self):
        """Reset the form entries"""
        for var in self._vars.values():
            if isinstance(var, tk.BooleanVar):
                var.set(False)
            else:
                var.set('')

    def get(self):
        data = dict()
        fault = self._vars['Equipment Fault'].get()
        for key, variable in self._vars.items():
            if fault and key in ('Light', 'Humidity', 'Temperature'):
                data[key] = ''
            else:
                try:
                    data[key] = variable.get()
                except tk.TclError:
                    message = f'Error in field: {key}. Data was not saved!'
                    raise ValueError(message)
        return data

variables = dict()
records_saved = 0

root = tk.Tk()
root.title('ABQ Data Entry Application')
root.columnconfigure(0, weight=1)

ttk.Label(
    root,
    text='ABQ Data Entry Application',
    font=('TkDefaultFont', 16)
).grid()

# drf is short for data record form
drf = ttk.Frame(root)
drf.grid(padx=10, sticky=(tk.E + tk.W))
drf.columnconfigure(0, weight=1)

r_info = ttk.LabelFrame(drf, text='Record Information')
r_info.grid(sticky=(tk.W + tk.E))
for i in range(3):
    r_info.columnconfigure(i, weight=1)

variables['Date'] = tk.StringVar()
ttk.Label(r_info, text='Date').grid(row=0, column=0)
ttk.Entry(
    r_info, 
    textvariable=variables['Date']
).grid(row=1, column=0, sticky=(tk.W + tk.E))

time_values = ['8:00', '12:00', '16:00', '20:00']
variables['Time'] = tk.StringVar()
ttk.Label(r_info, text='Time').grid(row=0, column=1)
ttk.Combobox(
    r_info,
    textvariable=variables['Time'], value=time_values
).grid(row=1, column=1, stick=(tk.W + tk.E))

variables['Technician'] = tk.StringVar()
ttk.Label(r_info, text='Technician').grid(row=0, column=2)
ttk.Entry(
    r_info, textvariable=variables['Technician']
).grid(row=1, column=2, sticky=(tk.W + tk.E))

variables['Lab'] = tk.StringVar()
ttk.Label(r_info, text='Lab').grid(row=2, column=0)
labframe = ttk.Frame(r_info)
for lab in ('A', 'B', 'C'):
    ttk.Radiobutton(
        labframe, value=lab, text=lab, variable=variables['Lab']
    ).pack(side=tk.LEFT, expand=True)

labframe.grid(row=3, column=0, sticky=(tk.W + tk.E))

variables['Plot'] = tk.IntVar()
ttk.Label(r_info, text='Plot').grid(row=2, column=1)
ttk.Combobox(
    r_info,
    textvariable=variables['Plot'],
    values=[ x for x in range(1,21) ]
).grid(row=3, column=1, sticky=(tk.W + tk.E))

variables['Seed Sample'] = tk.StringVar()
ttk.Label(r_info, text='Seed Sample').grid(row=2, column=2)
ttk.Entry(
    r_info,
    textvariable=variables['Seed Sample']
).grid(row=3, column=2, sticky=(tk.W + tk.E))

e_info = ttk.LabelFrame(drf, text='Environment Data')
e_info.grid(sticky=(tk.W + tk.E))
for i in range(3):
    e_info.columnconfigure(i, weight=1)


variables['Humidity'] = tk.DoubleVar()
ttk.Label(e_info, text='Humidity (g/m\u00b3)').grid(row=0, column=0)
ttk.Spinbox(
    e_info, textvariable=variables['Humidity'],
    from_=0.5, to=52.0, increment=0.01
).grid(row=1, column=0, sticky=(tk.W + tk.E))

variables['Light'] = tk.DoubleVar()
ttk.Label(e_info, text='Light(klx)').grid(row=0, column=1)
ttk.Spinbox(
    e_info, textvariable=variables['Light'],
    from_=0, to=100, increment=0.01
).grid(row=1, column=1, sticky=(tk.W + tk.E))

variables['Temperature'] = tk.DoubleVar()
ttk.Label(e_info, text='Temperature \u00b0\u0043').grid(row=0, column=2)
ttk.Spinbox(
    e_info, textvariable=variables['Temperature'],
    from_=4, to=40, increment=.01
).grid(row=1, column=2, sticky=(tk.W + tk.E))

variables['Equipment Fault'] = tk.BooleanVar(value=False)
ttk.Checkbutton(
    e_info, variable=variables['Equipment Fault'],
    text='Equipment Fault'
).grid(row=2, column=0, sticky=tk.W, pady=5)

p_info = ttk.LabelFrame(drf, text='Plant Data')
p_info.grid(stick=(tk.W + tk.E))
for i in range(3):
    p_info.columnconfigure(i, weight=1)

variables['Plants'] = tk.IntVar()
ttk.Label(p_info, text='Plants').grid(row=0, column=0)
ttk.Spinbox(
    p_info, textvariable=variables['Plants'],
    from_=0, to=20, increment=1
).grid(row=1, column=0, sticky=(tk.W + tk.E))

variables['Blossoms'] = tk.IntVar()
ttk.Label(p_info, text='Blossoms').grid(row=0, column=1)
ttk.Spinbox(
    p_info, textvariable=variables['Blossoms'],
    from_=0, to=1000, increment=1
).grid(row=1, column=1, sticky=(tk.W + tk.E))

variables['Fruit'] = tk.IntVar()
ttk.Label(p_info, text='Fruit').grid(row=0, column=2)
ttk.Spinbox(
    p_info, textvariable=variables['Fruit'],
    from_=0, to=1000, increment=1
).grid(row=1, column=2, sticky=(tk.W + tk.E))

variables['Min Height'] = tk.DoubleVar()
ttk.Label(p_info, text='Min Height (cm)').grid(row=2, column=0)
ttk.Spinbox(
    p_info, textvariable=variables['Min Height'],
    from_=0, to=1000, increment=0.01
).grid(row=3, column=0, stick=(tk.W + tk.E))

variables['Max Height'] = tk.DoubleVar()
ttk.Label(p_info, text='Max Height (cm)').grid(row=2, column=1)
ttk.Spinbox(
    p_info, textvariable=variables['Max Height'],
    from_=0, to=1000, increment=0.01
).grid(row=3, column=1, sticky=(tk.W + tk.E))

variables['Med Height'] = tk.DoubleVar()
ttk.Label(p_info, text='Median Height (cm)').grid(row=2, column=2)
ttk.Spinbox(
    p_info, textvariable=variables['Med Height'],
    from_=0, to=1000, increment=0.01
).grid(row=3, column=2, sticky=(tk.W + tk.E))

ttk.Label(drf, text='Notes').grid()
notes_inp = tk.Text(drf, width=75, height=10)
notes_inp.grid(sticky=(tk.W + tk.E))

buttons = tk.Frame(drf)
buttons.grid(stick=tk.W + tk.E)
save_button = ttk.Button(buttons, text='Save')
save_button.pack(side=tk.RIGHT)

reset_button = ttk.Button(buttons, text='Reset')
reset_button.pack(side=tk.RIGHT)

status_variable = tk.StringVar()
ttk.Label(
    root, textvariable=status_variable
).grid(sticky=tk.W + tk.E, row=99, padx=10)


def on_reset():
    """Called when reset button is clicked, or after save"""
    for variable in variables.values():
        if isinstance(variable, tk.BooleanVar):
            variable.set(False)
        else:
            variable.set('')
    notes_inp.delete('1.0', tk.END)

reset_button.configure(command=on_reset)


def on_save():
    '''Handle ave button clicks'''
    global records_saved
    datestring = datetime.today().strftime("%Y-%m-%d")
    filename = f"abq_data_record_{datestring}.csv"
    newfile = not Path(filename).exists()
    data = dict()
    fault = variables['Equipment Fault'].get()
    for key, variable in variables.items():
        if fault and key in ('Light', 'Humidity', 'Temperature'):
            data[key] = ''
        else:
            try:
                data[key] = variable.get()
            except tk.TclError:
                status_variable.set(
                    f'Error in field: {key}. Data was not saved!'
                )
                return
    data['Notes'] = notes_inp.get('1.0', tk.END)
    with open(filename, 'a', newline='') as fh:
        csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
        if newfile:
            csvwriter.writeheader()
        csvwriter.writerow(data)
    records_saved += 1
    status_variable.set(
        f"{records_saved} records saved this session"
    )
    on_reset()

save_button.configure(command=on_save)
on_reset()
root.mainloop()