

import polyglot
from polyglot.text import Text, Word

text = Text("Bonjour, Mesdames.")
print("Language Detected: Code={}, Name={}\n".format(text.language.code, text.language.name))

rus_text ='''
Не сильно хороший фильм.
'''
text = Text(rus_text)
print("{:<16}{}".format("Word", "Polarity")+"\n"+"-"*30)

for w in text.words:
    if w.polarity !=0:
        print("{:<16}{:>2}".format(w, w.polarity))



