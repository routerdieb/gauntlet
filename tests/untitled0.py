from word2number import w2n

def find_cardAndOrdinalClean(text):
    text2 = ''
    prevNum = False
    for token in text.split():
        if chr(4) in token:
            word,tag = token.split(chr(4))
            if word == "-":
                text2 += "- "
                continue
            if tag == 'NUM' or tag == 'CD':
                if not prevNum:
                    text2 += chr(4)+'NUM '
                    prevNum = True
                else:
                    text2 = text2[:-2]
            elif '-' in word and len(word) > 1:
              for index,sub_token in enumerate(word.split('-')):
                try:
                  number = float(sub_token)
                  
                  if not prevNum:
                      text2 += chr(4)+'NUM - '
                      prevNum = True
                except:
                  try:
                    number = w2n.word_to_num(sub_token)
                    if not prevNum:
                        text2 += chr(4)+'NUM - '
                        prevNum = True
                  except:
                    text2 += sub_token+' - '
                    prevNum = False
              text2 = text2[:-2]
            elif word.endswith('th'):
              try:
                number = w2n.word_to_num(word[:-2])
                if not prevNum:
                    text2 += chr(4)+'NUM '
                    prevNum = True
                else:
                    text2 = text2[:-2]
              except:
                text2 += word + ' '
                prevNum = False
            else:
              text2 += word + ' '
              prevNum = False
    return text2

def prepare(doc):
  text1 = ''
  text2 = ''
  for token in doc:
      #print(token.text + " " + token.tag_ + ' - ' + token.pos_ + '/n')
      text1 += token.text+chr(4)+token.tag_+" "
      text2 += token.text+chr(4)+token.tag_+" "
  print("og")
  print(doc)
  #print(find_cardAndOrdinalClean(text1))
  print(find_cardAndOrdinalClean(text2))
  
import spacy
nlp = spacy.load("en_core_web_sm")

doc = nlp("The Flintstones were in 5 .")
prepare(doc)
doc = nlp("The Flintstones were in sixth place.")
prepare(doc)
doc = nlp("The Flintstones were in 6th place.")
prepare(doc)
doc = nlp("The Flintstones were in the top-5 place.")
prepare(doc)
doc = nlp("She was a six-shooter")
prepare(doc)
doc = nlp("She was twenty-three")
prepare(doc)
doc = nlp("He gave me a high-five.")
prepare(doc)