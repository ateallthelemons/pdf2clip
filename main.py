#!/usr/bin/env python3

import io
import sys
import fitz
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
from Cocoa import NSPasteboard, NSPasteboardTypePNG, NSData


class ToolTip:
    def __init__(self, widget, textfunc, delay_ms=200):
        self.widget = widget
        self.textfunc = textfunc
        self.delay_ms = delay_ms
        self.tipwindow = None
        widget.bind("<Enter>", self._schedule_show)
        widget.bind("<Leave>", self._hide)

    def _schedule_show(self, _):
        self.widget.after(self.delay_ms, self._show)

    def _show(self):
        if self.tipwindow or not self.widget.winfo_viewable():
            return
        text = self.textfunc()
        if not text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(
            tw,
            text=text,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            padx=4,
            pady=2,
        ).pack()

    def _hide(self, _=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


def copy_image_to_clipboard(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = NSData.dataWithBytes_length_(buf.getvalue(), buf.tell())
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.setData_forType_(data, NSPasteboardTypePNG)


def render_page(pdf_path, page_no):
    with fitz.open(pdf_path) as doc:
        if not (1 <= page_no <= len(doc)):
            raise ValueError(f"page {page_no} out of range (1–{len(doc)})")
        pix = doc.load_page(page_no - 1).get_pixmap(matrix=fitz.Matrix(2, 2))
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)


class App(tk.Tk):
    FLASH_MS = 1500

    def __init__(self):
        super().__init__()
        self.title("pdf2clip")
        self.resizable(False, False)
        self.pdf_path = tk.StringVar()
        self.num_pages = None
        self.last_copied = None

        tk.Button(self, text="select PDF…", command=self.choose_pdf).pack(pady=6)
        tk.Label(self, textvariable=self.pdf_path, wraplength=380).pack()

        row = tk.Frame(self)
        row.pack(pady=8)

        tk.Button(row, text="–", width=2, command=self.dec_page).pack(side=tk.LEFT)
        self.page_entry = tk.Entry(row, width=6, justify="center")
        self.page_entry.insert(0, "1")
        self.page_entry.pack(side=tk.LEFT, padx=4)
        tk.Button(row, text="+", width=2, command=self.inc_page).pack(side=tk.LEFT)

        self.page_label = tk.Label(self, text="1/? pages")
        self.page_label.pack()

        self.copy_btn = tk.Button(self, text="copy page to clipboard", command=self.copy_page)
        self.copy_btn.pack(pady=4)

        ToolTip(
            self.copy_btn,
            lambda: f"last copied page: {self.last_copied}"
            if self.last_copied is not None
            else "no page copied yet",
        )

        self.page_entry.bind("<KeyRelease>", lambda e: self.update_page_label())

    def choose_pdf(self):
        path = filedialog.askopenfilename(
            title="open PDF",
            filetypes=[("PDF files", "*.pdf"), ("all files", "*.*")],
        )
        if path:
            self.pdf_path.set(path)
            with fitz.open(path) as d:
                self.num_pages = len(d)
            self.set_page_int(1)
            self.update_page_label()

    def get_page_int(self):
        try:
            return max(1, int(self.page_entry.get()))
        except ValueError:
            return 1

    def set_page_int(self, value):
        self.page_entry.delete(0, tk.END)
        self.page_entry.insert(0, str(value))

    def update_page_label(self):
        current = self.get_page_int()
        total = self.num_pages if self.num_pages else "?"
        self.page_label.config(text=f"{current}/{total} pages")

    def inc_page(self):
        cur = self.get_page_int()
        if self.num_pages:
            cur = min(cur + 1, self.num_pages)
        else:
            cur += 1
        self.set_page_int(cur)
        self.update_page_label()

    def dec_page(self):
        self.set_page_int(max(1, self.get_page_int() - 1))
        self.update_page_label()

    def flash_copied(self):
        orig = self.copy_btn["text"]
        self.copy_btn.config(text="copied!", state=tk.DISABLED)
        self.after(self.FLASH_MS, lambda: self.copy_btn.config(text=orig, state=tk.NORMAL))

    def copy_page(self):
        if not self.pdf_path.get():
            messagebox.showerror("no PDF selected", "choose a PDF first.")
            return
        try:
            page_no = self.get_page_int()
            img = render_page(self.pdf_path.get(), page_no)
            copy_image_to_clipboard(img)
            self.last_copied = page_no
            self.flash_copied()
        except Exception as e:
            messagebox.showerror("error", str(e))


if __name__ == "__main__":
    if sys.platform != "darwin":
        sys.exit("this script is intended for macOS.")
    try:
        import Cocoa
    except ImportError:
        sys.exit("pyobjc not installed. run: pip install pyobjc-framework-AppKit")
    App().mainloop()