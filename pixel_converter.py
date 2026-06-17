#!/usr/bin/env python3
"""
Pixel Converter Application
Converts pixels to various physical measurements and vice versa.

Key Parameters for Conversion:
1. DPI/PPI (Dots/Pixels Per Inch): The resolution of the display or output device
2. PPI is used for screens/displays, DPI for printers

Supported Measurements:
- Pixels (px)
- Inches (in)
- Centimeters (cm)
- Millimeters (mm)
- Points (pt) - 1/72 inch, used in typography
- Picas (pc) - 1/6 inch, used in typography
- Twips - 1/1440 inch, used in Windows GDI
- Meters (m)
- Feet (ft)
- Yards (yd)
"""

import FreeSimpleGUI as sg


def create_layout():
    """Create the GUI layout."""
    # Define the input fields
    layout = [
        [sg.Text('Pixel Converter', font=('Helvetica', 20, 'bold'), justification='center')],
        [sg.HorizontalSeparator()],
        
        [sg.Text('DPI/PPI (Dots/Pixels Per Inch):', size=(30, 1))],
        [sg.InputText('96', key='-DPI-', size=(20, 1), tooltip='Standard screen DPI is 96. Print is usually 300.')],
        [sg.Text('Common presets:', font=('Helvetica', 9)), 
         sg.Button('Screen 72', size=(10, 1)), 
         sg.Button('Screen 96', size=(10, 1)), 
         sg.Button('Print 300', size=(10, 1)), 
         sg.Button('Retina 144', size=(10, 1))],
        
        [sg.HorizontalSeparator()],
        
        [sg.Text('Enter value and select unit:', font=('Helvetica', 11, 'bold'))],
        [sg.InputText(key='-VALUE-', size=(20, 1), tooltip='Enter the numeric value to convert')],
        [sg.Combo([
            'Pixels (px)',
            'Inches (in)',
            'Centimeters (cm)',
            'Millimeters (mm)',
            'Points (pt)',
            'Picas (pc)',
            'Twips',
            'Meters (m)',
            'Feet (ft)',
            'Yards (yd)'
        ], default_value='Pixels (px)', key='-FROM_UNIT-', size=(25, 12), readonly=True)],
        
        [sg.Button('Convert', button_color=('white', 'blue'), size=(15, 1))],
        
        [sg.HorizontalSeparator()],
        
        [sg.Text('Conversion Results:', font=('Helvetica', 11, 'bold'))],
        [sg.Multiline(key='-OUTPUT-', size=(60, 15), disabled=True, background_color='white')],
        
        [sg.HorizontalSeparator()],
        
        [sg.Button('Clear', size=(10, 1)), sg.Button('Exit', size=(10, 1))]
    ]
    
    return layout


def convert_pixels_to_unit(pixels, dpi, unit):
    """Convert pixels to the specified unit."""
    # First convert pixels to inches
    inches = pixels / dpi
    
    conversions = {
        'Pixels (px)': pixels,
        'Inches (in)': inches,
        'Centimeters (cm)': inches * 2.54,
        'Millimeters (mm)': inches * 25.4,
        'Points (pt)': inches * 72,
        'Picas (pc)': inches * 6,
        'Twips': inches * 1440,
        'Meters (m)': inches * 0.0254,
        'Feet (ft)': inches / 12,
        'Yards (yd)': inches / 36
    }
    
    return conversions.get(unit, None)


def convert_unit_to_pixels(value, from_unit, dpi):
    """Convert from a specified unit to pixels."""
    # First convert to inches, then to pixels
    if from_unit == 'Pixels (px)':
        return value
    elif from_unit == 'Inches (in)':
        inches = value
    elif from_unit == 'Centimeters (cm)':
        inches = value / 2.54
    elif from_unit == 'Millimeters (mm)':
        inches = value / 25.4
    elif from_unit == 'Points (pt)':
        inches = value / 72
    elif from_unit == 'Picas (pc)':
        inches = value / 6
    elif from_unit == 'Twips':
        inches = value / 1440
    elif from_unit == 'Meters (m)':
        inches = value / 0.0254
    elif from_unit == 'Feet (ft)':
        inches = value * 12
    elif from_unit == 'Yards (yd)':
        inches = value * 36
    else:
        return None
    
    # Convert inches to pixels
    pixels = inches * dpi
    return pixels


def perform_conversion(values, from_unit, dpi):
    """Perform the conversion and return formatted results."""
    try:
        value = float(values['-VALUE-'])
        dpi = float(values['-DPI-'])
        
        if dpi <= 0:
            return "Error: DPI must be a positive number."
        
        # Convert input to pixels first
        pixels = convert_unit_to_pixels(value, from_unit, dpi)
        
        if pixels is None:
            return "Error: Invalid unit selected."
        
        # Generate all conversions
        results = []
        units = [
            ('Pixels', 'px'),
            ('Inches', 'in'),
            ('Centimeters', 'cm'),
            ('Millimeters', 'mm'),
            ('Points', 'pt'),
            ('Picas', 'pc'),
            ('Twips', ''),
            ('Meters', 'm'),
            ('Feet', 'ft'),
            ('Yards', 'yd')
        ]
        
        results.append(f"Input: {value} {from_unit}")
        results.append(f"DPI/PPI: {dpi}")
        results.append("=" * 40)
        results.append("")
        
        for unit_name, unit_symbol in units:
            full_unit = f"{unit_name} ({unit_symbol})" if unit_symbol else unit_name
            converted_value = convert_pixels_to_unit(pixels, dpi, full_unit)
            if converted_value is not None:
                if abs(converted_value) < 0.0001 or abs(converted_value) > 10000:
                    results.append(f"{unit_name:15}: {converted_value:.6e} {unit_symbol}")
                else:
                    results.append(f"{unit_name:15}: {converted_value:.6f} {unit_symbol}")
        
        return "\n".join(results)
        
    except ValueError:
        return "Error: Please enter a valid numeric value."
    except Exception as e:
        return f"Error: {str(e)}"


def main():
    """Main function to run the application."""
    sg.theme('LightBlue2')
    
    window = sg.Window('Pixel Converter', create_layout(), resizable=True)
    
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        if event == 'Convert':
            if not values['-VALUE-']:
                sg.popup_error('Please enter a value to convert.')
            else:
                result = perform_conversion(values, values['-FROM_UNIT-'], values['-DPI-'])
                window['-OUTPUT-'].update(result)
        
        if event == 'Clear':
            window['-VALUE-'].update('')
            window['-OUTPUT-'].update('')
            window['-DPI-'].update('96')
            window['-FROM_UNIT-'].update('Pixels (px)')
        
        # DPI preset buttons
        if event == 'Screen 72':
            window['-DPI-'].update('72')
        elif event == 'Screen 96':
            window['-DPI-'].update('96')
        elif event == 'Print 300':
            window['-DPI-'].update('300')
        elif event == 'Retina 144':
            window['-DPI-'].update('144')
    
    window.close()


if __name__ == '__main__':
    main()
