import requests
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto import Signature
from Crypto.Hash import SHA256
import jwt, time, sys, random, string
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import binascii

class User:
    
    def __init__(self):
        self.getCSRFtoken()
    
    def getCSRFtoken(self):
        URL = 'https://127.0.0.1:8000/accounts/challenge/'
        self.client = requests.session()

        # Retrieve the CSRF token first
        self.client.get(URL)  # sets cookie
        if 'csrftoken' in self.client.cookies:
            # Django 1.6 and up
            self.csrftoken = self.client.cookies['csrftoken']  # CSRF token needed for each request.
        else:
            # older versions
            self.csrftoken = self.client.cookies['csrf']

        return
    
    def isTokenExpired(self, token):
        claims = jwt.decode(token, options={"verify_signature": False})

        current_time = time.time()

        if current_time > claims['exp']:
            return True
        else:
            return False
    
    def tokenRefresh(self):
        URL = 'https://127.0.0.1:8000/accounts/refresh/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, refresh=self.refreshToken)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL))

        if r.status_code == 200:
            self.accessToken = r.json().get("access")
        
        return
    
    def encryptPrivateKey(self, symmetricKey, privateKey):
        cipher = AES.new(symmetricKey, AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(privateKey)
        return ciphertext, tag, cipher.nonce
    
    def decryptPrivateKey(self, symmetricKey, EncryptedPrivateKey, nonce, tag):
        cipher = AES.new(symmetricKey, AES.MODE_EAX, nonce=nonce)
        data = cipher.decrypt_and_verify(EncryptedPrivateKey, tag)
        return data
    
    def register(self, displayname, username, password):
        URL = 'https://127.0.0.1:8000/accounts/register/'

        keyPair = RSA.generate(2048)
        publicKey = keyPair.publickey().exportKey(format="PEM")
        privateKey = keyPair.exportKey(format="PEM")

        self.userSecret = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(6))

        symmetricKey = PBKDF2(password, self.userSecret, 32, count=1000000, hmac_hash_module=SHA256)
        
        encryptedPrivateKey, tag, nonce = self.encryptPrivateKey(symmetricKey, privateKey)

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, username=username, displayname=displayname, 
                        private_key = binascii.hexlify(encryptedPrivateKey),
                        tag = tag,
                        nonce = nonce,
                        public_key = publicKey)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL))
        
        return r
    
    def login(self, username, password, secret):
        # CHALLENGE.
        URL_challenge = 'https://127.0.0.1:8000/accounts/challenge/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, username=username)
        r = self.client.post(URL_challenge, data=sendData, headers=dict(Referer=URL_challenge))
        
        if (r.status_code == 200):
            challenge = r.json().get("challenge")
            self.publicKey = r.json().get("public_key")
            encryptedPrivateKey = r.json().get("private_key")
            tag = r.json().get("tag")
            nonce = r.json().get("nonce")

            publicKey = load_pem_public_key(bytes.fromhex(self.publicKey))

            symmetricKey = PBKDF2(password, secret, 32, count=1000000, hmac_hash_module=SHA256)

            self.privateKey = load_pem_private_key(self.decryptPrivateKey(symmetricKey, encryptedPrivateKey, nonce, tag))

            signature = self.privateKey.sign(challenge,
                                            padding.PSS(
                                            mgf=padding.MGF1(hashes.SHA256()),
                                            salt_length=padding.PSS.MAX_LENGTH),
                                            hashes.SHA256())
        
            # LOGIN.
            URL = 'https://127.0.0.1:8000/accounts/login/'

            sendData = dict(csrfmiddlewaretoken=self.csrftoken, username=username, signed_challenge=signature)
            r = self.client.post(URL, data=sendData, headers=dict(Referer=URL))

            if (r.status_code == 200):
                self.tokens = r.json().get("tokens")
                self.accessToken = self.tokens['access']
                self.refreshToken = self.tokens['refresh']
                self.displayname = r.json().get("displayname")
        
            return r
    
    def events(self):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit()
        
        URL = 'https://127.0.0.1:8000/events/list/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))

        eventsDic = r.json()
        listEvents = []

        for i in eventsDic:
            listEvents.append(EventUser(eventsDic[i][0], self.displayname, eventsDic[i][1], eventsDic[i][2], eventsDic[i][3], 
                                        eventsDic[i][4], eventsDic[i][5]))
        
        return listEvents

    def createEvent(self, event):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/events/create/'

        # ASSYMETRIC PUBLIC & PRIVATE KEYS: RSA.

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, name=event.name, startdate=event.startdate, enddate=event.enddate, location=event.location, 
                        description=event.description, participants=event.participants)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))
        
        return r

    def invitedEvents(self):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/events/invitations/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))

        eventsDic = r.json()
        listEvents = []

        for i in eventsDic:
            listEvents.append(EventUser(eventsDic[i][0], eventsDic[i][1], eventsDic[i][2], eventsDic[i][3], eventsDic[i][4], 
                                        eventsDic[i][5], eventsDic[i][6]))
        
        return listEvents
    
    def removeEvent(self, event):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/events/remove/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, name=event.name, startdate=event.startdate, enddate=event.enddate)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))
        
        return r
    
    def modifyEvent(self, oldEvent, newEvent):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/events/modify/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, oldname=oldEvent.name, oldstartdate=oldEvent.startdate, oldenddate=oldEvent.enddate,
                        newname=newEvent.name, newstartdate=newEvent.startdate, newenddate=newEvent.enddate, newlocation=newEvent.location,
                        newdescription=newEvent.description, newparticipants=newEvent.participants)

        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))
        
        return r


    def addContact(self, friend):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/contacts/add/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, frienddisplayname=friend)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))

        return r

    def contacts(self):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/contacts/list/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))
        
        return r.json()
    
    def pendingContacts(self):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/contacts/pending/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))
        
        return r.json()

    def acceptContact(self, friend):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/contacts/accept/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, frienddisplayname=friend)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))
        
        return r

    def removeContact(self, friend):
        if self.isTokenExpired(self.accessToken):
            self.tokenRefresh()
        if self.isTokenExpired(self.refreshToken):
            sys.exit("Refresh token expired")
        
        URL = 'https://127.0.0.1:8000/contacts/remove/'

        sendData = dict(csrfmiddlewaretoken=self.csrftoken, frienddisplayname=friend)
        r = self.client.post(URL, data=sendData, headers=dict(Referer=URL, Authorization = "Bearer " + self.accessToken))
        
        return r
    

class EventUser:

    def __init__(self, name, creator, participants, startdate, enddate, location, description):
        self.name = name
        self.creator = creator
        self.participants = participants
        self.startdate = startdate
        self.enddate = enddate
        self.location = location
        self.description = description