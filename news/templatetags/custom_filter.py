from django import template

register = template.Library()

@register.filter()
def censor(value: str):

    bad_words = {'Бяка' : 'Б***',
                 'бяка' : 'б***',
                 'Кака' : 'К***',
                 'кака' : 'к***',
                 'фигня': 'ф****',
                 'Фигня': 'Ф****',
                 'Ерунда': 'Е*****',
                 'ерунда': 'е*****',
                 }

    words = value.split(' ')
    new_text = ''

    for i in range(len(words)):
        if words[i] in bad_words:
            words[i] = bad_words[words[i]]
            new_text += words[i]
            new_text += ' '
        else:
            new_text += words[i]
            new_text += ' '


    return new_text
