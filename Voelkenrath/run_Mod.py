'''
import sys

import result
import jparsing
import data_save
import clustering
import pdf_globing
import w2v_training
import xlsx_postprocessing
import data_preprocessing_spacy
'''

from gensim.models import Word2Vec

import clustering
import matplotlib.pyplot as plt
import matplotlib as mpl


model_test = Word2Vec.load("./models/methanation_only_text_mc10")

clusters, labels, d3dendro = clustering.w2v_to_json_mod(model_test, "methanation_only_text_mc10")


# set up plot
fig, ax = plt.subplots(figsize=(17, 9)) # set size
ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling

x = [clusters[i][0] for i in range(len(clusters))]
y = [clusters[i][1] for i in range(len(clusters))]

ax.plot(x,y,marker = 'o', linestyle = '', ms = 12, label = labels, color = '#1b9e77', mec = 'none')
ax.set_aspect('auto')
ax.tick_params(\
    axis= 'x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='off')
ax.tick_params(\
    axis= 'y',         # changes apply to the y-axis
    which='both',      # both major and minor ticks are affected
    left='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelleft='off')


'''
from scipy.cluster.hierarchy import ward, dendrogram

linkage_matrix = ward(dist) #define the linkage_matrix using ward clustering pre-computed distances

fig, ax = plt.subplots(figsize=(15, 20)) # set size
ax = dendrogram(linkage_matrix, orientation="right", labels=titles);

plt.tick_params(\
    axis= 'x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom='off',      # ticks along the bottom edge are off
    top='off',         # ticks along the top edge are off
    labelbottom='off')

plt.tight_layout() #show plot with tight layout

#uncomment below to save figure
plt.savefig('ward_clusters.png', dpi=200) #save figure as ward_clusters
'''
#a = model_test.wv.index_to_key

#import pandas as pd

#df = pd.DataFrame(a)

#df.to_excel('Concept_list_CFI_MOD.xlsx')



'''
def textmining(name, mincount):
    # function which calls every needed script
    # set a higher max recursion limit
    max_rec = sys.getrecursionlimit()
    sys.setrecursionlimit(100000)

    name_raw = name + "_raw"

    # extracting text out of PDF files and save string
    print('Extracting text of PDF...')
    data_raw = pdf_globing.get_globed_content()
    data_save.save_pickle(data_raw, name_raw)
    print('Done!')

    # preprocessing text and save string
    print('Preprocessing text...')
    data_prep = data_preprocessing_spacy.preprocessing(data_raw)
    data_save.save_pickle(data_prep, name)
    print('Done!')

    # training Word2Vec model, clustering and creating first json-file
    print('Training Word2Vec...')
    model = w2v_training.create_model(data_prep, mincount)
    name_model = name + '_mc' + str(mincount)
    model.save('./models/' + name_model)
    print('Done!')

    # clustering data and create a json file
    print('Clustering Data and creating a json-file...')
    clustering.w2v_to_json(model, name_model)
    print('Done!')

    # extract hypernyms
    print('Extracting hypernyms...')
    df = jparsing.parsing(name_model)
    print('Done!')

    # calculate accuracy
    print('Calculate accuracy...')
    result_lists = result.calculate(df, model, name)
    print('Done!')

    # creating xlsx file
    xlsx_postprocessing.postprocessing(df, name)

    # reset recursion limit
    sys.setrecursionlimit(max_rec)
    return result_lists, df


'''

