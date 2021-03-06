import asyncore
import asynchat
import socket
import json
import hashlib
import controllers
import event_manager
import events
import view

import tkinter
import tkinter.messagebox as messagebox

class Login:
    def __init__(self, caller):
        self._caller = caller

        self._login = tkinter.Tk()
        self._login.title("Login")
        self._login.geometry('190x70')
        self._center(self._login)
        self._usernameLabel = tkinter.Label(self._login, text = "Username:")
        self._userEntry = tkinter.Entry(self._login)
        self._passwordLabel = tkinter.Label(self._login, text = "Password:")
        self._passEntry = tkinter.Entry(self._login, show="*")
        self._connectButton = tkinter.Button(self._login, text = "Connect", command = self._connect)
        self._usernameLabel.grid(row = 0, column = 0)
        self._userEntry.grid(row = 0, column = 1)
        self._passwordLabel.grid(row = 1, column = 0)
        self._passEntry.grid(row = 1, column = 1)
        self._connectButton.grid(row = 2, column = 1)
        
        self._passEntry.bind('<Return>', self._connect)
        self._username = ""

        self._login.mainloop()

    def _center(self, toplevel):
        toplevel.update_idletasks()
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def _connect(self, *args):
        self._username = self._userEntry.get()
        self._caller.push(bytes("LOGIN_ATTEMPT " + json.dumps(dict([("username", self._username),
                               ("password", hashlib.sha512(bytes(self._passEntry.get(), 'UTF-8')).hexdigest())])) + "\n", 'UTF-8'))

        self._login.destroy()

    def get_user(self):
        return self._username
    

    def _login_fail(self):
        messagebox.showerror("Error", "Wrong Password!")
        return True

   


class Lobby:
    def __init__(self, caller):
        self._caller = caller
        self._lobby = tkinter.Tk()
        self._lobby.title("Lobby")
        self._lobby.geometry('200x150')
        self._center(self._lobby)

        self._welcomeLabel = tkinter.Label(self._lobby, text = "Welcome " + caller._username + "!")

        self._create = tkinter.Button(self._lobby, text = "Create", command = self._create)
        self._join = tkinter.Button(self._lobby, text = "Join", command = self._join)
        self._entry = tkinter.Entry(self._lobby)
        self._message = tkinter.Label(self._lobby, text = "Create a new game \n or join an existing game \n by typing in a username!")
        self._welcomeLabel.pack()
        self._create.pack()
        self._entry.pack()
        self._join.pack()
        self._message.pack()
        self._lobby.mainloop()

    def _center(self, toplevel):
        toplevel.update_idletasks()
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = w/2 - size[0]/2
        y = h/2 - size[1]/2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def _create(self):
        self._create.config(text = "Start", command = self._start)
        self._join.config(state = 'disable')
        self._caller.push(bytes("NEW_GAME" + "\n", 'UTF-8'))
        self._message.config(text = "New game created \n press start when ready to play!")

    def _start(self):
        self._caller.push(bytes("GAME_START" + "\n", 'UTF-8'))
        self._lobby.destroy()

    def _join(self):
        self._caller.push(bytes("JOIN_GAME " + self._entry.get() + "\n", 'UTF-8'))
        self._lobby.destroy()


class Client(asynchat.async_chat):

    def __init__(self, host, port, eventManager):
        asynchat.async_chat.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        self._event_manager = eventManager
        self._event_manager.register_listener(self)
        self.set_terminator(b'\n')
        self._received_data = ""
        self._pygame_view = None
        self._login_screen = True

        self._username = ""
        
    def handle_connect(self):
        login = Login(self)
        self._username = login.get_user()

    def collect_incoming_data(self, data):
        self._received_data += data.decode('UTF-8')

    def found_terminator(self):
        self._received_data.strip('\n')
        split_string = self._received_data.split(' ', 1)
        key = split_string[0]
        if key == "UPDATE":
            data = split_string[1]
            self._event_manager.post(events.ServerUpdateReceived(data))
        elif key == "LOGIN_REQUEST":
            login = Login(self)
            self._username = login.get_user()
        elif key == "LOGIN_FAIL":
            print("LOGIN FAILED")
            root = tkinter.Tk()
            root.withdraw()
            messagebox.showerror("Error", "Wrong Password!")
            root.destroy()
            login = Login(self)
            self._username = login.get_user()
        elif key == "LOGIN_SUCCESS":
            self._pygame_view = view.PygameView(self._event_manager)
            lobby = Lobby(self)

        elif key == "USER_CREATED":
            self._pygame_view = view.PygameView(self._event_manager)
            lobby = Lobby(self)

        elif key == "GAME_OVER":
            self._event_manager.post(events.GameOverEvent())
        self._received_data = ""

    def notify(self, event):
        if isinstance(event, events.QuitEvent):
            self.push(bytes("QUIT\n",'UTF-8'))
            self.close()
        elif isinstance(event, events.MoveEvent):
            print("Message: {} sent".format(event.get_direction()))
            self.push(bytes("MOVE " + json.dumps(dict([("username", self._username),
                                                       ("direction", event.get_direction())])) + "\n", 'UTF-8'))
        elif isinstance(event, events.RestartEvent):
            self.push(bytes("RESTART\n", 'UTF-8'))


def check_ip_addr(ip_addr):
    try:
        socket.inet_pton(socket.AF_INET, ip_addr)
        return True
    except socket.error:
        return False

def main():
    try:
        eventManager = event_manager.EventManager()
        ip_addr = ""
        while not check_ip_addr(ip_addr):
            ip_addr = input("Please input server's IP address: ")
        port = ""
        while not port.isdigit():
            port = input("Please input server's port: ")
        controller = controllers.Controller(eventManager)
        client = Client(ip_addr, int(port), eventManager)
        asyncore.loop(timeout=1)
    except:
        pass

if __name__ == "__main__":
    main()
