from datetime import datetime
import requests
from PyQt5 import QtWidgets
import clientui
from Crypto.Cipher import DES


def decode_text(key_str, text_str):
    key = key_str.encode('utf-8')
    text = bytes.fromhex(text_str)

    des = DES.new(key, DES.MODE_ECB)
    data = des.decrypt(text)

    return data.decode('utf-8')



class MessengerApp(QtWidgets.QMainWindow, clientui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.last_time = 0
        self.pushButton.pressed.connect(self.button_clicked)  # clicked
        self.pushButton_2.pressed.connect(self.update_messages_iteration)

    def send_message(self, username, password, text, ip):

        url = 'http://127.0.0.1:5000/'
        #url = 'http://' + ip + ':5000/'


        try:
            response_1 = requests.get(url, timeout=0.1)

            response = requests.post(
                url + 'auth',
                json={"username": username, "password": password}
            )

            if not response.json()['ok']:
                self.add_to_chat('Сообщение не отправлено')
                self.add_to_chat('')
                return

            response = requests.post(
                url + 'send',
                json={"username": username, "password": password, "text": text}
            )

            if not response.json()['ok']:
                self.add_to_chat('Сообщение не отправлено')
            self.add_to_chat('')

        except:
            self.add_to_chat('Произошла ошибка при отправке')


    def encode_text(self, key_str, text_str):

        key = key_str.encode('utf-8')
        text = text_str.encode('utf-8')

        def pad(text):
            while len(text) % 8 != 0:
                text += b' '
            return text

        des = DES.new(key, DES.MODE_ECB)
        padded_text = pad(text)
        encrypted_text = (des.encrypt(padded_text)).hex()
        self.add_to_chat(f"Зашифрованный текст:")
        self.add_to_chat(encrypted_text)
        return encrypted_text

    def update_messages_iteration(self):
        try:
            ip = self.plainTextEdit_3.toPlainText()
            url = 'http://127.0.0.1:5000/'
            #url = 'http://' + ip + ':5000/'

            response_1 = requests.get(url, timeout=0.1)
            response = requests.get(url + 'messages',
                                    params={'after': self.last_time})

            messages = response.json()["messages"]

            for message in messages:
                beauty_time = datetime.fromtimestamp(message["time"])
                beauty_time = beauty_time.strftime('%d/%m/%Y %H:%M:%S')
                self.add_to_chat(message["username"] + ' ' + beauty_time)
                self.add_to_chat(decode_text("qwertyui", message["text"]))
                self.add_to_chat('')

                self.last_time = message["time"]
        except:
            self.add_to_chat('Произошла ошибка при обновлении')

    def button_clicked(self):
        text_encrypt = self.encode_text("qwertyui", self.textEdit.toPlainText())
        try:
            self.send_message(
                self.plainTextEdit.toPlainText(),
                self.plainTextEdit_2.toPlainText(),
                text_encrypt,
                self.plainTextEdit_3.toPlainText()
            )
            #self.update_messages_iteration(self.plainTextEdit_3.toPlainText())

        except:
            self.add_to_chat('Произошла ошибка')

        self.textEdit.setText('')
        self.textEdit.repaint()
        #self.update_messages_iteration()

    def add_to_chat(self, text):
        self.textBrowser.append(text)
        self.textBrowser.repaint()


app = QtWidgets.QApplication([])
window = MessengerApp()
window.show()
app.exec_()
