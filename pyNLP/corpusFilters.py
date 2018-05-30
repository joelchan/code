venueNames =[
        "Nature",
        "Science",
        "Proceedings of the National Academy of Sciences of the United States of America",
        "Expert Syst.Appl.",
        "IEEE Communications Letters",
        "Plos One"
    ]

keepList =["brain",
    "neuro",
    "cogn",
    "psychol",
    "comput",
    "acm",
    "sigchi",
    "interaction",
    "cscw",
    "info",
    "visualization",
    "learning",
    "statisti",
    "design",
    "user",
    "interface",
    "behavior",
    "social",
    "creativ",
    "software"]

removeList = ['cryptography', 'animal', 'rat', 'mice', 'geneti','radiology',
              'surg', 'medic', 'physics', 'sex', 'chemi', 'clinic', 'doctor', 'nurse', 'patient',
              'disease', 'blood', 'nucle', 'tissue', 'protein','peptide', 'dna', 'rna', 'acid']

def keepRemove(keepList, removeList, searchString):
    for strToMatch in removeList:
        if strToMatch.lower() in searchString.lower():
            return False

    for strToMatch in keepList:
        if strToMatch.lower() in searchString.lower():
            return True

def filterByVenue(article):
    venue = article["venue"].lower();
    hasVenue = len(article["venue"]) > 0
    hasJournalName = len(article['journalName']) > 0
    hasAbstract = len(article['paperAbstract']) > 0

    if (not hasVenue and not hasJournalName):
        return False

    if not hasAbstract:
        return False

    if (not hasVenue and hasJournalName):
        venue = article['journalName'].lower()

    if venue in venueNames:
        ents = [item for sublist in article['entities'] for item in sublist]
        searchString = ents.lower() + ' ' + article['paperAbstract'].lower() + ' ' + article['title']
        return keepRemove(keepList, removeList, searchString)

    return keepRemove(keepList, removeList, article['paperAbstract'].lower())

    return False

#venue better than journal. journal more often empty
def venueJournalDifferent(corpusItem):
    if corpusItem['venue'] != corpusItem['journalName']:
        print('***************************************')
        print('VENUE: ' + corpusItem['venue'])
        print('Journal: ' + corpusItem['journalName'])
        return True
    else:
        return False

# saveCsv(calcFrequences(bag1, 'venue'), 'venue_freqs.csv')


# bag2 = bag1.filter(filterByJournal)
# bag2.to_textfiles(outDir, name_function=None,
#              encoding='utf-8', compute=True, get=None, storage_options=None)
# print(len(filteredArticles))



#%%

# print(set([p['journalName'] for p in papers if 'IEEE' in p['journalName']]))
#%%


# papers = []
# for i,s in enumerate(corpusString.strip().split('\n')):
#     try: # deal with entries that error
#         papers.append(json.loads(s))
#     except:
#         print('error for: ', i)
#         continue
# # print(len(papers))

#%%

# bag1 = corpusFilesToDaskBag(corpusPath)
# def venueJournalDifferent(corpusItem):
#     if corpusItem['venue'] == corpusItem['journalName']:
#         print('VENUE: ' + corpusItem['venue'])
#         print('VENUE: ' + corpusItem['journalName'])
#
#     else:
#         return True