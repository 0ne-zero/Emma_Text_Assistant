def get_key_by_value(value:str, dictionary:dict):
    if type(dictionary) == dict:
        for k in dictionary.keys():
            if dictionary[k] == value.capitalize():
                return k

def upper_first_letter(string:str):
    '''Returns input string with Upper first letter'''
    return string[0].upper() + string[1:]

def smalling_text(text: str, max_length) -> list:
    '''
    Smalling text to maximum length
    If the text characters are larger than max_length,
    we need to make the text smaller, so we divide the text into smaller pieces.
    and put those pieces into a list
    Returns:
    string: when the text characters itself is less than the max_length
    list: when the text characters bigger than the max_length
    '''
    if len(text) <= max_length:
        return text
    else:
        sentences = []
        variable_max_length = max_length
        pos = 0
        length = len(text)
        complete = False
        while (complete == False):
            if ((pos + variable_max_length) < length):
                while(text[(pos + variable_max_length)] != ' '):
                    variable_max_length -= 1
                sentences.append(text[pos:(pos + variable_max_length)])
                pos = (pos + variable_max_length)
                variable_max_length = max_length
            else:
                sentences.append(text[pos:])
                complete = True
        return sentences

    '''
    Another approach
    while text != '':
    try:
        while(text[variable_max_length] != ' '):
            variable_max_length -= 1
        sentences.append(text[:variable_max_length])
        text = text[variable_max_length:]
        variable_max_length = max_length
    except:
        sentences.append(text)
        text = ''
    '''

def convert_words_list_to_sentence(words_list: list):
    list_len = len(words_list)
    sentence = ''
    index = 0
    while(index < list_len):
        for t in words_list:
            if not words_list[index] == ',':
                sentence += t + ' '
            index += 1
    return sentence


def get_sentences(text:str):
    """Split the string s into a list of sentences."""
    if not (isinstance(text,str)):
        raise TypeError( "text must be a string" )
    pos = 0
    sentenceList = []
    l = len(text)
    while pos < l:
        try: p = text.index('.', pos)
        except: p = l+1
        try: q = text.index('?', pos)
        except: q = l+1
        try: e = text.index('!', pos)
        except: e = l+1
        end = min(p,q,e)
        sentenceList.append( text[pos:end].strip() )
        pos = end+1
    # If no sentences were found, return a one-item list containing
    # the entire input string.
    if len(sentenceList) == 0: sentenceList.append(text)
    return sentenceList