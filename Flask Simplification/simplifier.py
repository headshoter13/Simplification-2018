from flask import Flask, request, render_template
import pymorphy2
import re


def search(query):
    result_final = ''
    morph = pymorphy2.MorphAnalyzer()
    text = preprocess(query)
    for sentence in text:
        sentence_splitted, all_pos = structure(morph,sentence) #Части речи
        dotted_sentence = simple_structure(sentence_splitted, all_pos, sentence)
        cut_sent = delete_words(dotted_sentence, morph)
        result = final_text(cut_sent)
        result_final += result + '\n\n'
    print (result_final)
    return result_final
        
    
def final_text(cut_sent):
    result = ''
    
    cut_sent = cut_sent.split('.')
    for sent in cut_sent:
        if sent == '':
            cut_sent.remove(sent)
    for element in cut_sent:
        element = element.capitalize()
        if element != '' and element != ' ':
            result += element + '. '
            
    
    return result

def delete_words(dotted_sentence,morph):
    result = ''
    cut_sent = dotted_sentence.split('.')
    cut_sent = [sent.strip() for sent in cut_sent]
    for sentence in cut_sent:
        sentence = sentence.lower()
        sentence = sentence.replace(' какой-либо', '')
        sentence = sentence.replace(' какому-либо', '')
        sentence = sentence.replace(' какая-либо', '')
        sentence = sentence.replace(' какое-либо', '')
        sentence = sentence.replace('кроме того', '')
        sentence_splitted, all_pos = structure(morph,sentence)

        prcl_pos_numb = []          #Позиции частиц
        for i in range(len(all_pos)):    #Позиции частиц
            if all_pos[i] == 'PRCL':
                prcl_pos_numb.append(i)

        for i in range(len(all_pos) - 1):
            number_pos = i
            if all_pos[i] == 'PRCL' and sentence_splitted[number_pos] != 'не' and sentence_splitted[number_pos] != 'ни':
                sentence = sentence.replace(' ' + sentence_splitted[number_pos], '')
            if all_pos[i] == 'ADVB' and (all_pos[i + 1] == 'NOUN' or all_pos[i + 1] == 'ADJF'):
                sentence = sentence.replace(' ' + sentence_splitted[number_pos], '')
            if all_pos[i] == 'ADJF' and all_pos[i + 1] == 'ADJF' == 'ADJF':
                sentence = sentence.replace(' ' + sentence_splitted[number_pos + 1], '')

        for i in range(len(all_pos) - 2):
            if len(sentence_splitted) == 3 and all_pos[i] == 'NOUN' and all_pos[i + 1] == 'CONJ' and all_pos[i + 2] == 'NOUN':
                sentence = ''
        result += sentence + '.'   

    
    return result
        

def structure(morph, sentence):
    all_pos = []
    pos_dict = {}
    pos_dict_rev = {}
    sentence_splitted = sentence.split()
    words = re.findall(r"[\w']+", sentence)
    for word in words:
        all_pos.append(morph.parse(word)[0].tag.POS)

    return sentence_splitted, all_pos

                
def simple_structure(sentence_splitted, all_pos, sentence):
    result_delims = 0
    delims = [',',':',';', ' – ']
    for delim in delims:
        if delim in sentence:
            result_delims += 1
    if result_delims > 0:
        dotted_sent = sentence
        verbs_pos_numb = []          #Позиции глагола
        nouns_pos_numb = []          #Позиции сущ

        for i in range(len(all_pos)):    #Позиции глагола
            if all_pos[i] == 'VERB' or all_pos[i] == 'INFN':
                verbs_pos_numb.append(i)

        for i in range(len(all_pos)):    #Позиции сущ
            if all_pos[i] == 'NOUN' or all_pos[i] == 'NPRO':
                nouns_pos_numb.append(i)
                     
        for i in range(len(all_pos) - 1):
            if all_pos[i] == 'CONJ' or all_pos[i] == 'PREP':
                number_pos = i
                if sentence_splitted[i - 1][-1] == ',':
                    if 'VERB' in all_pos[: number_pos + 1] and 'VERB' in all_pos[number_pos:]:
                        dotted_sent = dotted_sent.replace(', ' + sentence_splitted[i], '.')
                    if 'VERB' in all_pos[: number_pos + 1] and 'NOUN' in all_pos[number_pos:]:
                        dotted_sent = dotted_sent.replace(', ' + sentence_splitted[i], '.')
                if i == 0:
                    min_verb_pos = min(verbs_pos_numb)
                    if sentence_splitted[min_verb_pos][-1] == ',':
                        dotted_sent = dotted_sent.replace(sentence_splitted[min_verb_pos], sentence_splitted[min_verb_pos][:-1] + '.')
                if ':' in sentence:
                    dotted_sent = dotted_sent.replace(':', '. ')
                if sentence_splitted[i][-1] == ',' and all_pos[i + 1] == 'CONJ':
                    dotted_sent = dotted_sent.replace(sentence_splitted[i], '.')
                    dotted_sent = dotted_sent.replace(', . ' + sentence_splitted[i + 1], '. ')     

            if ' – ' in sentence and len(verbs_pos_numb) == len(nouns_pos_numb):
                    dotted_sent = dotted_sent.replace(' – ', '. ')

        if '.' and ',' in sentence:
            n_dots = dotted_sent.count('.')
            n_commas = dotted_sent.count(',')
            n_verbs = len(verbs_pos_numb)
            if n_dots < n_verbs and n_dots <= n_commas and n_commas < n_verbs:
                dotted_sent = dotted_sent.replace(', ', '. ')
                        
                
        return dotted_sent
                
    else:
        return sentence


    
def preprocess(message):
    text = message
    text = text.replace('?', '.')
    text = text.replace('!', '.')
    text = text.replace('\n', '')
    text = text.replace(',', ', ')
    text = re.sub(r'\s+', ' ', text)
    text = text.split('.')
    text = [sent.strip() for sent in text]
    for sentence in text:
        if sentence == '':
            text.remove(sentence)
    return text




app = Flask(__name__)

 
@app.route('/')
def index():
    if request.args:
        query = request.args['query']
        links = search(query)
        return render_template('index.html',links=links)
    return render_template('index.html',links=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)
