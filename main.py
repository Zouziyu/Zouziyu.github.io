import tkinter as tk
from tkinter import font

class Calculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#2d2d2d")

        self.expression = ""
        self.display_var = tk.StringVar()
        self.display_var.set("0")

        self._build_display()
        self._build_buttons()

    def _build_display(self):
        frame = tk.Frame(self.root, bg="#2d2d2d")
        frame.pack(padx=12, pady=(12, 8), fill="x")

        self.display = tk.Label(
            frame,
            textvariable=self.display_var,
            anchor="e",
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Helvetica", 28),
            padx=12,
            pady=8,
        )
        self.display.pack(fill="both")

    def _build_buttons(self):
        btn_frame = tk.Frame(self.root, bg="#2d2d2d")
        btn_frame.pack(padx=12, pady=(0, 12), fill="both", expand=True)

        buttons = [
            ("C",  0, 0, "#ff5252", "#ffffff"),
            ("÷", 0, 1, "#424242", "#ffffff"),
            ("×", 0, 2, "#424242", "#ffffff"),
            ("⌫", 0, 3, "#424242", "#ffffff"),
            ("7",  1, 0, "#424242", "#ffffff"),
            ("8",  1, 1, "#424242", "#ffffff"),
            ("9",  1, 2, "#424242", "#ffffff"),
            ("-",  1, 3, "#424242", "#ffffff"),
            ("4",  2, 0, "#424242", "#ffffff"),
            ("5",  2, 1, "#424242", "#ffffff"),
            ("6",  2, 2, "#424242", "#ffffff"),
            ("+",  2, 3, "#424242", "#ffffff"),
            ("1",  3, 0, "#424242", "#ffffff"),
            ("2",  3, 1, "#424242", "#ffffff"),
            ("3",  3, 2, "#424242", "#ffffff"),
            ("=",  3, 3, "#4caf50", "#ffffff"),
            ("0",  4, 0, "#424242", "#ffffff"),
            (".",  4, 2, "#424242", "#ffffff"),
        ]

        for i in range(5):
            btn_frame.rowconfigure(i, weight=1)
        for i in range(4):
            btn_frame.columnconfigure(i, weight=1)

        for (text, row, col, bg, fg) in buttons:
            colspan = 2 if text == "0" else 1
            btn = tk.Button(
                btn_frame,
                text=text,
                font=("Helvetica", 16),
                bg=bg,
                fg=fg,
                activebackground="#616161",
                activeforeground="#ffffff",
                borderwidth=0,
                cursor="pointinghand",
                command=lambda t=text: self._on_click(t),
            )
            btn.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=2, pady=2)

    def _on_click(self, char):
        if char == "C":
            self.expression = ""
            self.display_var.set("0")
        elif char == "⌫":
            self.expression = self.expression[:-1]
            self.display_var.set(self.expression if self.expression else "0")
        elif char == "=":
            self._evaluate()
        elif char == "×":
            self.expression += "*"
            self.display_var.set(self.expression)
        elif char == "÷":
            self.expression += "/"
            self.display_var.set(self.expression)
        else:
            self.expression += char
            self.display_var.set(self.expression)

    def _evaluate(self):
        try:
            result = eval(self.expression)
            if isinstance(result, float) and result == int(result):
                result = int(result)
            self.expression = str(result)
            self.display_var.set(self.expression)
        except Exception:
            self.display_var.set("Error")
            self.expression = ""

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    Calculator().run()
