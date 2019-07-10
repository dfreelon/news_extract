# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 11:23:28 2018

@author: freelon
"""

import collections
from datetime import datetime
import json
import pandas as pd
import re
from .striprtf2 import striprtf2
import unicodedata

### OLD NEXIS REGEXES ###

re_split_ln = re.compile('[0-9]+\sof\s[0-9]+\sDOCUMENTS')
re_get_field_names = re.compile('(?<=\n\n)([A-Z]+?\:\s)(?!\s)')
re_get_fields = re.compile('(?<=\n\n)(?:[A-Z]+?\:\s)(?!\s)(.+?)(?=\n{2,}|$)',re.DOTALL)
re_field_sub = re.compile('[^A-Z]')
re_get_body_field = re.compile('(?:LENGTH\:\s[0-9]+?\s+?words\n+?)(.+?)(?:\n\n[A-Z]+\:\s[A-Z]{3,})',re.DOTALL)
re_get_date_field = re.compile('[A-Za-z]+?\s[0-9]{1,2}\,\s[0-9]{4}')
re_get_pub_field = re.compile('(?:\s+)(.+?)(?=\n)')
re_get_headline_field = re.compile('(?:\d{4}.*?\n\n)(.+?)(?=\n\n)',re.DOTALL)

### NEXISUNI REGEXES ###

re_date_nu = re.compile("\w+\s\d{1,2},\s\d{4}")
re_section_nu = re.compile("(?<=Section: )(.+)")
re_length_nu = re.compile("(?<=Length: )(\d+)(?= words)")
re_byline_nu = re.compile("(?<=Byline: )(.+)")
re_byline2_nu = re.compile("([A-Z\-\s]+)(?=[^A-Z\-\s])")
re_anchors_nu = re.compile("(?<=Anchors: )(.+)")
re_geo_nu = re.compile("(?<=Geographic: )(.+)")

### FACTIVA REGEXES ###

re_split_factiva = re.compile('\nDocument .+\n\n+')
re_get_field_names2 = re.compile('\*[A-Z]{2}\*')
re_get_field_names3 = re.compile('\*[A-Z]{3}\*')
re_get_fields2 = re.compile('(?<=\*[A-Z]{2}\*)(.+?)(?=\s+\*[A-Z]{2,}\*)',re.DOTALL)
re_get_fields3 = re.compile('(?<=\*[A-Z]{3}\*)(.+?)(?=\s+\*[A-Z]{2,}\*)',re.DOTALL)

### SHARED REGEXES ###

re_fix_whitespace = re.compile('\s+')

### CURRENTLY UNUSED REGEXES ###

re_get_housereps = re.compile('(?:Rep\. )([A-Za-z\.\s]+)(?: \(|\,| of)')
re_get_senators = re.compile('(?:Sen\. )([A-Za-z\.\s]+)(?: \(|\,| of)')

### FUNCTIONS ###

def nexis_rtf_extract(nex_rtf):
    is_filename = nex_rtf[-4:].lower() == '.rtf'
    if is_filename:
        rtf_str = open(nex_rtf,"r").read()
        nex_str = striprtf2(rtf_str)
    else:
        nex_str = nex_rtf
    nex_str = unicodedata.normalize('NFKD',nex_str)
    nex_articles = nex_str.split("End of Document")[:-1]
    nex_list = [] 
    
    for x,nex in enumerate(nex_articles):
        nex_dict = {}
        nex_split = nex.split("\n")
        nex_split = [i for i in nex_split if i != '']
        #fields
        headline = nex_split[0]
        outlet = nex_split[1]
        date_str = re_date_nu.findall(nex_split[2])[0]
        pub_date = datetime.strptime(date_str,
                                  "%B %d, %Y").isoformat()[:10]
        try:
            sec_index = [n for n,i 
                         in enumerate(nex_split) 
                         if i[:8] == "Section:"][0]
            section = re_section_nu.findall(
                            nex_split[sec_index])[0]
        except IndexError:
            section = ""
        try:
            ct_index = [n for n,i 
                        in enumerate(nex_split) 
                        if i[:7] == "Length:"][0]
            word_ct = int(
                        re_length_nu.findall(
                                   nex_split[ct_index])[0])
        except (IndexError,ValueError):
            word_ct = 0    
        #bylines are a little tricky    
        try:
            by_index = [n for n,i 
                        in enumerate(nex_split) 
                        if i[:7] == "Byline:"][0]
            byline = re_byline_nu.findall(
                          nex_split[by_index])[0]
        except IndexError:
            by_index = None
        if by_index is None:
            try:
                by_index = [n for n,i 
                            in enumerate(nex_split) 
                            if i[:8] == "Anchors:"][0]
                byline = re_anchors_nu.findall(
                                nex_split[by_index])[0]
            except IndexError:
                by_index = None
            
        try:
            loc_index = [n for n,i 
                        in enumerate(nex_split) 
                        if i[:11] == "Geographic:"][0]
            loc = re_geo_nu.findall(nex_split[loc_index])[0]
        except IndexError:
            loc = ""
        body_start = [n for n,i 
                      in enumerate(nex_split) 
                      if i == "Body"][0] + 1
        body_end = [n for n,i 
                    in enumerate(nex_split) 
                    if i == "Classification"][0]
        body_text = " ".join(nex_split[body_start:body_end])
        
        if by_index is None:
            try:
                byline = re_byline2_nu.findall(body_text)[0]
            except IndexError:
                byline = ""
        if len(byline) == 1:
            byline = ""
        
        nex_dict['HEADLINE'] = headline
        nex_dict['OUTLET'] = outlet
        nex_dict['DATE'] = pub_date
        nex_dict['SECTION'] = section
        nex_dict['LENGTH'] = word_ct
        nex_dict['BYLINE'] = byline
        nex_dict['LOCATION'] = loc
        nex_dict['BODY'] = body_text
        if is_filename:
            nex_dict['FILENAME'] = nex_rtf
        else:
            nex_dict['FILENAME'] = ""
        nex_list.append(nex_dict)

    return nex_list

def factiva_extract(article_fn):
    factiva_list = []
    txt = open(article_fn,encoding='utf8').read()
    txt = re_split_factiva.split(txt)[:-1]
    for t in txt:
        field_names2 = [fn.replace('*','') 
                        for fn 
                        in re_get_field_names2.findall(t)]
        field_names3 = [fn.replace('*','') 
                        for fn
                        in re_get_field_names3.findall(t)]
        field_names3.append('TXT')
        fields2 = [f.strip() 
                   for f 
                   in re_get_fields2.findall(t)]
        fields3 = [f.strip()
                   for f
                   in re_get_fields3.findall(t)]
        fields3.append('')
        
        article_dict2 = dict(zip(field_names2,fields2))
        article_dict3 = dict(zip(field_names3,fields3))
        
        if 'LP' in article_dict2: 
            article_dict3['TXT'] += article_dict2['LP'] 
            del article_dict2['LP']
        if 'TD' in article_dict2:
            article_dict3['TXT'] += " " + article_dict2['TD'] 
            del article_dict2['TD']
        article_dict3['TXT'] = re_fix_whitespace.sub(
                               ' ',article_dict3['TXT'])
        
        article_dict = {}
        article_dict.update(article_dict2)
        article_dict.update(article_dict3)
        article_dict['FILENAME'] = article_fn
        article_dict['PD'] = datetime.strptime(
                             article_dict['PD'],
                             '%d %B %Y').isoformat()[:10]
        article_dict['WC'] = int(article_dict['WC'].replace(
                             " words",""))
        factiva_list.append(article_dict)
        
    return factiva_list

def fix_fac_fieldnames(factiva_list):
    fff_dict = {"SE":"SECTION",
                "HD":"HEADLINE",
                "PD":"DATE",
                "WC":"LENGTH",
               "TXT":"BODY",
                "SN":"OUTLET",
                "RE":"LOCATION",
                "BY":"BYLINE"}
    
    for n,i in enumerate(factiva_list):
        for j in fff_dict:
            if j in factiva_list[n]:
                factiva_list[n][fff_dict[j]] = factiva_list[n][j]
                del factiva_list[n][j]
    return factiva_list
        
def news_export(news_list,
                to_pandas=True,
                fn_template='nexis',
                jacc_threshold=0.75,
                show_dup_rows=True,
                master_fields=[],
                field_threshold=0.5,
                dup_days=14):   
    news_dates = []
    remove_rows = []
    for n,i in enumerate(news_list):
        try:
            news_dates.append(datetime.strptime(i['DATE'],
                                                "%Y-%m-%d"))
        except ValueError:
            remove_rows.append(n)
    
    news_list = [i for n,i 
                 in enumerate(news_list) 
                 if n not in remove_rows]
    
    print("Removed",len(remove_rows),"articles with bad dates.")
    dup_split = [set(i['BODY'].split()) for i in news_list]
    dup_rows = []
    news_len = len(news_list)
    
    for n,i in enumerate(dup_split):
        for x,j in enumerate(dup_split):
            day_diff = abs(news_dates[x] - news_dates[n]).days
            if x > n and len(j) > 0 and day_diff <= dup_days:
                jacc = len(dup_split[n].intersection(dup_split[x]))/ \
                       len(dup_split[n].union(dup_split[x]))
                if jacc >= jacc_threshold:
                    dup_rows.append(x)
        if n % 100 == 0:
            print(100*n/news_len,"% done.")
    
    remove_list = set(dup_rows)                    
    n_dups = len(remove_list)
    print(n_dups,'duplicates removed.')
    if show_dup_rows == True:
        print(dup_rows)
    news_list = [i for n,i 
                 in enumerate(news_list) 
                 if n not in remove_list]
    
    if master_fields != []:
        master_fields = sorted(master_fields)
    else:
        for a in news_list:
            master_fields.extend(list(a.keys()))
        master_top = collections.Counter(master_fields).most_common()
        n_articles = len(news_list)
        master_fields = [i[0] 
                         for i 
                         in master_top 
                         if i[1]/n_articles >= field_threshold]
        master_fields = sorted(list(set(master_fields)))
    
    if to_pandas == True:
        to_df_list = []
        for a in news_list:
            article_list = []
            for f in master_fields:
                try:
                    article_list.append(a[f])
                except KeyError:
                    article_list.append('')
            to_df_list.append(article_list)
        
        news_df = pd.DataFrame(to_df_list,columns=master_fields)
        return news_df

    else:
        nlen = len(str(len(news_list)))
        for n,a in enumerate(news_list):
            for f in master_fields:
                if f not in a:
                    a[f] = ''
            with open(fn_template + '_' + 
                      str(n+1).zfill(nlen) + 
                      '.json','w') as f:
                f.write(json.dumps(a))
                
#old nexis extraction code
def ln_extract(article_fn):
    ln_list = []
    txt = open(article_fn,encoding='utf8').read()
    txt = re_split_ln.split(txt)[1:]
    for n,t in enumerate(txt):
        field_names = []
        fields = []
        field_names.append('BODY')
        try: 
            fields.append(re_get_body_field.findall(t)[0] + '.')
        except IndexError:
            print("Fulltext not found for article at index",n,"in file",article_fn)
            continue
        field_names.append('DATE')
        try:
            iso_date = datetime.strptime(
                       re_get_date_field.findall(t)[0],
                       "%B %d, %Y").isoformat()[:10]
        except ValueError:
            print("No date found for article",
                   n,"in file",article_fn)
            continue
        fields.append(iso_date)
        field_names.append('PUBLICATION')
        fields.append(re_get_pub_field.findall(t)[0].strip())
        field_names.append('HEADLINE')
        try:
            fields.append(re_get_headline_field.findall(t)[0].strip())
        except IndexError:
            print("Year not found for article",n,"in file",article_fn)
            continue            
        field_names.append('FILENAME')
        fields.append(article_fn)
        
        field_names.extend([re_field_sub.sub('',fn)
                            for fn 
                            in re_get_field_names.findall(t)])
        fields.extend([f.strip() 
                       for f 
                       in re_get_fields.findall(t)])
        
        article_dict = dict(zip(field_names,fields))
        article_dict['LENGTH'] = article_dict['LENGTH'].replace(
                                 " words","")
        if len(fields) != len(field_names):
            article_dict['BROKEN'] = True
        else:
            article_dict['BROKEN'] = False
        ln_list.append(article_dict)
    
    for n,i in enumerate(ln_list):
        for j in i:
            if j != "BROKEN":
                ln_list[n][j] = re_fix_whitespace.sub(' ',
                                   ln_list[n][j])
    return ln_list