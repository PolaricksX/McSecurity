import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from password_manager.password_manager import PasswordManager
from password_manager.password_strength import REQUIREMENTS, is_strong_password
import os


class PasswordManagerUI:
    """GUI for the Password Manager using tkinter."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Password Manager")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.pm = None
        self.master_password_set = False
        
        # Set style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Initialize login screen
        self.show_login_screen()
    
    def show_login_screen(self):
        """Display the master password login screen."""
        self.clear_window()
        
        frame = ttk.Frame(self.root, padding="20")
        frame.pack(expand=True)
        
        # Title
        title = ttk.Label(frame, text="Password Manager", font=("Helvetica", 24, "bold"))
        title.pack(pady=20)
        
        # Instructions
        instructions = ttk.Label(
            frame, 
            text="Enter your master password to access your passwords.",
            font=("Helvetica", 10)
        )
        instructions.pack(pady=10)
        
        # Master password input
        ttk.Label(frame, text="Master Password:").pack(pady=5)
        self.master_password_var = tk.StringVar()
        password_entry = ttk.Entry(frame, textvariable=self.master_password_var, show="*", width=30)
        password_entry.pack(pady=5)
        password_entry.focus()
        
        # Login button
        login_btn = ttk.Button(frame, text="Login", command=self.login)
        login_btn.pack(pady=20)
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: self.login())
    
    def login(self):
        """Authenticate with master password."""
        master_password = self.master_password_var.get()
        
        if not master_password:
            messagebox.showwarning("Input Error", "Please enter a master password.")
            return

        new_account = not (os.path.exists("encryption.key") or os.path.exists("passwords.json"))
        if new_account:
            if not is_strong_password(master_password):
                messagebox.showwarning("Weak Master Password", REQUIREMENTS)
                return
            messagebox.showinfo("Master Password", "Password meets strength requirements.")
        
        try:
            self.pm = PasswordManager(master_password)
            self.show_main_screen()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize password manager: {str(e)}")
    
    def show_main_screen(self):
        """Display the main password manager interface."""
        self.clear_window()
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = ttk.Label(main_frame, text="Your Passwords", font=("Helvetica", 18, "bold"))
        title.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        add_btn = ttk.Button(button_frame, text="+ Add Password", command=self.show_add_password_dialog)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(button_frame, text="Delete Selected", command=self.delete_password)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        view_btn = ttk.Button(button_frame, text="View Password", command=self.view_password)
        view_btn.pack(side=tk.LEFT, padx=5)
        
        logout_btn = ttk.Button(button_frame, text="Logout", command=self.logout)
        logout_btn.pack(side=tk.RIGHT, padx=5)
        
        # Listbox frame
        list_frame = ttk.LabelFrame(main_frame, text="Stored Services", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.services_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10)
        )
        self.services_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.services_listbox.yview)
        
        # Bind double-click to view password
        self.services_listbox.bind('<Double-Button-1>', lambda e: self.view_password())
        
        # Refresh list
        self.refresh_services_list()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set(f"Total passwords: {len(self.pm.get_all_services())}")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def refresh_services_list(self):
        """Refresh the listbox with all services."""
        self.services_listbox.delete(0, tk.END)
        services = self.pm.get_all_services()
        for service in sorted(services):
            self.services_listbox.insert(tk.END, service)
    
    def show_add_password_dialog(self):
        """Show dialog to add a new password."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Password")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Service
        ttk.Label(frame, text="Service Name:").pack(anchor=tk.W, pady=5)
        service_var = tk.StringVar()
        service_entry = ttk.Entry(frame, textvariable=service_var, width=30)
        service_entry.pack(fill=tk.X, pady=5)
        
        # Username
        ttk.Label(frame, text="Username/Email:").pack(anchor=tk.W, pady=5)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(frame, textvariable=username_var, width=30)
        username_entry.pack(fill=tk.X, pady=5)
        
        # Password
        ttk.Label(frame, text="Password:").pack(anchor=tk.W, pady=5)
        password_var = tk.StringVar()
        password_entry = ttk.Entry(frame, textvariable=password_var, width=30, show="*")
        password_entry.pack(fill=tk.X, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        def save_password():
            service = service_var.get().strip()
            username = username_var.get().strip()
            password = password_var.get()
            
            if not all([service, username, password]):
                messagebox.showwarning("Input Error", "Please fill in all fields.")
                return
            
            if self.pm.service_exists(service):
                if not messagebox.askyesno("Confirm", f"'{service}' already exists. Overwrite?"):
                    return

            if is_strong_password(password):
                messagebox.showinfo("Password Strength", "Password meets strength requirements.")
            else:
                messagebox.showinfo(
                    "Password Strength",
                    f"Weak password; changing it is optional. {REQUIREMENTS}",
                )

            try:
                self.pm.add_password(service, username, password)
                messagebox.showinfo("Success", f"Password for '{service}' saved successfully!")
                dialog.destroy()
                self.refresh_services_list()
                self.status_var.set(f"Total passwords: {len(self.pm.get_all_services())}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save password: {str(e)}")
        
        ttk.Button(button_frame, text="Save", command=save_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def view_password(self):
        """View the selected password."""
        selection = self.services_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a service.")
            return
        
        service = self.services_listbox.get(selection[0])
        username, password = self.pm.get_password(service)
        
        if username is None:
            messagebox.showerror("Error", password)
            return
        
        # Create a new window to display password
        view_window = tk.Toplevel(self.root)
        view_window.title(f"Password for {service}")
        view_window.geometry("400x180")
        view_window.resizable(False, False)
        
        frame = ttk.Frame(view_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Service name
        ttk.Label(frame, text=f"Service: {service}", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        # Username
        ttk.Label(frame, text=f"Username: {username}").pack(anchor=tk.W, pady=5)
        
        # Password (initially hidden)
        password_frame = ttk.Frame(frame)
        password_frame.pack(anchor=tk.W, pady=5, fill=tk.X)
        
        ttk.Label(password_frame, text="Password:").pack(side=tk.LEFT)
        
        self.password_shown = False
        password_var = tk.StringVar()
        password_var.set("••••••••")
        
        password_display = ttk.Label(password_frame, textvariable=password_var, font=("Courier", 10))
        password_display.pack(side=tk.LEFT, padx=10)
        
        def toggle_password():
            if self.password_shown:
                password_var.set("••••••••")
                self.password_shown = False
            else:
                password_var.set(password)
                self.password_shown = True
        
        ttk.Button(password_frame, text="Show", command=toggle_password).pack(side=tk.LEFT)
        
        # Copy button
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        
        ttk.Button(frame, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=10)
    
    def delete_password(self):
        """Delete the selected password."""
        selection = self.services_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Error", "Please select a service to delete.")
            return
        
        service = self.services_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{service}'?"):
            self.pm.delete_password(service)
            self.refresh_services_list()
            self.status_var.set(f"Total passwords: {len(self.pm.get_all_services())}")
            messagebox.showinfo("Success", f"'{service}' has been deleted.")
    
    def logout(self):
        """Logout and return to login screen."""
        self.pm = None
        self.show_login_screen()
    
    def clear_window(self):
        """Clear all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = PasswordManagerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
