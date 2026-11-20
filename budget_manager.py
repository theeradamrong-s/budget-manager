import tkinter as tk
from tkinter import ttk, messagebox
import turtle
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class Transaction:
    def __init__(self, account_name, account_type, amount, category, t_type):
        self.account_name = account_name
        self.account_type = account_type
        self.amount = amount
        self.category = category
        self.type = t_type
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"{self.timestamp} | {self.account_name} | {self.account_type} | {self.type} | {self.category} | ${self.amount:.2f}"


class Account:
    def __init__(self, name, acc_type):
        self.name = name
        self.type = acc_type
        self.transactions = []
        self.total = 0

    def add_transaction(self, transaction):
        self.transactions.append(transaction)


#Page Base
class Page(tk.Frame):
    #Base Class
    def __init__(self, master, app):
        super().__init__(master)
        self.master = master
        self.app = app

    def show(self):
        self.lift()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()


#Page Inheritance
class AccountPage(Page):
    def build_ui(self):
        self.clear()
        tk.Label(self, text="Select or Create Account", font=("Arial", 18, "bold")).pack(pady=20)

        if self.app.accounts:
            tk.Label(self, text="Choose Existing Account:").pack(pady=5)
            self.existing_account_var = tk.StringVar()
            account_names = [f"{acc.name} ({acc.type})" for acc in self.app.accounts]
            self.existing_account_menu = ttk.Combobox(
                self, textvariable=self.existing_account_var, values=account_names, state="readonly"
            )
            self.existing_account_menu.pack(pady=5)
            tk.Button(self, text="Open Account", command=self.open_existing_account).pack(pady=10)
            ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        tk.Label(self, text="Create New Account", font=("Arial", 14, "bold")).pack(pady=5)
        tk.Label(self, text="Account Name:").pack()
        self.account_name_var = tk.StringVar()
        tk.Entry(self, textvariable=self.account_name_var).pack(pady=5)

        tk.Label(self, text="Account Type:").pack()
        self.account_type_var = tk.StringVar()
        ttk.Combobox(self, textvariable=self.account_type_var,
                     values=["Personal Account", "Business Account"], state="readonly").pack(pady=5)

        tk.Button(self, text="Create", command=self.create_account).pack(pady=15)

    def create_account(self):
        name = self.account_name_var.get().strip()
        acc_type = self.account_type_var.get()
        if not name or not acc_type:
            messagebox.showerror("Error", "Please enter both name and account type.")
            return
        for acc in self.app.accounts:
            if acc.name == name and acc.type == acc_type:
                messagebox.showerror("Error", "Account already exists.")
                return
        account = Account(name, acc_type)
        self.app.accounts.append(account)
        self.app.current_account = account
        self.app.show_page("TransactionPage")

    def open_existing_account(self):
        selected = self.existing_account_var.get()
        if not selected:
            messagebox.showerror("Error", "Please select an account.")
            return
        for acc in self.app.accounts:
            display_name = f"{acc.name} ({acc.type})"
            if display_name == selected:
                self.app.current_account = acc
                self.app.show_page("TransactionPage")
                return


class TransactionPage(Page):
    def build_ui(self):
        self.clear()
        tk.Label(self, text=f"Account: {self.app.current_account.name} ({self.app.current_account.type})",
                 font=("Arial", 14, "bold")).pack(pady=10)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        if "Business" in self.app.current_account.type:
            types = ["Revenue", "Cost"]
        else:
            types = ["Income", "Expense"]
            
        tk.Label(frame, text="Type:").grid(row=0, column=0, padx=5)
        self.type_var = tk.StringVar(value=types[0])
        ttk.Combobox(frame, textvariable=self.type_var, values=types, state="readonly").grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Category:").grid(row=1, column=0, padx=5)
        self.category_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.category_var).grid(row=1, column=1, padx=5)

        tk.Label(frame, text="Amount:").grid(row=2, column=0, padx=5)
        self.amount_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.amount_var).grid(row=2, column=1, padx=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Add Transaction", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Bar Graph", command=self.app.show_bargraph).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Line Graph", command=self.app.show_linegraph).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Summary", command=lambda: self.app.show_page("SummaryPage")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Back", command=lambda: self.app.show_page("AccountPage")).pack(side=tk.LEFT, padx=5)

        self.trans_text = tk.Text(self, height=30, width=120)
        self.trans_text.pack(pady=30, padx=50)
        self.update_transaction_display()

    def add_transaction(self):
        try:
            amount = float(self.amount_var.get())
            if amount == 0:
                raise ValueError("Amount cannot be zero.")
            category = self.category_var.get()
            t_type = self.type_var.get()
            if not category:
                raise ValueError("Category cannot be empty.")
            if len(category) > 15:
                raise ValueError("Category is too long.")

            if t_type in ["Income", "Revenue"]:
                value = amount
            else:
                value = -amount
            self.app.current_account.total += value
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        tr = Transaction(self.app.current_account.name, self.app.current_account.type, amount, category, t_type)
        self.app.current_account.add_transaction(tr)
        self.update_transaction_display()
        self.amount_var.set("")
        self.category_var.set("")

    def update_transaction_display(self):
        self.trans_text.delete("1.0", "end")
        for tr in self.app.current_account.transactions:
            self.trans_text.insert("end", str(tr) + "\n")


