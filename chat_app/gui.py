from tkinter import *

# Esempio di GUI
def initialize_login():
    Window = Tk()
    Window.withdraw()

    # create login 
    loginform = Toplevel()
    
    # loginform.title
    loginform.resizable(width=False,
                                height=False)
    loginform.configure(width=400,
                                height=300)
    # create a Label
    pls = Label(loginform,
                        text="Please login to continue",
                        font="Helvetica 14 bold")

    pls.place(relheight=0.15,
                    relx=0.2,
                    rely=0.07)
    # create a Label
    labelName = Label(loginform,
                            text="Name: ",
                            font="Helvetica 12")

    labelName.place(relheight=0.2,
                            relx=0.1,
                            rely=0.2)

    # create a entry box for
    entryName = Entry(loginform,
                            font="Helvetica 14")

    entryName.place(relwidth=0.4,
                            relheight=0.12,
                            relx=0.35,
                            rely=0.2)

    # create a Label pass
    labelPass = Label(loginform,
                            text="Pass: ",
                            font="Helvetica 12")

    labelPass.place(relheight=0.2,
                            relx=0.1,
                            rely=0.4)

    # create a entry box for pass
    entryPass = Entry(loginform,
                            font="Helvetica 14")

    entryPass.place(relwidth=0.4,
                            relheight=0.12,
                            relx=0.35,
                            rely=0.4)

    # set the focus of the curser
    entryName.focus()

    # create a Continue Button
    # along with action
    go = Button(loginform,
                        text="CONTINUE",
                        font="Helvetica 14 bold")

    go.place(relx=0.4,
                    rely=0.7)
    Window.mainloop()

initialize_login()
