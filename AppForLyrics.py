from tkinter import *
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt

# Create the window for the GUI
root = Tk()
root.geometry('300x300')

# A dictionnary for the songs and their respective genius site url
songs_url = {"Oh My God": "https://genius.com/Adele-oh-my-god-lyrics",
             "A Gentleman's Excuse Me": "https://genius.com/Fish-a-gentlemans-excuse-me-lyrics",
             "Gravity": "https://genius.com/Sara-bareilles-gravity-lyrics",
             "Happier Than Ever": "https://genius.com/Billie-eilish-happier-than-ever-lyrics",
             "Believer": "https://genius.com/Imagine-dragons-believer-lyrics",
             "abcdefu":"https://genius.com/Imagine-dragons-believer-lyrics",
             "Easy On Me": "https://genius.com/Adele-easy-on-me-lyrics"
             }

# Add the label to the GUI window
l = Label(root, text = "Song Lyric Analyzer")
l.pack()

# Get the user selected song and use it to perform the functions
def buttonFunction():
    myLabel = Label(root, text = song.get())
    myLabel.pack()

def lyricsAnalyzer():
    # find the contents of the site
    input_song = song.get()
    url = songs_url[input_song]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # find the song title
    title = soup.find(class_="SongHeaderVariantdesktop__HiddenMask-sc-12tszai-10 bFjDxc").get_text()
    print(title)

    # find the song Artist
    artist = soup.find(class_="Link-h3isu4-0 hwdSYP SongHeaderVariantdesktop__Artist-sc-12tszai-11 ayFeg").get_text()
    print(artist)

    # find the lyrics
    # As the website changes, you might have to change the attrs = {} to the new class code
    lyrics = soup.findAll("div", attrs={"class": "Lyrics__Container-sc-1ynbvzw-6 jYfhrf"})
    print(lyrics)

    # Put all the lyrics in 1 long line
    lyrics_one_line = []
    for p in lyrics:
        for br in p.findAll('br'):
            br.replace_with('\n')

        parsedText = p.get_text()
        while '\n ' in parsedText:
            parsedText = parsedText.replace('\n ', '\n')

        lyrics_on_lines = parsedText.strip()
        lyrics_one_line.append(lyrics_on_lines)

    lyrics_array = np.array(lyrics_one_line)

    # Create an array for the lyrics based on new lines
    clean_lyrics = []
    for i in lyrics_array:
        clean_lyric = i.split('\n')
        clean_lyric = clean_lyric[1:-1]
        clean_lyrics.append(clean_lyric)

    # Transform the array into a dataframe
    df = pd.DataFrame(clean_lyrics)
    df = df.transpose()

    # Make all the words in the lyrics into 1 column dataframe
    all_values = []
    for column in df:
        this_column_values = df[column].tolist()
        all_values += this_column_values
    one_column_df = pd.DataFrame(all_values)
    one_column_df = one_column_df.dropna()
    one_column_df.columns = ["Lyrics"]
    one_column_df = one_column_df[~one_column_df["Lyrics"].str.contains("[", regex=False)]

    # Lyrics without the paragraphs separating them
    one_column_no_par = one_column_df.copy()
    one_column_no_par["Lyrics"].replace('', np.nan, inplace=True)
    one_column_no_par.dropna(subset=["Lyrics"], inplace=True)

    # Create a paragraph of all of the words to count each occurence
    list = one_column_no_par.values.tolist()
    list_to_string = ' '.join([str(elem) for elem in list])

    # Remove special characters we dont want included in the words
    list_to_string2 = list_to_string.replace("[", "")
    list_to_string2 = list_to_string2.replace("]", "")
    list_to_string2 = list_to_string2.replace(")", "")
    list_to_string2 = list_to_string2.replace("!", "")
    list_to_string2 = list_to_string2.replace(" '", " ")
    list_to_string2 = list_to_string2.replace("' ", " ")
    list_to_string2 = list_to_string2.replace("\\", "")
    list_to_string2 = list_to_string2.replace("?", "")
    list_to_string2 = list_to_string2.replace("(", "")
    list_to_string2 = list_to_string2.replace('"', '')
    list_to_string2 = list_to_string2.replace(',', '')
    list_to_string2 = list_to_string2.lower()

    # remove stop words from the lyrics
    words = [word for word in list_to_string2.split() if word.lower() not in ENGLISH_STOP_WORDS]
    list_no_stpwrds = " ".join(words)

    # count the frequency each word is said
    def freq(str):
        str_list = str.split()
        unique_words = set(str_list)

        for words in unique_words:
            print("Frequency of ", words, " : ", str_list.count(words))

    freq(list_no_stpwrds)

    #Create the word cloud and show it in a new window
    wordcloud = WordCloud(max_font_size=50, collocations=False, stopwords=STOPWORDS,
                          background_color="white").generate(list_no_stpwrds)
    plt.figure()
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

# update the listbox based on what is typed
def update(data):
    # Clear the listbox
    all_songs.delete(0, END)
    # Add songs to listbox
    for item in data:
        all_songs.insert(END,item)

# Update entry box with listbox clicked
def fillout(e):
    # Delete whatever is in the entry box
    song.delete(0,END)
    # Add clicked list in item to entry box
    song.insert(0,all_songs.get(ACTIVE))

def check(e):
    # grab what was typed in the text box to update it
    typed = song.get()

    if typed == '':
        data = songs_url
    else:
        data = []
        for item in songs_url:
            if typed.lower() in item.lower():
                data.append(item)
    # update our listbox with selected items
    update(data)


# fill in box with all the song options from the dictionary
song = Entry(root)
song.pack()

# List box of all the songs in the dictionary
all_songs = Listbox(root, width = 20)
all_songs.pack()

# List of songs changes as people search in the text box
update(songs_url)

# Create a binding on the listbox onclick
all_songs.bind("<<ListboxSelect>>", fillout)

# Create a binding on the entry box
song.bind("<KeyRelease>", check)

# Add a button to the window to run the analyzer function
b = Button(root, text = "Run It", command = lyricsAnalyzer)
b.pack()

root.mainloop()