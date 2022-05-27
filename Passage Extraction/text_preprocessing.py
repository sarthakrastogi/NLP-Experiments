import re

def remove_email(text):
    if text:
        text = text.lower()
        text = re.sub('([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})',' ',str(text))
    else:
        pass
    return text


def remove_weblink(text):
    if text:
        text=text.lower()
        text = re.sub('(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})','link',str(text))
    else:
        pass
    return text


# Function for removing paper refrences from text e.g [19],[1a,2b] or [19,14,15]
def remove_reference(text):
    if text:
        text=text.lower()
        text = re.sub('\[\d+(,\s{0,}\d+){0,}\]','',str(text))   
    else:
        pass
    return text


# Function for removing non ASCII charecters like 'Ϫ','ó','ü','©','µ','▲','→'
# This function check if charecter hex value in range [\x00,\x7F] (in decimal [0,127] i.e range of ASCII charecters) and replace if it occurs outside limit
def remove_ghost_char(text):
    if text:
        text = re.sub(r'[^\x00-\x7F]+',' ', str(text))
    else:
        pass
    
    return text


# This function remove all brackets with data
def remove_brackets(text):
    if text:
        text = re.sub('(\(.*?\))|(\[.*?\])','',str(text))   
    else:
        pass
    return text



# Function for removing multiple spaces 
def remove_extra_spaces(text):
    if text:
        text = re.sub(r'( +)',' ', str(text))
    else: 
        pass
   
    return text


