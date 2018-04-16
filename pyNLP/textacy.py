#%%
from pyquery import PyQuery as q
import os
import textacy
en = textacy.load_spacy('en_core_web_lg')

xmlFilePath = os.path.join(os.getcwd(), 'assets', 'picf.xml');
with open(xmlFilePath,'r', encoding='utf8') as f:
    qxml = q(f.read())

#%% preprocess textacy
text = qxml("p:not(caption)").text();
text = textacy.preprocess.preprocess_text(text,
    lowercase=True, no_numbers=False,
    no_urls=True, no_emails=True, no_contractions=True)
text = textacy.preprocess.remove_punct(text, marks='()[]<>=;:,\n')
text = textacy.preprocess.normalize_whitespace(text)

print(text)
doc = textacy.Doc(text, lang=en)
print(doc)
#%% preprocess textacy
bot = doc.to_bag_of_terms(
     ngrams=(1, 2, 3), named_entities=True, weighting='count', normalize='lemma',
     as_strings=True, filter_stops=True, drop_determiners=True)

terms = sorted(bot.items(), key=lambda x: x[1], reverse=True)[:15]
# [print(n) for n in terms]

#better than singlerank or textrank
terms = textacy.keyterms.sgrank(doc, n_keyterms=30, window_width=50, ngrams=(1,2,3,4))
ner = textacy.keyterms.aggregate_term_variants(set([i[0] for i in terms]))

# print(ner)
[print(n) for n in ner]

