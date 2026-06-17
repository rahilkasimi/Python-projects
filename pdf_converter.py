#!/usr/bin/env python3
"""
PDF to Word Converter and Table Extractor
A GUI application using FreeSimpleGUI to convert PDFs to Word documents
and extract tables from PDFs into Excel files.
Uses pdfplumber for table extraction (no Java required).
"""

import os
import threading
import traceback
from datetime import datetime

import FreeSimpleGUI as sg
import pandas as pd
import pdfplumber
from pdf2docx import Converter


def convert_pdf_to_word(pdf_path, docx_path, status_key, window):
    """Convert PDF to Word using pdf2docx."""
    try:
        window[status_key].update("Converting...", text_color="yellow")
        cv = Converter(pdf_path)
        cv.convert(docx_path)
        cv.close()
        return True, "Conversion successful!"
    except Exception as e:
        error_msg = f"Error converting PDF to Word: {str(e)}\n{traceback.format_exc()}"
        return False, error_msg


def extract_tables_to_excel(pdf_path, excel_path, status_key, window):
    """Extract tables from PDF to Excel using pdfplumber (no Java required)."""
    try:
        window[status_key].update("Extracting...", text_color="yellow")
        all_tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        # Convert table to DataFrame
                        df = pd.DataFrame(table[1:], columns=table[0] if table[0] else None)
                        all_tables.append(df)
        
        if not all_tables:
            return False, "No tables found in the PDF."
        
        # Write all tables to Excel, each on a separate sheet
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for i, df in enumerate(all_tables):
                sheet_name = f"Table_{i+1}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return True, f"Successfully extracted {len(all_tables)} table(s) to Excel."
    except Exception as e:
        error_msg = f"Error extracting tables: {str(e)}\n{traceback.format_exc()}"
        return False, error_msg


def main():
    sg.theme('DarkBlue3')

    layout = [
        [sg.Text("PDF to Word & Table Extractor", font=("Helvetica", 16, "bold"))],
        [sg.HorizontalSeparator()],
        
        # PDF to Word Section
        [sg.Text("PDF to Word Converter", font=("Helvetica", 12, "bold"))],
        [sg.Text("Select PDF:"), 
         sg.Input(key="-PDF_PATH_WORD-", enable_events=True), 
         sg.FileBrowse(file_types=(("PDF Files", "*.pdf"),))],
        [sg.Text("Save Word As:"), 
         sg.Input(key="-DOCX_PATH-"), 
         sg.FileSaveAs(file_types=(("Word Files", "*.docx"),), key="-BROWSE_DOCX-")],
        [sg.Button("Convert to Word", key="-CONVERT_WORD-"), 
         sg.Text("", key="-STATUS_WORD-", size=(40, 1))],
        
        [sg.HorizontalSeparator()],
        
        # Table Extraction Section
        [sg.Text("Extract Tables to Excel", font=("Helvetica", 12, "bold"))],
        [sg.Text("Select PDF:"), 
         sg.Input(key="-PDF_PATH_EXCEL-", enable_events=True), 
         sg.FileBrowse(file_types=(("PDF Files", "*.pdf"),), key="-BROWSE_PDF_EXCEL-")],
        [sg.Text("Save Excel As:"), 
         sg.Input(key="-EXCEL_PATH-"), 
         sg.FileSaveAs(file_types=(("Excel Files", "*.xlsx"),), key="-BROWSE_EXCEL-")],
        [sg.Button("Extract Tables", key="-EXTRACT_TABLES-"), 
         sg.Text("", key="-STATUS_EXCEL-", size=(40, 1))],
        
        [sg.HorizontalSeparator()],
        [sg.Button("Exit")]
    ]

    window = sg.Window("PDF Tools", layout, finalize=True)

    def auto_fill_output(input_key, output_key, extension):
        """Auto-fill output path based on input path."""
        input_path = window[input_key].get()
        if input_path and os.path.isfile(input_path):
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            dir_name = os.path.dirname(input_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(dir_name, f"{base_name}_{timestamp}{extension}")
            window[output_key].update(output_path)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == "Exit":
            break

        # Auto-fill output paths when input changes
        if event == "-PDF_PATH_WORD-":
            auto_fill_output("-PDF_PATH_WORD-", "-DOCX_PATH-", ".docx")
        elif event == "-PDF_PATH_EXCEL-":
            auto_fill_output("-PDF_PATH_EXCEL-", "-EXCEL_PATH-", ".xlsx")

        # Convert to Word
        if event == "-CONVERT_WORD-":
            pdf_path = values["-PDF_PATH_WORD-"]
            docx_path = values["-DOCX_PATH-"]

            if not pdf_path or not os.path.isfile(pdf_path):
                sg.popup_error("Please select a valid PDF file.")
                continue
            if not docx_path:
                sg.popup_error("Please specify an output Word file path.")
                continue

            window["-STATUS_WORD-"].update("Converting...", text_color="yellow")
            window["-CONVERT_WORD-"].update(disabled=True)

            def thread_convert_word():
                success, message = convert_pdf_to_word(pdf_path, docx_path, "-STATUS_WORD-", window)
                color = "green" if success else "red"
                window["-STATUS_WORD-"].update(message, text_color=color)
                window["-CONVERT_WORD-"].update(disabled=False)
                if success:
                    sg.popup_yes_no(f"Success!\n{message}\n\nOpen output folder?", title="Conversion Complete")
            
            threading.Thread(target=thread_convert_word, daemon=True).start()

        # Extract Tables
        if event == "-EXTRACT_TABLES-":
            pdf_path = values["-PDF_PATH_EXCEL-"]
            excel_path = values["-EXCEL_PATH-"]

            if not pdf_path or not os.path.isfile(pdf_path):
                sg.popup_error("Please select a valid PDF file.")
                continue
            if not excel_path:
                sg.popup_error("Please specify an output Excel file path.")
                continue

            window["-STATUS_EXCEL-"].update("Extracting...", text_color="yellow")
            window["-EXTRACT_TABLES-"].update(disabled=True)

            def thread_extract_tables():
                success, message = extract_tables_to_excel(pdf_path, excel_path, "-STATUS_EXCEL-", window)
                color = "green" if success else "red"
                window["-STATUS_EXCEL-"].update(message, text_color=color)
                window["-EXTRACT_TABLES-"].update(disabled=False)
                if success:
                    sg.popup_yes_no(f"Success!\n{message}\n\nOpen output folder?", title="Extraction Complete")

            threading.Thread(target=thread_extract_tables, daemon=True).start()

    window.close()


if __name__ == '__main__':
    main()
