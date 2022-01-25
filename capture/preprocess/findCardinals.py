def find_card(text):
    text2 = ''
    for token in text.split():
        if chr(4) in token:
            word,tag = token.split(chr(4))
            if tag == 'NUM' or tag == 'CD':
                text2 += chr(4)+'NUM '
            else:
                text2 += word + ' '
    return text2

#print(find_card('This'+chr(4)+' is' +chr(4)+'verb 5'+chr(4)+'NUM' ))

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