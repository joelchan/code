#%%
from gensim.models import FastText
import gensim
assert gensim.models.fasttext.FAST_VERSION > -1

sentences = [["cat", "say", "meow"], ["dog", "say", "woof"]]

model = FastText(sentences, min_count=1)
say_vector = model['say']  # get vector for word
of_vector = model['of']  # get vector for out-of-vocab word
print(say_vector, of_vector)

#%%
