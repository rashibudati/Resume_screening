import json
import docx2txt
from Resume_screening import *

with open('key_terms.json') as f:
    terms = json.loads(f.read())

def screening(resume_path):
    my_text = docx2txt.process(resume_path)
    name,emails,phone_number,locations,organisations_worked,person_education,skills,scores = summary(my_text,terms)
    return dict(zip("Name of candidate,E-mail address,Phone no,Current City,Companies Worked,Colleges/schools,Experience/Skills,Rating".split(","),
    [name,emails,phone_number,locations,organisations_worked,person_education,skills,scores]))


if __name__ =='__main__':
    resume_path = r'C:\Users\Rashi Budati\Desktop\Borneo\dataset\Resumes\Adelina_Erimia_PMP1.docx'
    summary_of_candidate = screening(resume_path)
    print(summary_of_candidate)



