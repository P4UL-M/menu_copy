import socket # seriously a comment for that ?
import json # well no need to explain
from threading import Thread # because we need multi-threading everywhere

class context:
    """
    class pour passer les infos du message rapidement
    """
    def __init__(self,peer,message):
        self.peer = peer
        for name,elt in message.items():
            setattr(self,name,elt)

# class inherit from socket so all that a socket can do, this class can also do
class Client(socket.socket):
    """
    class discussion avec le server
    """
    def __init__(self,Host=None, Port = None):
        #constants
        self.client_name = None
        self.HOST = Host or 'localhost'  # The server's hostname or IP address
        self.PORT = Port or 65432        # The port used by the server
        # dict of all method for all possible event
        self.handles:dict = {}
           
    def run(self):
        """
        Initialise et lance le client socket
        """
        self.ready = False
        super().__init__(socket.AF_INET, socket.SOCK_STREAM) # inititalization of the socket
        self.connect((self.HOST, self.PORT)) # connection to the server
        self.thread = Thread(target=self.handle,daemon=True) # new thread for handling event
        self.thread.start()
        if self.client_name:
            self.send_message(event="connection",args={"name":self.client_name})
    
    def handle(self):
        """
        récupère et traite les évènement
        """
        try:
            while True:
                data = self.recv(1024)
                if not data:
                    raise ConnIterupted()
                data = data.decode('utf-8')
                print("<- ",data)
                ctx = context(self,json.loads(data))
                if ctx.event in self.handles.keys():
                    self.handles[ctx.event](ctx)
                else:
                    print("Event not found :",ctx.event)
        except ConnRejected: # trigger by bad name event
            print(f"connection to {self.HOST} was rejected")
        except ConnIterupted: # trigger by lost of connection
            self.ready = False
            print(f"disconnected from {self.HOST}, connection was stop by the peer")
        except Exception as e:
            print(f"disconnected from {self.HOST}, {e}")

    def Event(self,func):
        """
        Ce décorateur crée une fonction qui ajoute celle ci à la liste des fonctions.
        La fonction passé en décoration n'est executé que si l'évènement est appellé.
        """
        if func.__name__ not in self.handles.keys():
            self.handles[func.__name__] = func
        else:
            raise RuntimeError("the function you want to pass already exist")

    def send_message(self,event,args=dict()):
        """
        Fonction d'envoie de message
        """
        if event=='':
            return
        message = {
            'event':event
        }
        message.update(args)
        message = json.dumps(message)
        print("->",message)
        data = str.encode(message)
        self.sendall(data)

class ConnRejected(Exception):
    """
    Execption when server reject connection
    """
    def __init__(self, *args: object,**kargs):
        super().__init__(*args,**kargs)

class ConnIterupted(Exception):
    """
    Execption when server reject connection
    """
    def __init__(self, *args: object,**kargs):
        super().__init__(*args,**kargs)