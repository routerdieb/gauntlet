def find_card(text):
    text2 = ''
    for token in text.split():
        if chr(4) in token:
            word,tag = token.split(chr(4))
            if tag == 'NUM' or tag == 'CD':
                text2 += chr(4)+'NUM'
            else:
                text2 += word + ' '
    return text2

#print(find_card('This'+chr(4)+' is' +chr(4)+'verb 5'+chr(4)+'NUM' ))
