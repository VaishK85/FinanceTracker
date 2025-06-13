import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Colors and fonts aligned with DEFAULT design guidelines
BG_COLOR = "#ffffff"  # Light background with lots of whitespace
CONTAINER_BG = "#f9fafb"  # Light card background
TEXT_PRIMARY = "#111827"  # Bold, elegant typography color for headlines and primaries
TEXT_SECONDARY = "#6b7280"  # Neutral gray for body text
BUTTON_BG = "#000000"  # Black button background
BUTTON_FG = "#ffffff"  # White button text
BUTTON_HOVER_BG = "#222222"  # Soft hover effect

FONT_HEADER = ("Inter", 48, "bold")       # Big headline font (48px+)
FONT_SUBHEADER = ("Inter", 20, "bold")   # Subheading font
FONT_BODY = ("Inter", 16)                 # Body text font (16-18px)
FONT_SMALL = ("Inter", 14)                # Smaller label font
FONT_MONO = ("Consolas", 12)              # Monospaced font for passbook

MAX_WIDTH = 1200
CARD_RADIUS = 12
CARD_SHADOW_COLOR = "#e5e7eb"

def round_rectangle(canvas, x1, y1, x2, y2, radius=CARD_RADIUS, **kwargs):
    # Draw a rectangle with rounded corners on a Tkinter Canvas
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

class BankAccount:
    def __init__(self, account_holder, balance=0.0, account_type='Savings'):
        self.account_holder = account_holder
        self.balance = balance
        self.account_type = account_type
        self.transactions = []

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.transactions.append(('Deposit', amount, datetime.now(), 'Completed'))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        self.transactions.append(('Withdrawal', amount, datetime.now(), 'Completed'))

    def transfer(self, amount, to_account):
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        now = datetime.now()
        self.transactions.append(('Transfer Sent', amount, now, 'Completed'))
        self.transactions.append(('Transfer Received', amount, now, 'Completed'))

    def info(self):
        return {
            'Account Holder': self.account_holder,
            'Account Type': self.account_type,
            'Balance': f"${self.balance:,.2f}"
        }

    def all_transactions(self):
        return self.transactions

class BankApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bank Account Management Dashboard")
        self.geometry("1100x750")
        self.minsize(900, 700)
        self.configure(bg=BG_COLOR)

        self.account = None
        container = tk.Frame(self, bg=BG_COLOR)
        container.pack(fill="both", expand=True)
        self.frames = {}

        for F in (LoginPage, Dashboard, PassbookPage, ThankYouPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def logout(self):
        if messagebox.askyesno("Logout Confirmation", "Are you sure you want to logout?"):
            self.account = None
            self.frames["Dashboard"].reset()
            self.frames["PassbookPage"].reset()
            self.frames["ThankYouPage"].reset()
            self.show_frame("LoginPage")

    def _get_initials(self, name):
        parts = name.strip().split()
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][0].upper()
        return (parts[0][0] + parts[-1][0]).upper()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        container = tk.Frame(self, bg=BG_COLOR)
        # Center container vertically and horizontally
        container.place(relx=0.5, rely=0.5, anchor="center")
        container.config(width=MAX_WIDTH//2, padx=40, pady=40)

        tk.Label(container, text="Welcome Back", font=FONT_HEADER, fg=TEXT_PRIMARY, bg=BG_COLOR).pack(pady=(0, 24))
        tk.Label(container, text="Enter your account details to login", font=FONT_BODY, fg=TEXT_SECONDARY, bg=BG_COLOR).pack(pady=(0, 32))

        tk.Label(container, text="Account Holder Name", font=FONT_SMALL, fg=TEXT_PRIMARY, bg=BG_COLOR).pack(anchor="w", pady=(0, 6))
        self.entry_name = ttk.Entry(container, font=FONT_BODY)
        self.entry_name.pack(fill='x', ipady=10, pady=(0,20))

        tk.Label(container, text="Account Type", font=FONT_SMALL, fg=TEXT_PRIMARY, bg=BG_COLOR).pack(anchor="w", pady=(0, 6))
        self.account_type_var = tk.StringVar()
        self.combo_type = ttk.Combobox(container, values=["Savings", "Checking", "Business"], state="readonly",
                                       textvariable=self.account_type_var, font=FONT_BODY)
        self.combo_type.current(0)
        self.combo_type.pack(fill='x', ipady=10, pady=(0,20))

        tk.Label(container, text="Initial Deposit", font=FONT_SMALL, fg=TEXT_PRIMARY, bg=BG_COLOR).pack(anchor="w", pady=(0, 6))
        self.entry_deposit = ttk.Entry(container, font=FONT_BODY)
        self.entry_deposit.pack(fill='x', ipady=10, pady=(0,32))

        btn_login = tk.Button(container, text="Login",
                              font=FONT_BODY, fg=BUTTON_FG, bg=BUTTON_BG,
                              activebackground=BUTTON_HOVER_BG, activeforeground=BUTTON_FG,
                              relief="flat", cursor="hand2", command=self.handle_login)
        btn_login.pack(fill="x", pady=(0,12), ipady=12)

    def handle_login(self):
        name = self.entry_name.get().strip()
        account_type = self.account_type_var.get()
        deposit_str = self.entry_deposit.get().strip()
        if not name:
            messagebox.showerror("Input Error", "Account Holder Name is required.")
            return
        if not deposit_str:
            messagebox.showerror("Input Error", "Initial Deposit is required.")
            return
        try:
            deposit = float(deposit_str)
            if deposit < 0:
                raise ValueError("Deposit must be positive.")
        except ValueError:
            messagebox.showerror("Input Error", "Initial Deposit must be a positive number.")
            return

        self.controller.account = BankAccount(name, deposit, account_type)
        self.entry_name.delete(0, tk.END)
        self.entry_deposit.delete(0, tk.END)
        self.combo_type.current(0)
        self.controller.frames["Dashboard"].setup()
        self.controller.show_frame("Dashboard")

class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller
        self.account = None

        header = tk.Frame(self, bg=BG_COLOR, height=80)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)

        tk.Label(header, text="Bank Account Manager", font=FONT_HEADER, fg=TEXT_PRIMARY, bg=BG_COLOR).pack(side='left', padx=32, pady=16)

        logout_btn = tk.Button(header, text="Logout", font=FONT_BODY, fg=BUTTON_FG, bg=BUTTON_BG,
                               activebackground=BUTTON_HOVER_BG, activeforeground=BUTTON_FG,
                               relief="flat", cursor="hand2", command=self.controller.logout)
        logout_btn.pack(side='right', padx=32, pady=18, ipadx=24, ipady=8)

        container = tk.Frame(self, bg=BG_COLOR)
        container.pack(fill='both', expand=True, padx=32, pady=16)

        # Left: Quick Actions Card
        self.actions_card = tk.Frame(container, bg=CONTAINER_BG, bd=0, relief="flat")
        self.actions_card.pack(side='left', fill='y', padx=(0, 32), ipadx=20, ipady=20)
        self.actions_card.config(highlightbackground="#e5e7eb", highlightthickness=1)

        tk.Label(self.actions_card, text="Quick Actions", font=FONT_SUBHEADER, fg=TEXT_PRIMARY, bg=CONTAINER_BG).pack(anchor='w', pady=(0, 24))

        self.buttons = {}
        btn_texts = ['Deposit', 'Withdraw', 'Transfer Funds']
        btn_commands = [self.open_deposit_popup, self.open_withdraw_popup, self.open_transfer_popup]

        for text, cmd in zip(btn_texts, btn_commands):
            btn = tk.Button(self.actions_card, text=text, font=FONT_BODY,
                            bg=BUTTON_BG, fg=BUTTON_FG, relief="flat",
                            activebackground=BUTTON_HOVER_BG, activeforeground=BUTTON_FG,
                            cursor="hand2", command=cmd)
            btn.pack(fill='x', pady=8, ipady=12)
            self.buttons[text] = btn

        # Center: Account Overview Card
        self.account_card = tk.Frame(container, bg=CONTAINER_BG, bd=0, relief="flat")
        self.account_card.pack(side='left', fill='both', expand=True, ipadx=20, ipady=20)
        self.account_card.config(highlightbackground="#e5e7eb", highlightthickness=1)

        tk.Label(self.account_card, text="Account Overview", font=FONT_SUBHEADER, fg=TEXT_PRIMARY, bg=CONTAINER_BG).pack(anchor='nw', pady=(0, 24))

        self.info_frame = tk.Frame(self.account_card, bg=CONTAINER_BG)
        self.info_frame.pack(anchor='nw')

        labels = ["Account Holder:", "Account Type:", "Balance:"]
        self.info_values = []
        for i, txt in enumerate(labels):
            tk.Label(self.info_frame, text=txt, font=FONT_BODY, fg=TEXT_SECONDARY, bg=CONTAINER_BG).grid(row=i, column=0, sticky='w', padx=20, pady=8)
            v = tk.Label(self.info_frame, text="", font=FONT_BODY, fg=TEXT_PRIMARY, bg=CONTAINER_BG)
            v.grid(row=i, column=1, sticky='w', pady=8)
            self.info_values.append(v)

        # Right: Transaction History Card
        self.txn_card = tk.Frame(container, bg=CONTAINER_BG, bd=0, relief="flat")
        self.txn_card.pack(side='left', fill='both', ipadx=20, ipady=20)
        self.txn_card.config(highlightbackground="#e5e7eb", highlightthickness=1)

        tk.Label(self.txn_card, text="Transaction History", font=FONT_SUBHEADER, fg=TEXT_PRIMARY, bg=CONTAINER_BG).pack(anchor='nw', padx=16, pady=(0, 16))

        columns = ("Type", "Amount", "Date", "Status")
        self.txn_table = ttk.Treeview(self.txn_card, columns=columns, show='headings', height=15)
        for col in columns:
            self.txn_table.heading(col, text=col)
            anchor = 'center' if col != "Amount" else 'e'
            self.txn_table.column(col, anchor=anchor, width=120 if col != "Amount" else 100)
        self.txn_table.pack(padx=16, pady=(0, 16), fill='both', expand=True)

        scrollbar = ttk.Scrollbar(self.txn_card, orient='vertical', command=self.txn_table.yview)
        self.txn_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Action Message Label
        self.action_msg_var = tk.StringVar()
        self.action_label = tk.Label(container, textvariable=self.action_msg_var,
                                     font=FONT_BODY, fg="#059669", bg=BG_COLOR, wraplength=MAX_WIDTH//3)
        self.action_label.pack(pady=8)

    def setup(self):
        self.account = self.controller.account
        info = self.account.info()
        for i, key in enumerate(["Account Holder", "Account Type", "Balance"]):
            self.info_values[i].config(text=info[key])
        self.refresh_transactions()
        self.clear_action_message()

    def reset(self):
        for v in self.info_values:
            v.config(text="")
        self.txn_table.delete(*self.txn_table.get_children())
        self.clear_action_message()

    def refresh_transactions(self):
        self.txn_table.delete(*self.txn_table.get_children())
        for t in reversed(self.account.all_transactions()):
            dt_str = t[2].strftime("%Y-%m-%d %H:%M:%S")
            self.txn_table.insert("", "end", values=(t[0], f"${t[1]:,.2f}", dt_str, t[3]))

    def clear_action_message(self):
        self.action_msg_var.set("")

    def set_action_message(self, msg):
        self.action_msg_var.set(msg)
        self.after(5000, self.clear_action_message)

    def open_deposit_popup(self):
        self._amount_popup("Deposit", self.do_deposit)

    def open_withdraw_popup(self):
        self._amount_popup("Withdraw", self.do_withdraw)

    def open_transfer_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Transfer Funds")
        popup.geometry("400x300")
        popup.configure(bg=BG_COLOR)
        popup.resizable(False, False)

        tk.Label(popup, text="Amount:", font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_COLOR).pack(anchor='w', padx=24, pady=(20, 6))
        amt_entry = ttk.Entry(popup, font=FONT_BODY)
        amt_entry.pack(ipady=8, padx=24, fill='x')

        tk.Label(popup, text="Recipient (Account Holder):", font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_COLOR).pack(anchor='w', padx=24, pady=(20, 6))
        rec_entry = ttk.Entry(popup, font=FONT_BODY)
        rec_entry.pack(ipady=8, padx=24, fill='x')

        def confirm():
            try:
                amt = float(amt_entry.get())
                recipient = rec_entry.get().strip()
                if amt <= 0 or not recipient:
                    raise ValueError
                self.account.transfer(amt, recipient)
                self.setup()
                self.set_action_message(f"➡️ Transferred ${amt:.2f} to {recipient}.")
                popup.destroy()
                self.controller.frames["PassbookPage"].setup()
                self.controller.show_frame("PassbookPage")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        btn = tk.Button(popup, text="Transfer", bg=BUTTON_BG, fg=BUTTON_FG,
                        activebackground=BUTTON_HOVER_BG, font=FONT_BODY,
                        relief="flat", cursor="hand2", command=confirm)
        btn.pack(pady=24, ipadx=20, ipady=10)

    def _amount_popup(self, action, callback):
        popup = tk.Toplevel(self)
        popup.title(action)
        popup.geometry("320x180")
        popup.configure(bg=BG_COLOR)
        popup.resizable(False, False)

        tk.Label(popup, text=f"{action} Amount:", font=FONT_BODY, fg=TEXT_PRIMARY, bg=BG_COLOR).pack(anchor="w", padx=24, pady=(24, 8))
        entry_amount = ttk.Entry(popup, font=FONT_BODY)
        entry_amount.pack(ipady=8, padx=24, fill='x')

        def confirm():
            try:
                amt = float(entry_amount.get())
                if amt <= 0:
                    raise ValueError
                callback(amt)
                popup.destroy()
            except Exception:
                messagebox.showerror("Input error", "Please enter a valid positive number.")

        btn = tk.Button(popup, text=action, bg=BUTTON_BG, fg=BUTTON_FG, font=FONT_BODY,
                        width=15, command=confirm, cursor="hand2")
        btn.pack(pady=24, ipadx=20, ipady=10)

    def do_deposit(self, amount):
        try:
            self.account.deposit(amount)
            self.setup()
            self.set_action_message(f"✅ Deposited ${amount:.2f} successfully.")
            self.controller.frames["PassbookPage"].setup()
            self.controller.show_frame("PassbookPage")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def do_withdraw(self, amount):
        try:
            if amount > self.account.balance:
                messagebox.showerror("Error", "Insufficient funds.")
                return
            self.account.withdraw(amount)
            self.setup()
            self.set_action_message(f"✅ Withdrew ${amount:.2f} successfully.")
            self.controller.frames["PassbookPage"].setup()
            self.controller.show_frame("PassbookPage")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class PassbookPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=CONTAINER_BG)
        self.controller = controller

        header = tk.Frame(self, bg=CONTAINER_BG, height=80)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        tk.Label(header, text="📖 Passbook Preview", font=FONT_HEADER, fg=TEXT_PRIMARY, bg=CONTAINER_BG).pack(side='left', padx=40, pady=20)

        btn_back = tk.Button(header, text="Back to Dashboard", bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", cursor="hand2",
                             activebackground=BUTTON_HOVER_BG, font=FONT_BODY,
                             command=lambda: controller.show_frame("Dashboard"))
        btn_back.pack(side='right', padx=40, pady=20)

        btn_next = tk.Button(header, text="Next ➡️", bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", cursor="hand2",
                             activebackground=BUTTON_HOVER_BG, font=FONT_BODY,
                             command=lambda: controller.show_frame("ThankYouPage"))
        btn_next.pack(side='right', pady=20, padx=(0, 16))

        self.canvas = tk.Canvas(self, width=950, height=600, bg="white", highlightthickness=0)
        self.canvas.pack(padx=40, pady=24)

        self._draw_card_background()

        self.sticker_canvas = tk.Canvas(self, width=100, height=100, bg=CONTAINER_BG, highlightthickness=0)
        self.sticker_canvas.place(relx=0.85, rely=0.7)
        self.draw_sticker()

    def _draw_card_background(self):
        round_rectangle(self.canvas, 5, 5, 945, 595, radius=CARD_RADIUS, fill='white', outline=CARD_SHADOW_COLOR, width=2)

    def draw_sticker(self):
        c = self.sticker_canvas
        size = 90
        padding = 5
        c.create_oval(padding, padding, size-padding, size-padding, fill=BUTTON_HOVER_BG, outline="")
        # Face: simple eyes and smile
        c.create_oval(25, 30, 35, 40, fill="white", outline="")
        c.create_oval(55, 30, 65, 40, fill="white", outline="")
        c.create_arc(25, 45, 65, 70, start=210, extent=120, style='arc', width=3, outline="white")

    def setup(self):
        self.account = self.controller.account
        self.draw_passbook()

    def draw_passbook(self):
        c = self.canvas
        c.delete("all")
        self._draw_card_background()
        if not self.account:
            return

        w = int(c['width'])
        h = int(c['height'])

        c.create_text(w // 2, 40, text="Passbook", font=("Inter", 28, "bold"), fill=TEXT_PRIMARY)

        headers = ["Date", "Type", "Amount", "Status"]
        positions = [80, 300, 600, 750]
        for pos, htext in zip(positions, headers):
            c.create_text(pos, 90, text=htext, font=("Inter", 14, "bold"), fill=TEXT_SECONDARY)

        y_start = 140
        line_h = 30
        max_entries = 15
        txns = self.account.all_transactions()[-max_entries:]
        y = y_start
        for t in reversed(txns):
            dt_str = t[2].strftime("%Y-%m-%d %H:%M")
            c.create_text(positions[0], y, text=dt_str, anchor='w', font=FONT_MONO, fill=TEXT_PRIMARY)
            c.create_text(positions[1], y, text=t[0], anchor='w', font=FONT_MONO, fill=TEXT_PRIMARY)
            c.create_text(positions[2], y, text=f"${t[1]:,.2f}", anchor='e', font=FONT_MONO, fill=TEXT_PRIMARY)
            c.create_text(positions[3], y, text=t[3], anchor='w', font=FONT_MONO, fill=TEXT_PRIMARY)
            y += line_h

        c.create_line(50, h-70, w-50, h-70, fill=TEXT_SECONDARY, width=2)
        c.create_text(w // 2, h-40, text="End of Passbook Preview", font=("Inter", 12, "italic"), fill=TEXT_SECONDARY)

    def reset(self):
        self.canvas.delete("all")

class ThankYouPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOR)
        self.controller = controller

        container = tk.Frame(self, bg=BG_COLOR)
        container.place(relx=0.5, rely=0.5, anchor="center")

        emoji_wave = "👋"
        emoji_star = "✨"

        self.thank_label = tk.Label(container, text=f"{emoji_wave} Thank you! {emoji_star}",
                                    font=("Inter", 36, "bold italic"), fg=BUTTON_BG, bg=BG_COLOR, wraplength=700, justify="center")
        self.thank_label.pack(pady=20)

        self.sticker_canvas = tk.Canvas(container, width=150, height=150, bg=BG_COLOR, highlightthickness=0)
        self.sticker_canvas.pack()

        # Decorative heart sticker shape
        self.sticker_canvas.create_oval(35, 20, 115, 105, fill=BUTTON_HOVER_BG, outline="")
        self.sticker_canvas.create_polygon(75, 110, 40, 60, 75, 30, 110, 58, fill="#e0e7ff", outline="")

        self.back_btn = tk.Button(container, text="Back to Dashboard", bg=BUTTON_BG, fg=BUTTON_FG,
                                  activebackground=BUTTON_HOVER_BG, activeforeground=BUTTON_FG,
                                  font=FONT_BODY, relief="flat", cursor="hand2",
                                  command=lambda: controller.show_frame("Dashboard"))
        self.back_btn.pack(pady=20, ipadx=30, ipady=12)

    def reset(self):
        pass

if __name__ == "__main__":
    app = BankApp()
    app.mainloop()
