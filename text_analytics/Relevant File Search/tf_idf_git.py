
import pandas as pd
import PyPDF2 as pypdf2
import collections
import numpy as np
import string

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from os import listdir
import os.path
from os.path import isfile, join
import docx



file_path="insert a path containing .pdf and .docx files"

files_name= [file for file in listdir(file_path) if isfile(join(file_path,file))and (file.endswith('.pdf')or file.endswith('.docx') )]

def docx_reader(file):

    doc = docx.Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text

    return(text)


def pdf_reader(file):
    pdf_object = open(file, 'rb')
    pdfreader = pypdf2.PdfFileReader(pdf_object)

    num_pages = pdfreader.numPages
    c = 0
    text = ""
    while c < num_pages:
        pageObj = pdfreader.getPage(c)
        c += 1
        text += pageObj.extractText()

    return(text)


def tokenisation_df(file_content):


    d = [x.lower() for x in file_content.split()]
    file_content = ' '.join(d)
    table = str.maketrans({key: ' ' for key in string.punctuation})
    file_content = file_content.translate(table)
    stop_words = stopwords.words('english')
    s = [x for x in file_content.split() if x not in stop_words]
    file_content = ' '.join(s)
    tokens = word_tokenize(file_content)
    d = collections.Counter(tokens)

    keywords_df = pd.DataFrame.from_dict(d, orient='index').reset_index()
    keywords_df = keywords_df.rename(columns={'index': 'event', 0: 'freq'})
    return (keywords_df)


def text(x,z):
    switcher = {
        '.pdf': pdf_reader,
        '.docx': docx_reader,

    }

    y = switcher.get(x)

    return (y(z))


def main_df(files_name):
    keywords_final = pd.DataFrame()

    for file in files_name:

        filename=join(file_path,file)

        tex=text(os.path.splitext(filename)[1],filename)

        keywords_frequency=tokenisation_df(tex)

        keywords_frequency['File']=file
        keywords_frequency['TF']=keywords_frequency['freq']/sum(keywords_frequency['freq'])


        keywords_final=keywords_final.append(keywords_frequency, ignore_index=True)


    keywords_final['idf']=0


    for i in range(len(keywords_final)):

        sub=keywords_final.loc[keywords_final['event']==keywords_final['event'][i]]


        idf =np.log(len(np.unique(keywords_final['File']))/(1+len(sub)))

        if idf<0:
            keywords_final.loc[i, 'idf']=1
        else:
            keywords_final.loc[i, 'idf']=idf

    keywords_final['Tf_idf']=keywords_final['TF']*keywords_final['idf']
    return keywords_final



def rank_df(input_content):
    rank_matrix = pd.DataFrame()


    input_text=input_content

    token_df=tokenisation_df(input_text)
    keywords_final=main_df(files_name)
    #keywords_final=df

    for i in files_name:

        score=0

        for w in token_df['event']:

            sub_df=keywords_final.loc[(keywords_final['event']==w) & (keywords_final['File']==i)]

            if len(sub_df)==0:
                score=score
            else:

                score=score+float(sub_df['Tf_idf'])

        rank_matrix=rank_matrix.append({'File':i,'Score':score},ignore_index=True)

    return(rank_matrix)



Relevancy_files= rank_df('enter keywords to search')
Relevancy_files= Relevant_files.sort_values(by='Score', ascending=False)










