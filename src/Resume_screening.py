#!/usr/bin/env python
# coding: utf-8


import numpy as np
import pandas as pd
import pdb
import re
import string
import spacy
import docx2txt
import json
from spacy.lang.en.stop_words import STOP_WORDS as stop_words
from spacy.lang.en import English
from spacy.matcher import Matcher


# Create our list of punctuation marks
punctuations = string.punctuation
parser = spacy.load("en_core_web_sm", disable=["tok2vec", "parser", "ner"])

nlp = spacy.load('en_core_web_trf')
matcher = Matcher(nlp.vocab)


def no_stopword_list(mytokens):
    mytokens = [ word.lemma_.lower().strip() if word.lemma_ != "-PRON-" else word.lower_ for word in mytokens ]
    mytokens = [ word for word in mytokens if word not in stop_words and word not in punctuations ]
    return mytokens


def spacy_tokenizer(sentence):
    # Creating our token object, which is used to create documents with linguistic annotations.
    mytokens = parser(sentence)

    # Lemmatizing each token and converting each token into lowercase
    mytokens = no_stopword_list(mytokens)
    return mytokens


def cleanResume(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText)  # remove URLs
    resumeText = re.sub('RT|cc', ' ', resumeText)  # remove RT and cc
    resumeText = re.sub('#\S+', '', resumeText)  # remove hashtags
    resumeText = re.sub('\n',',',resumeText)
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&()*+-/:;,<=>?[\]^_`{|}~"""), ' ', resumeText)  # remove punctuations
    resumeText = re.sub('[%s]' % re.escape("'"), '', resumeText)
    resumeText = re.sub(r'[^\x00-\x7f]',r' ', resumeText) 
    resumeText = re.sub('\s+', ' ', resumeText)  # remove extra whitespace
    return resumeText


def extract_name(nlp_text):
    
    
    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    
    matcher.add('NAME', [pattern])
    
    matches = matcher(nlp_text)
    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text



def companies_worked(doc):
    exp_start = [(tok, tok.i) for tok in doc if ((tok.text.lower() == "experience") and (tok.text == tok.text.upper()))]
    if exp_start:
        exp_start_num = exp_start[0][1]
        org = min([
            (X.start-exp_start_num,X) for X in doc.ents if X.label_ == 'ORG' and X.start>exp_start_num]+[(99999, None)])[1]
    else:
        exp_start = [(tok, tok.i) for tok in doc if ((tok.text.lower() == "experience") and (tok.text[0] == 'E'))]
        if exp_start:
            exp_start_num = exp_start[0][1]
            org = min([
                (X.start-exp_start_num,X) for X in doc.ents if X.label_ == 'ORG' and X.start>exp_start_num]+[(99999, None)])[1]
        else:
            org = None
    return org


def education(doc):
    education_start = [(tok, tok.i) for tok in doc if ((tok.text.lower() == "education") and (tok.text == tok.text.upper()))]
    if education_start:
        exp_start_num = education_start[0][1]
        edu=doc[exp_start_num+1:exp_start_num+5]
    elif education_start:
        education_start = [(tok, tok.i) for tok in doc if ((tok.text.lower() == "education") and (tok.text[0] == 'E'))]
        if education_start:
            exp_start_num = education_start[0][1]
            edu=doc[exp_start_num+1:exp_start_num+5]
    else:
        education_start = [(tok, tok.i) for tok in doc if ((tok.text.lower() == "career") and (tok.text[0] == 'C'))]
        if education_start:
            exp_start_num = education_start[0][1]
            edu=doc[exp_start_num+1:exp_start_num+5]
        else:
            edu = None
    return edu



# Initializie score counters for each area
def rating_score(text,terms):
    quality = 0
    operations = 0
    supplychain = 0
    project = 0
    data = 0
    healthcare = 0

    # Create an empty list where the scores will be stored
    scores = []
    skills = []

    # Obtain the scores for each area
    for area in terms.keys():

        if area == 'Quality/Six Sigma':
            for word in terms[area]:
                if word in text:
                    quality +=1
                    skills.append(word)
            scores.append(quality)

        elif area == 'Operations management':
            for word in terms[area]:
                if word in text:
                    operations +=1
                    skills.append(word)
            scores.append(operations)

        elif area == 'Supply chain':
            for word in terms[area]:
                if word in text:
                    supplychain +=1
                    skills.append(word)
            scores.append(supplychain)

        elif area == 'Project management':
            for word in terms[area]:
                if word in text:
                    project +=1
                    skills.append(word)
            scores.append(project)

        elif area == 'Data analytics':
            for word in terms[area]:
                if word in text:
                    data +=1
                    skills.append(word)
            scores.append(data)

        else:
            for word in terms[area]:
                if word in text:
                    healthcare +=1
                    skills.append(word)
            scores.append(healthcare)
    return scores, skills



def summary(my_text,terms):
    my_text_cleaned = cleanResume(my_text)
    nlp_text = nlp(my_text_cleaned)
    doc= nlp_text
    name = extract_name(nlp_text)
    emails = re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", my_text_cleaned)
    phone_number = re.findall(r"[\d]{3} [\d]{3} [\d]{3}", my_text_cleaned)
    gpe_locations = [(X.text, X.label_) for X in doc.ents if X.label_ == 'GPE']
    locations = [i[0] for i in gpe_locations[:5]]
    organisations_worked = companies_worked(doc)
    person_education = education(doc)
    scores,skills = rating_score(my_text_cleaned,terms)
    scores = dict(zip(terms.keys(), scores))
    return name,emails,phone_number,locations,organisations_worked,person_education,skills,scores

