""" The default game, using the 'meaning' mode.

Mode 1: meaning.
    A radical is shown, and the player has to choose the meaning.
Mode 2: localization.
    A meaning is given, the player has to select the localization
    of the radical inside example hanzi.
Mode 3: meaning_r
    A radical is shown, and the player has to choose the correct
    meaning in english.
"""
import random
import pandas as pd

from load import load_radicals, load_radicals_complete

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QFrame, QHBoxLayout, QMenu, QDialog, QListWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl


# load gamemodes
class Screen(QWidget):
    def __init__(self, parent=None, mode='meaning'):
        super().__init__(parent)
        self.radicals = load_radicals_complete()
        # self.radicals = self.radicals[:27]
        # print("WARNING: Loaded radicals 0-26")
        self.initUI(mode=mode)


    def set_mode(self, mode):
        # modes: 'meaning', 'find hanzi'
        self.mode = mode
        if mode == 'meaning':
            self.game_function = self.show_new_radical_and_choices
            self.choice_count = 4
            self.choices.setFixedHeight(150)
            self.score.setFont(QFont('Arial', 20))
            self.score.setFixedHeight(100)
            self.choice_font_size = 20

        elif mode == 'find hanzi':
            self.game_function = self.show_new_meaning_and_choices
            self.choice_count = 8
            self.choices.setFixedHeight(400)
            self.score.setFont(QFont('Arial', 25))
            self.score.setFixedHeight(100)
            self.choice_font_size = 30
        else:
            raise ValueError(f'Unknown mode {mode}')
        
        self.game_function()
        

    def initUI(self, mode):
        self.input = QLineEdit()
        self.input.setReadOnly(True)
        self.input.setFont(QFont('Arial', 40))
        self.input.setAlignment(Qt.AlignCenter)
        self.input.setFixedHeight(100)
    
        self.input_pinyin = QLineEdit()
        self.input_pinyin.setReadOnly(True)
        self.input_pinyin.setAlignment(Qt.AlignCenter)

        self.choices = QListWidget()
        self.choices.itemClicked.connect(self.check_choice)

        # score is a text that allows newlines
        self.score = QLabel()
        self.score.setWordWrap(True)
        self.score_correct = 0
        self.score_wrong = 0
        self.score.setFixedHeight(70)
        self.score.setAlignment(Qt.AlignTop)
        self.score.setText('0 correct, 0 wrong')
        self.answer = ''
        
        # spacer, between score and input
        spacer = QWidget()
        spacer.setFixedHeight(20)

        self.audio_player = QMediaPlayer()
        self.play_audio_button = QPushButton('Play audio')
        self.play_audio_button.clicked.connect(self.play_current_audio)

        # start mode with 'Game mode' title
        self.mode_box = QComboBox()
        self.mode_box.setFont(QFont('Arial', 20))
        self.mode_box.addItems(['meaning', 'find hanzi'])
        self.mode_box.setCurrentText(mode)
        self.mode_box.currentTextChanged.connect(self.set_mode)

        self.set_mode(mode)

        # layout
        layout = QVBoxLayout()
        layout.addWidget(self.mode_box)
        layout.addWidget(self.score)
        layout.addWidget(spacer)
        layout.addWidget(self.input)
        layout.addWidget(self.input_pinyin)
        layout.addWidget(self.choices)
        layout.addWidget(self.play_audio_button)
        self.setLayout(layout)


    def play_current_audio(self):
        """ Play the audio of the pinyin """
        # Set the  media content to the player
        self.play_audio(self.mp3_p)


    def show_new_radical_and_choices(self):
        """ Show a radical,
            the choices (1 real, n fake) for the player.
            the answer, but hide it initially
        """
        # show radical
        radical = self.radicals.sample()
        input_text = radical['Radical'].values[0]
        input_pinyin = radical['Pinyin'].values[0]
        self.answer = radical['Meaning'].values[0]
        self.input.setText(input_text)
        self.choices.clear()
        self.input_pinyin.setText(input_pinyin)

        # show choices
        choices = [radical['Meaning'].values[0]]
        while len(choices) < self.choice_count:
            fake = self.radicals.sample()
            fake = fake['Meaning'].values[0]
            # check if fake is already in choices, also prevents using real answer as fake
            if fake not in choices:
                choices.append(fake)

        random.shuffle(choices)
        for choice in choices:
            self.choices.addItem(choice)
            
        # for choices, align to center
        for i in range(self.choices.count()):
            item = self.choices.item(i)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(QFont('Arial', self.choice_font_size))
           
 
        # lastly, play the audio
        mp3_p = radical['Audio'].values[0]
        mp3_p = str(mp3_p.resolve())
        self.mp3_p = mp3_p
        self.play_audio(mp3_p)


    def show_new_meaning_and_choices(self):
        """ Show a meaning,
            the choices (1 real Hanzi, n fake) for the player.
            the answer, but hide it initially
        """
        # Select a random radical
        radical = self.radicals.sample()
        self.answer = radical['Radical'].values[0]
        input_meaning = radical['Meaning'].values[0]
        input_pinyin = radical['Pinyin'].values[0]
        
        self.input.setText(input_meaning)
        self.input_pinyin.setText(input_pinyin)
        self.choices.clear()

        # Prepare choices with one real and fake Hanzi
        choices = [self.answer]
        while len(choices) < self.choice_count:
            fake = self.radicals.sample()
            fake_hanzi = fake['Radical'].values[0]
            if fake_hanzi not in choices:
                choices.append(fake_hanzi)
        
        random.shuffle(choices)
        for choice in choices:
            self.choices.addItem(choice)
        # for choices, align to center
        for i in range(self.choices.count()):
            item = self.choices.item(i)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(QFont('Arial', self.choice_font_size))

        # Play the audio
        mp3_p = radical['Audio'].values[0]
        mp3_p = str(mp3_p.resolve())
        self.mp3_p = mp3_p
        self.play_audio(mp3_p)

    def play_audio(self, mp3_p):
        """ Play the audio of the pinyin """
        # Set the  media content to the player
        url = QUrl.fromLocalFile(mp3_p)  # Replace with the path to your MP3 file
        content = QMediaContent(url)
        self.audio_player.setMedia(content)
        # Play the audio
        self.audio_player.play()
    

    def check_choice(self, item):
        """ Check if the player's choice is correct """
        # Correct! 女 means female
        pinyin_text = self.input_pinyin.text()
        real_meaning = f'{self.input.text()} ({pinyin_text}) = {self.answer}'
        if item.text() == self.answer:
            message = f'Correct! {real_meaning}'
            self.score_correct += 1
        else:
            message = f'Wrong! {real_meaning}'
            self.score_wrong += 1

        score_text = f'{self.score_correct} correct, {self.score_wrong} wrong\n\n{message}'
        self.score.setText(score_text)

        self.score.show()
        self.game_function()




if __name__ == '__main__':
    app = QApplication([])
    # init with mode 'show hanzi'
    # screen = Screen(mode='find hanzi')
    screen = Screen(mode='meaning')
    screen.show()
    app.exec_()