class SummaryPage(Page):
    def build_ui(self):
        self.clear()
        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True)

        tk.Label(main_frame, text=f"Summary for {self.app.current_account.name}", font=("Arial", 16, "bold")).pack(pady=10)

        acc_type = self.app.current_account.type
        if "Business" in acc_type:
            total_revenue = sum(tr.amount for tr in self.app.current_account.transactions if tr.type == "Revenue")
            total_cost = sum(tr.amount for tr in self.app.current_account.transactions if tr.type == "Cost")
            profit = total_revenue - total_cost
            result_text = "Profit" if profit >= 0 else "Loss"
            tk.Label(main_frame, text=f"Total Revenue: ${total_revenue:.2f}", font=("Arial", 12)).pack(pady=5)
            tk.Label(main_frame, text=f"Total Cost: ${total_cost:.2f}", font=("Arial", 12)).pack(pady=5)
            tk.Label(main_frame, text=f"{result_text}: ${abs(profit):.2f}", font=("Arial", 12, "bold")).pack(pady=10)
        else:
            total_income = sum(tr.amount for tr in self.app.current_account.transactions if tr.type == "Income")
            total_expense = sum(tr.amount for tr in self.app.current_account.transactions if tr.type == "Expense")
            net_balance = total_income - total_expense
            tk.Label(main_frame, text=f"Total Income: ${total_income:.2f}", font=("Arial", 12)).pack(pady=5)
            tk.Label(main_frame, text=f"Total Expense: ${total_expense:.2f}", font=("Arial", 12)).pack(pady=5)
            tk.Label(main_frame, text=f"Net Balance: ${net_balance:.2f}", font=("Arial", 12, "bold")).pack(pady=10)

        #Category summary
        tk.Label(main_frame, text="By Category:", font=("Arial", 12, "underline")).pack(pady=5)
        categories = {}
        for tr in self.app.current_account.transactions:
            sign = 1 if tr.type in ["Income", "Revenue"] else -1
            categories[tr.category] = categories.get(tr.category, 0) + tr.amount * sign

        for cat, total in categories.items():
            color = "green" if total >= 0 else "red"
            tk.Label(main_frame, text=f"{cat}: ${total:.2f}", fg=color).pack()

        #Charts
        if self.app.current_account.transactions:
            cats = [tr.category for tr in self.app.current_account.transactions]
            fig_width = max(8, len(cats) * 0.8)
            fig_height = 4
            fig = Figure(figsize=(fig_width, fig_height), dpi=100)

            #Bar chart
            ax1 = fig.add_subplot(121)
            amts = [tr.amount if tr.type in ["Income", "Revenue"] else -tr.amount
                    for tr in self.app.current_account.transactions]
            ax1.bar(cats, amts, color=['green' if a >= 0 else 'red' for a in amts])
            ax1.set_title("Transactions")
            ax1.tick_params(axis='x', rotation=30, labelsize=7)

            #Line chart
            ax2 = fig.add_subplot(122)
            balance = 0
            balances = []
            for tr in self.app.current_account.transactions:
                value = tr.amount if tr.type in ["Income", "Revenue"] else -tr.amount
                balance += value
                balances.append(balance)
            ax2.plot(range(len(balances)), balances, marker='o', color='blue')
            ax2.set_title("Balance Trend")

            canvas = FigureCanvasTkAgg(fig, master=main_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=10)
            fig.tight_layout()

        tk.Button(main_frame, text="Back", command=lambda: self.app.show_page("TransactionPage")).pack(pady=15)


