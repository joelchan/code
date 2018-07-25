from nltk.corpus import stopwords
from gensim import corpora, models
from gensim.utils import lemmatize
from gensim.matutils import cossim


class gensimObject:
    """
    Convenience object for loading and using an existing gensim model + dictionary.
    """
    def __init__(self, path_to_model, path_to_dict):
        self._model = models.LsiModel.load(path_to_model)
        self._dictionary = corpora.Dictionary.load(path_to_dict)

    def model(self):
        return self._model

    def dictionary(self):
        return self._dictionary

class stopList:
    """
    Simple stoplist object. Can add or remove custom stopwords.
    """
    def __init__(self):
        self._stoplist = set(stopwords.words('english'))
        self._custom = set()

    def addCustom(self, toAdd):
        self._stoplist.update(toAdd)
        self._custom.update(toAdd)

    def removeCustom(self, toRemove):
        self._stoplist.remove(toRemove)
        self._custom.remove(toRemove)

    def allStops(self):
        return self._stoplist

    def customStops(self):
        return self._custom


def lemmatize_an_idea(idea, stoplist):
    lemm = [lem[:-3] for lem in lemmatize(idea) if lem[:-3] not in stoplist]
#     lemm.extend(extract_number_concept(idea))
#     lemm.extend(add_back_quantity(idea))
    return lemm

def calculate_lsi_requested_sim_in_df(model, dictionary, doc1ID, doc2ID, doc_data, IDfield, contentField, stoplist):
    """
    Expects a dataframe that actually holds the text associated with each doc (which
    is just passed in as strings that denote the id)
    Built in some flexibility for different field naming conventions by making
    the IDfield and contentField variables
    """
    # sim_output = []
    # for pair in pairs:
    #     low_id = pair[0]
    #     high_id = pair[1]
    #     idea1 = lemmatize_an_idea(all_ideas[all_ideas.ideaID == low_id].idea.values[0])
    #     idea2 = lemmatize_an_idea(all_ideas[all_ideas.ideaID == high_id].idea.values[0])
    #     vec1 = model[dictionary.doc2bow(idea1)]
    #     vec2 = model[dictionary.doc2bow(idea2)]
    #     sim_output.append((low_id, high_id,cossim(vec1,vec2)))

    text1 = lemmatize_an_idea(doc_data[doc_data[IDfield] == doc1ID][contentField].values[0], stoplist)
    text2 = lemmatize_an_idea(doc_data[doc_data[IDfield] == doc2ID][contentField].values[0], stoplist)
    vec1 = model[dictionary.doc2bow(text1)]
    vec2 = model[dictionary.doc2bow(text2)]

    return cossim(vec1,vec2)

def calculate_lsi_requested_sim(model, dictionary, text1, text2, stoplist):
    """
    Base version that just takes in two strings and spits out a similarity in the provided gensim model space
    """

    text1_lemm = lemmatize_an_idea(text1, stoplist)
    text2_lemm = lemmatize_an_idea(text2, stoplist)
    vec1 = model[dictionary.doc2bow(text1_lemm)]
    vec2 = model[dictionary.doc2bow(text2_lemm)]

    return cossim(vec1,vec2)
