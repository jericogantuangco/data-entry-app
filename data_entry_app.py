'''The ABQ Data Entry application'''
from cgitb import text
from datetime import datetime
from operator import truediv
from pathlib import Path
import csv
from re import L
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk

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
            var=self._vars['Blossoms'],
            input_args={'from_': 0, 'to': 1000}
        ).grid(row=0, column=1)
        LabelInput(
            p_info, 'Fruit', input_class=ttk.Spinbox,
            var=self._vars['Fruit'],
            input_args={'from_': 0, 'to': 1000}
        ).grid(row=0, column=2)
        LabelInput(
            p_info, 'Min Height (cm)',
            input_class=ttk.Spinbox, var=self._vars['Min Height'],
            input_args={'from_': 0, 'to': 1000, 'increment': .01}
        ).grid(row=1, column=0)
        LabelInput(
            p_info, 'Max Height (cm)', input_class=ttk.Spinbox,
            var=self._vars['Max Height'],
            input_args={'from_': 0, 'to': 1000, 'increment': .01}
        ).grid(row=1, column=1)
        LabelInput(
            p_info, 'Median Height (cm)', input_class=ttk.Spinbox,
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
        self.resetbutton.pack(side=tk.RIGHT)

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


class ValidatedMixin:
    """Adds a validation functionality to an input widget"""
    
    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)
        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)
        self.configure(
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _toggle_error(self, on=False):
        self.configure(foreground=('red' if on else 'black'))

    def _validate(self, proposed, current, char, event, index, action):
        self.error.set('')
        self._toggle_error()
        valid = True
        state = str(self.configure('state')[-1])
        if state == tk.DISABLED:
            return valid
        if event == 'focusout':
            valid = self._focusout_validate(event=event)
        elif event == 'key':
            valid = self._key_validate(
                propsed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )
        return valid

    def _focusout_validate(self, **kwargs):
        return True

    def _key_validate(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(
                proposed=proposed,
                current=current,
                char=char,
                event=event,
                index=index,
                action=action
            )

    def _focusout_invalid(self, **kwargs):
        """Handle invalid data on a focus event"""
        self._toggle_error(True)

    def _key_invalid(self, **kwargs):
        """
        Handle invalid ata on a key event. By default we want to do nothing
        """

    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid

class RequiredEntry(ValidatedMixin, ttk.Entry):
    """An Entry that requires a value"""
    
    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid

class DateEntry(ValidatedMixin, ttk.Entry):
    """An Entry that only accepts ISO Date strings"""

    def _key_validate(self, action, index, char, **kwargs):
        valid = True
        if action == '0':
            valid = True
        elif index in ('0', '1', '2' , '3', '5', '6' ,'8' ,'9'):
            valid = char.isdigit()
        elif index in ('4', '7'):
            valid = char == '-'
        else:
            valid = False
        return valid

    def _focusout_validate(self, event):
        valid = True
        if not self.get():
            self.error.set('A value is required')
            valid = False
        try:
            datetime.strptime(self.get(), '%Y-%m-%d')
        except ValueError:
            self.error.set('Invalid date')
            valid = False
        return valid

    
class ValidatedCombobox(ValidatedMixin, ttk.Combobox):
    """A combox that only takes values from its string list"""
    def _key_validate(self, proposed, action, **kwargs):
        valid = True
        if action == '0':
            self.set('')
            return True
        values = self.cget('values')
        matching = [
            x for x in values
            if x.lower().startswith(proposed.lower())
        ]

        if len(matching) == 0:
            valid = False
        elif len(matching) == 1:
            self.set(matching[0])
            self.icursos(tk.END)
            valid = False
        return valid

    def _focusout_validate(self, **kwargs):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid

class Application(ThemedTk):
    """Application root window"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.overrideredirect(True)
        # self.geometry('600x600+100+100')
        # title_bar = ttk.Frame(self)
        # close_button = tk.Button(title_bar, text='X', command=self.destroy,bd=0)
        # window = tk.Canvas(self, bg='#eff0f1')

        # title_bar.pack(expand=1, fill=tk.X)
        # close_button.pack(side=tk.RIGHT)
        # window.pack(expand=1, fill=tk.BOTH)
        
        # title_bar.bind('<B1-Motion>', self._move_window)

        self.title('ABQ Data Entry Application')
        self.columnconfigure(0, weight=1)
        
        ttk.Label(
            self, text='ABQ Data Entry Application',
            font=('TkDefaultFont', 16)
        ).grid(row=0)
        self.recordform = DataRecordForm(self)
        self.recordform.grid(row=1, padx=10, sticky=(tk.E + tk.W))
        self.status = tk.StringVar()
        self.s = ttk.Style()
        
        self.s.theme_use('breeze')
        self.tk.call('ttk::style', 'configure', 'TButton', '-background', 'green')
        # print(self.s.theme_names())
        # print(self.s.theme_use('yaru'))
        ttk.Label(
            self, textvariable=self.status,
        ).grid(row=2, padx=10,sticky=(tk.E + tk.W))
        self._records_saved = 0

    def _on_save(self):
        """Handles save button clicks"""
        datestring = datetime.today().strftime('%Y-%m-%d')
        filename = f'abq_data_record_{datestring}.csv'
        newfile = not Path(filename).exists()
        try:
            data = self.recordform.get()
        except ValueError as e:
            self.status.set(str(e))
            return
        with open(filename, 'a', newline='') as fh:
            csvwriter = csv.DictWriter(fh, fieldnames=data.keys())
            if newfile:
                csvwriter.writeheader()
            csvwriter.writerow(data)
        self._records_saved += 1
        self.status.set(
            f'{self._records_saved} records saved this session.'
        )
        self.recordform.reset()

    def _move_window(self, event):
        self.geometry('+{0}+{1}'.format(event.x_root, event.y_root))

if __name__ == '__main__':
    run = Application()
    run.mainloop()