#Main App
class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Budget Tracker")
        self.root.geometry("1000x1000")
        self.current_account = None
        self.accounts = []

        self.pages = {}
        for PageClass in (AccountPage, TransactionPage, SummaryPage):
            page = PageClass(root, self)
            page.place(relwidth=1, relheight=1)
            self.pages[PageClass.__name__] = page

        self.show_page("AccountPage")

    def show_page(self, page_name):
        page = self.pages[page_name]
        if hasattr(page, "build_ui"):
            page.build_ui()
        page.show()

    def reset_turtle(self):
        try:
            turtle.bye()
        except:
            pass
        turtle.TurtleScreen._RUNNING = True

    def show_bargraph(self):
        if not self.current_account.transactions:
            messagebox.showinfo("Info", "No transactions to show.")
            return
        self.reset_turtle()
        screen = turtle.Screen()
        screen.title("Transaction Bar Graph")
        t = turtle.Turtle()
        t.speed(0)
        t.hideturtle()
        t.penup()
        y_base = -50
        x_start = -250
        max_height = 250
        
        max_amount = max(abs(tr.amount) for tr in self.current_account.transactions)
        scale = max_height / max_amount if max_amount != 0 else 1
        
        scale_bar = 4 * len(self.current_account.transactions) - 1
        bar_width = max(20, (540 * (3 / scale_bar)))
        spacing = max(10, (540 * (1 / scale_bar)))
        
        size = max(6, min(10, int(spacing / 3)))
        
        t.goto(x_start - 58, y_base + max_height + 20)
        t.write("Amount", align="center", font=("Arial", 15, "normal"))
        t.goto(x_start - 50, y_base + max_height)
        t.pendown()
        t.goto(x_start - 50, y_base - max_height)
        t.penup()
        t.goto(x_start - 50, y_base)
        t.pendown()
        t.forward(600)
        t.penup()
        t.forward(20)
        t.write("Time", align="center", font=("Arial", 15, "normal"))
        x = x_start-10
        for tr in self.current_account.transactions:
            if tr.type in ["Income", "Revenue"]:
                height = tr.amount * scale
                color = "green"
                time_mark = -20
                amount_mark = 10
                offset = -15
            else:
                height = -tr.amount * scale
                color = "red"
                time_mark = 10
                amount_mark = -20
                offset = 15
            t.goto(x, y_base)
            t.fillcolor(color)
            t.begin_fill()
            t.pendown()
            t.forward(bar_width)
            t.left(90)
            t.forward(height)
            t.left(90)
            t.forward(bar_width)
            t.left(90)
            t.forward(height)
            t.left(90)
            t.end_fill()
            t.penup()
            t.goto(x + bar_width / 2, y_base + time_mark)
            t.write(f"| {tr.category} |", align="center", font=("Arial", size, "normal"))
            t.goto(x + bar_width / 2, y_base + time_mark + offset)
            t.write(tr.timestamp.split(" ")[1], align="center", font=("Arial", 8, "normal"))
            t.goto(x + bar_width / 2, y_base + amount_mark + height)
            t.write(f"${tr.amount}", align="center", font=("Arial", 8, "normal"))
            x += bar_width + spacing
        screen.mainloop()

    def show_linegraph(self):
        if not self.current_account.transactions:
            messagebox.showinfo("Info", "No transactions to show.")
            return
        self.reset_turtle()
        screen = turtle.Screen()
        screen.title("Balance Line Graph")
        t = turtle.Turtle()
        t.speed(0)
        t.hideturtle()
        t.penup()
        balance = 0
        balances = []
        for tr in self.current_account.transactions:
            value = tr.amount if tr.type in ["Income", "Revenue"] else -tr.amount
            balance += value
            balances.append(balance)
        max_balance = max(balances)
        min_balance = min(balances)
        max_height = 250
        y_scale = max_height / max(abs(max_balance), abs(min_balance), 1)
        x_start = -250
        y_base = 0
        offset = 20
        x_step = 600 / len(self.current_account.transactions)
        
        
        t.goto(x_start - 50, y_base)
        t.pendown()
        t.forward(600)
        t.penup()
        t.goto(x_start - 50, y_base + max_height)
        t.pendown()
        t.goto(x_start - 50, y_base - max_height)
        t.penup()
        prev_x, prev_y = None, None
        x = x_start
        for i, bal in enumerate(balances):
            tr = self.current_account.transactions[i]
            y = bal * y_scale
            if prev_x is not None:
                color = "green" if prev_y < y else "red"
            else:
                color = "green" if bal > 0 else "red"
            t.color(color)
            if prev_x is not None:
                t.goto(prev_x, prev_y)
                t.pendown()
                t.goto(x, y)
                t.penup()
            else:
                t.goto(x_start - 50, y_base)
                t.pendown()
                t.goto(x, y)
                t.penup()
            t.penup()
            t.goto(x, y + 10)
            t.color("black")
            if color == "red":
                text1 = f"- ${tr.amount}"
                text2 = f"Total: ${bal:.2f}"
            else:
                text1 = f"+ ${tr.amount}"  
                text2 = f"Total: ${bal:.2f}"
            t.write(text2, align="center", font=("Arial", 8, "normal"))
            t.penup()
            t.goto(x, y + offset)
            t.write(text1, align="center", font=("Arial", 8, "normal"))
            prev_x, prev_y = x, y
            x += x_step
        screen.mainloop()

#Main
if __name__ == "__main__":
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", lambda e: [root.attributes("-fullscreen", False), root.geometry("1000x1000")])

    app = BudgetApp(root)
    root.mainloop()
