import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import sys
import socket
import select
import time
from chat_utils import SERVER
from chat_server import Server

class ChatServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Server")
        self.root.geometry("700x500")
        
        # Server instance
        self.server = None
        self.server_running = False
        self.server_thread = None
        
        # Create main frame
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Server info frame
        self.info_frame = tk.LabelFrame(self.main_frame, text="Server Information", padx=5, pady=5)
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Server address display
        self.addr_label = tk.Label(self.info_frame, text=f"Server Address: {SERVER[0]}:{SERVER[1]}")
        self.addr_label.pack(anchor="w", pady=5)
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Stopped")
        self.status_label = tk.Label(self.info_frame, textvariable=self.status_var, fg="red")
        self.status_label.pack(anchor="w", pady=5)
        
        # Control buttons frame
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start Server Button
        self.start_btn = tk.Button(
            self.control_frame, 
            text="▶ Start Server", 
            command=self.start_server,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop Server Button
        self.stop_btn = tk.Button(
            self.control_frame,
            text="■ Stop Server",
            command=self.stop_server,
            state=tk.DISABLED,
            bg="#f44336",
            fg="white",
            padx=15,
            pady=5
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear Log Button
        self.clear_btn = tk.Button(
            self.control_frame,
            text="Clear Log",
            command=self.clear_log,
            padx=15,
            pady=5
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Log Frame
        self.log_frame = tk.LabelFrame(self.main_frame, text="Server Log", padx=5, pady=5)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Log Text Area with Scrollbar
        self.log_area = scrolledtext.ScrolledText(
            self.log_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Consolas', 10),
            state='disabled'
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Redirect stdout to log area
        sys.stdout = TextRedirector(self.log_area, "stdout")
    
    def log_message(self, message):
        """Add a message to the log area"""
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
    
    def clear_log(self):
        """Clear the log area"""
        self.log_area.configure(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state='disabled')
    
    def start_server(self):
        """Start the chat server in a separate thread"""
        if not self.server_running:
            try:
                self.server = Server()
                self.server_running = True
                
                # Start server in a separate thread
                self.server_thread = threading.Thread(
                    target=self.run_server, 
                    daemon=True
                )
                self.server_thread.start()
                
                # Update UI
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
                self.status_var.set(f"Status: Running on {SERVER[0]}:{SERVER[1]}")
                self.status_label.config(fg="green")
                self.log_message(f"[{time.strftime('%H:%M:%S')}] Server started on {SERVER[0]}:{SERVER[1]}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start server: {str(e)}")
                self.server_running = False
    
    def run_server(self):
        """Main server loop"""
        try:
            while self.server_running:
                try:
                    # Handle new connections and messages
                    read, write, error = select.select(
                        self.server.all_sockets, [], []) if self.server_running else ([], [], [])
                    
                    for sock in read:
                        if sock == self.server.server:
                            # New connection
                            sock, addr = self.server.server.accept()
                            self.server.new_client(sock)
                            self.log_message(f"[{time.strftime('%H:%M:%S')}] New client connected: {addr[0]}:{addr[1]}")
                        else:
                            # Existing client
                            if sock in self.server.new_clients:
                                self.server.login(sock)
                            else:
                                # Handle messages from client
                                self.server.handle_msg(sock)
                except Exception as e:
                    if self.server_running:
                        self.log_message(f"[{time.strftime('%H:%M:%S')}] Error: {str(e)}")
                    continue
        except Exception as e:
            self.log_message(f"[{time.strftime('%H:%M:%S')}] Server error: {str(e)}")
        finally:
            self.stop_server()
    
    def stop_server(self):
        """Stop the chat server"""
        if self.server_running and self.server:
            self.server_running = False
            
            # Close all client connections
            for sock in list(self.server.all_sockets):
                try:
                    if sock != self.server.server:
                        sock.close()
                except:
                    pass
            
            # Close the server socket
            try:
                self.server.server.close()
            except:
                pass
            
            # Update UI
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_var.set("Status: Stopped")
            self.status_label.config(fg="red")
            self.log_message(f"[{time.strftime('%H:%M:%S')}] Server stopped")
    
    def on_closing(self):
        """Handle window close event"""
        if self.server_running:
            if messagebox.askokcancel("Quit", "Server is still running. Are you sure you want to quit?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()


class TextRedirector:
    """Class to redirect stdout to a Tkinter Text widget"""
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag
    
    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")
    
    def flush(self):
        pass


def main():
    root = tk.Tk()
    app = ChatServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
