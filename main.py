import sys

from PyQt5.QtWidgets import (QApplication, QDialog, QMessageBox, QTableWidgetItem)

from PyQt5.uic import loadUi

from os.path import exists

class Window(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui/GUI.ui", self)
        self.connectButtonsPress()
        self.number = 8
        self.tabela = list()
        self.alfabet = list()
        for i in range(ord('a'), ord('z')+1):
            self.alfabet.append(str(chr(i)))
        for i in range(ord('A'), ord('Z') + 1):
            self.alfabet.append(str(chr(i)))
        for i in range(ord('0'), ord('9')+1):
            self.alfabet.append(str(chr(i)))
        self.alfabet.append(" ")
        self.alfabet.append(",")
        print(len(self.alfabet))
        self.size = 20

    def connectButtonsPress(self):
        self.info_button.clicked.connect(self.about)
        self.uruchom_button.clicked.connect(self.szyfrowanie)
        self.z_pliku_button.clicked.connect(self.wczytajPlik)
        self.do_pliku_button.clicked.connect(self.zapiszPlik)

    def about(self):
        #print(self.perm_kol.toPlainText())
        QMessageBox.about(self,
                          "O szyfrze: ",
                          "<p>Nazwa: Fractination</p>"
                          "<p>Implementacja: Maciej Walczykowski 145389</p>"
                          "<p>Działanie: Szyfr zamienia znaki tekstu na ich pozycje w tabeli</br>"
                          "(na prawo). Takie pozycje są łączone na zasadzie: </br>"
                          "pozycje w wierszach + pozycje w kolumnach, tak otrzymany ciąg</br>"
                          "znów przy użyciu tabeli zamieniany jest na znaki.</p>"
                          "<p>Deszyfrowanie: Szyfr zamienia znaki tekstu na ich pozycje w tabeli</br>"
                          "(na prawo). Takie pozycje są dzielone na zasadzie: </br>"
                          "połowa ciągu - wiersze, reszta - kolumny, tak otrzymany ciąg</br>"
                          "znów przy użyciu tabeli zamieniany jest na znaki.</p>"
                          "<p>Alfabet: Małe i wielkie znaki alfabetu z ASCII, spacja, przecinek i cyfry</p>"
                          "<p>Znaki spoza alfabetu są pomijane.</p>"
                          )

    def checkPerm(self, perm):
        obecne = list()
        for i in range(self.number):
            obecne.append(0)
        if perm == "":
            return False
        for i in perm:
            if i < "0" or i > str(self.number):
                return False
            liczba = int(i)
            if obecne[liczba-1] == 1:
                return False
            obecne[liczba-1] = 1
        if 0 in obecne:
            return False
        return True

    def checkKey(self, key):
        if key == "" :
            return False
        for i in key:
            if i not in self.alfabet:
                return False
        return True
    def nowyKey(self, key):
        nowy = ""
        for i, v in enumerate(key):
            if v in key[:i]:
                continue
            nowy += v
        return nowy

    def szyfrowanie(self):
        kolumny = self.perm_kol.toPlainText()
        wiersze = self.perm_wier.toPlainText()
        klucz = self.klucz.toPlainText()
        print(kolumny, wiersze, klucz)
        if not (self.checkPerm(kolumny) and self.checkPerm(wiersze) and self.checkKey(klucz)):
            QMessageBox.about(self,
                              "Błąd: ",
                              "<p>Nie podano parametrów szyfrowania!</p>"
                              "<p>Bądź błędne wartości!</p>")
            return
        klucz = self.nowyKey(klucz)
        self.generujTabele(kolumny, wiersze, klucz)
        print(klucz)
        if self.szyfruj.isChecked():
            print("Szyfrowanie")
            text = self.text_input.toPlainText()
            text = self.blokTekstu(text)
            result = ""
            for i in text:
                result += (self.zaszyfruj(i))
            self.text_output.setPlainText(result)
        else:
            print("Deszyfrowanie")
            text = self.text_input.toPlainText()
            text = self.blokTekstu(text)
            result = ""
            for i in text:
                result += (self.odszyfruj(i))
            self.text_output.setPlainText(result)

    def blokTekstu(self, dane):
        size = self.size
        teksty = list()
        reszta = len(dane) - len(dane)//size * size
        dodatek = "$"*reszta
        dane += dodatek
        i = 0
        while i < len(dane):
            teksty.append(dane[i:(len(teksty)+1)*size])
            i += size
        return teksty

    def zaszyfruj(self, text):
        wiersze = list()
        kolumny = list()
        result = ""
        for i in text:
            if i == "$":
                break
            if i not in self.alfabet:
                continue
            wsp = self.znajdzZnak(i)
            if type(wsp) is tuple:
                wiersze.append(wsp[0])
                kolumny.append((wsp[1]))
        lacznie = wiersze + kolumny
        for i in range(0, len(lacznie), 2):
            result += self.zwrocZnak((lacznie[i], lacznie[i+1]))
        return result

    def odszyfruj(self, text):
        temp = list()
        result = ""
        for i in range(len(text)):
            if text[i] == "$":
                break
            wsp = self.znajdzZnak(text[i])
            temp.append(wsp[0])
            temp.append(wsp[1])

        wiersze = temp[:len(temp)//2]
        kolumny = temp[len(temp)//2::]

        for i in range(len(kolumny)):
            result += self.zwrocZnak((wiersze[i], kolumny[i]))
        return result

    def znajdzZnak(self, znak):
        for i in range(1,self.number+1):
            for j in range(1,self.number+1):
                if self.tabela[i][j] == znak:
                    return self.tabela[i][0], self.tabela[0][j]
        return znak

    def zwrocZnak(self, wsp):
        for i in range(1, self.number+1):
            if self.tabela[i][0] == wsp[0]:
                w = i
        for i in range(1, self.number+1):
            if self.tabela[0][i] == wsp[1]:
                k = i
        return self.tabela[w][k]

    def generujTabele(self, kolumny, wiersze, klucz):
        for _ in range(self.number+1):
            self.tabela.append([0 for _ in range(self.number+1)])
        kol = [int(i) for i in kolumny]
        wier = [int(i) for i in wiersze]
        self.tabela[0][0] = "X"
        for i in range(self.number):
            self.tabela[0][i+1] = kol[i]
        for i in range(self.number):
            self.tabela[i+1][0] = wier[i]

        obecny = [0 for _ in range(len(self.alfabet))]
        nrKol = 1
        nrWier = 1
        for i in klucz:
            obecny[self.alfabet.index(i)] = 1
            self.tabela[nrWier][nrKol] = i
            nrKol += 1
            if nrKol == self.number+1:
                nrKol = 1
                nrWier += 1
        for i in range(len(obecny)):
            if obecny[i] == 1:
                continue
            self.tabela[nrWier][nrKol] = self.alfabet[i]
            nrKol += 1
            if nrKol == self.number+1:
                nrKol = 1
                nrWier += 1
        for i in range(self.number+1):
            for j in range(self.number+1):
                self.tabela_wiz.setItem(i, j, QTableWidgetItem(f'{self.tabela[i][j]}'))
    def zapiszPlik(self):
        nazwa = "informacja.txt"
        plik = open(nazwa, "w")
        dane = self.text_output.toPlainText()
        plik.write(dane)
        QMessageBox.about(self,
                          "Komunikat:",
                          "<p>Zapisano do pliku: informacja.txt</p>")
        plik.close()

    def wczytajPlik(self):
        nazwa = self.text_input.toPlainText() + ".txt"
        #print(nazwa)
        if not exists(nazwa):
            QMessageBox.about(self,
                              "Błąd: ",
                              "<p>Plik nie istnieje!</p>")
        else:
            plik = open(nazwa, "r")
            dane = plik.read()
            QMessageBox.about(self,
                              "Komunikat:",
                              "<p>Wczytano plik: " + nazwa + "</p>")
            plik.close()
            self.text_input.setPlainText(dane)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
