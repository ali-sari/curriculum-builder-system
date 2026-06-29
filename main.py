import tkinter as tk
from gui import LoginWindow

def main():
    root = tk.Tk()
    
    # LoginWindow kendi içinde AdminDB'yi çalıştırıp tabloları oluşturacak
    app = LoginWindow(root)
    
    root.mainloop()

if __name__ == '__main__':
    main()