from customtkinter import *

window = CTk()

window.geometry("400x400")

window.title('Task2')

btn = CTkButton (window, text='Клік', width=380)
btn.pack ()

coc = CTkTextbox(window,  width=380, height=280)
coc.pack(pady=10)

cat = CTkEntry(window,  width=380)
cat.pack(pady=10)

window.mainloop()
