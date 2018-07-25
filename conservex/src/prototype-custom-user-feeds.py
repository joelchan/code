# """
# ---------------------------------------------
# 1 - Get data from sql tables into python pandas
# ---------------------------------------------
#
# Libraries used
#  - pymssql
#  - pandas
# """
# import pymssql # for interacting with sql db
# import pandas as pd
# import numpy as np
#
# def table_to_df(tableName, conn, dbName="ConservX"):
#     """
#     args:
#         tableName (str) - name of the table in the db that you want to grab
#         conn (object) - pymssql connection object that has been initialized
#         dbName (str) - name of the db in the mssql instance that we want to pull data from
#     """
#     stmt = "SELECT * FROM %s..%s" %(dbName, tableName)
#     df = pd.read_sql(stmt, conn)
#     return df
#
# print "Step 1: Fetching data from mssql db..."
# # 1.1 open the connection by creating a pymssql connection object
# SERVER = "127.0.0.1"
# PORT = 1401
# USR = "SA"
# PWD = "MegaC0gnition"
#
# CONN = pymssql.connect(server=SERVER, user=USR, password=PWD, port=PORT)
#
# # 1.2 grab the relevant tables
# users = table_to_df("AspNetUsers", CONN, "ConservX")
# # tasks = table_to_df("TaskPost", CONN, "ConservX") # skipping tasks for now, since there aren't many
# posts = table_to_df("PostCore", CONN, "ConservX")
# tags = table_to_df("SiteTag", CONN, "ConservX")
# post_tags = table_to_df("PostCore_Tag", CONN, "ConservX") # mapping between tags and posts
#
# """
# 2 - Make the user "documents" that we are going to match on
#
# Libraries used
#  - pandas
# """
#
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
#
# print "Step 2: Making user 'documents' from tags..."
# # 2.0 Filter down to users who meet 2 criteria:
# # 1. Have a complete profile (this means they have tags)
# # 2. Have a nonzero score
# # SKIP this step for the real deployment; this is just for the prototype
#
# # 2.1 Reconcile user tags with main tags table
# users['SkillsKnownLower'] = [str(s).decode('utf-8', 'ignore').encode('ascii', 'ignore').lower() for s in users['SkillsKnown']]
# users['SkillsToLearnLower'] = [str(s).decode('utf-8', 'ignore').encode('ascii', 'ignore').lower() for s in users['SkillsToLearn']]
#
# informative_users = users[(users['Completeness'] == 100)&(users['Score'] > 0)][['Id','Score', 'SkillsKnownLower', 'SkillsToLearnLower']]
# print informative_users.count()
#
#
# # preprocess the tag list, reconcile with site tags
# users['SkillsKnownLower'] = [str(s).decode('utf-8', 'ignore').encode('ascii', 'ignore').lower() for s in users['SkillsKnown']]
# known_skills = set()
# for skillset in users['SkillsKnownLower']:
#     if skillset != "none":
#         skills = skillset.split(",")
#         known_skills.update(skills)
# len(known_skills)
#
# users['SkillsToLearnLower'] = [str(s).decode('utf-8', 'ignore').encode('ascii', 'ignore').lower() for s in users['SkillsToLearn']]
# desired_skills = set()
# for skillset in users['SkillsToLearnLower']:
#     if skillset != "none":
#         skills = skillset.split(",")
#         desired_skills.update(skills)
# len(desired_skills)
# all_tags_list = list(known_skills.union(desired_skills))
#
# # filter down the tags table to only tags that are attached to users
# tags['NameLower_Joel'] = [t.lower() for t in tags['Name']]
# tags['IsSkill'] = 0
# for index, tag in tags.iterrows():
#     if tag['Name'].lower() in all_tags_list:
#         tags.set_value(index, "IsSkill", 1)
# skilltags = tags[tags['IsSkill'] == 1]
#
# informative_user_tags = []
#
# for index, user in informative_users.iterrows():
#
#     for tagType in ['SkillsKnownLower', 'SkillsToLearnLower']:
#
#         for tag in user[tagType].split(","):
#             # find the matching tag
#             matching_tag = skilltags[skilltags['NameLower_Joel'] == tag]
#
#             if len(matching_tag) > 0:
#                 informative_user_tags.append({
#                         'userId': user['Id'],
#                         'tagId': matching_tag['Id'].values[0],
#                         'tagName': tag,
#                         'tagType': tagType,
#                         'tagWeight': 1
#                     })
#
# informative_user_tags = pd.DataFrame(informative_user_tags)
#
# """
# 3 - Make similarity structures
#
# Libraries used:
# - Joel's convenience classes in jc_nlp.py
# - itertools (part of python base distribution)
# - gensim and all its dependencies (e.g., scipy, numpy)
#
# We're only relying on python-specific libraries up to this point
# This means that if we're clever, after this step is where we can (in theory) get away with just doing stuff in C#
#
# """
# from gensim.matutils import cossim
# import itertools as it # for combinations
# import jc_nlp
#
# print "Step 3: Making similarity structures..."
#
# print "\tLoading and initializing model..."
# # get the model
# gensimObject = jc_nlp.gensimObject(path_to_model="/Users/jchan/Projects/models/lsi_200_text8",
#                             path_to_dict="/Users/jchan/Projects/models/dictionary_text8")
# stoplist = jc_nlp.stopList()
#
# # initialize the model components
# model = gensimObject.model()
# dictionary = gensimObject.dictionary()
# stoplist = stoplist.allStops()
#
# #/************************
# # 3.1 Process the tags first
# #/************************
#
# print "\tVectorizing tags..."
# # vectorize tags
# tag_vecs = {}
# for index, tag in skilltags.iterrows():
#     lemm = jc_nlp.lemmatize_an_idea(tag['NameLower_Joel'], stoplist)
#     vec = model[dictionary.doc2bow(lemm)]
#     tag_vecs[tag['Id']] = vec
#
# print "\tComputing tag-tag similarities..."
# # calculate tag-tag similarities
# # dictionary has "tag1 TO tag2" keys, where tag1 and tag2 are in alphabetical order
# # TODO: optimize this step
# tag_similarities = {}
# for tagId1, tagId2 in it.combinations(skilltags['Id'], 2):
#     tag1 = tag_vecs[tagId1]
#     tag2 = tag_vecs[tagId2]
#     sim = cossim(tag1, tag2)
#     tag_similarities["%s TO %s" %(tagId1, tagId2)] = sim
#
# #/************************
# # 3.2 Process the tag-post similarities
# #/************************
#
# print "\tPre-processing and vectorizing posts..."
# # concatenate posts' title and content, since they're so short
# posts['title_content'] = ""
# for index, post in posts.iterrows():
#     post_title = post['Title'] if post['Title'] is not None else ""
#     post_content = post['MainText'] if post['MainText'] is not None else ""
#     combo = post_title + post_content
#     posts.set_value(index, 'title_content', combo)
#
# # vectorize the posts
# post_vecs = {}
# for index, post in posts.iterrows():
#     lemm = jc_nlp.lemmatize_an_idea(post['title_content'], stoplist)
#     vec = model[dictionary.doc2bow(lemm)]
#     post_vecs[post['Id']] = vec
#
# print "\tComputing tag-post similarities..."
# # calculate tag-post similarities
# # since we're focused on the tag as a query, we create a
# # data structure that has tags as keys, and a dictionary of posts as a value
# tag_post_similarities = {}
# for index, tag in skilltags.iterrows():
#     this_tag_similarities = {}
#     tag_vec = tag_vecs[tag['Id']]
#     for index, post in posts.iterrows():
#         sim = 0.0
#         if post['Id'] in post_vecs:
#             post_vec = post_vecs[post['Id']]
#             sim = cossim(tag_vec, post_vec)
#         this_tag_similarities[post['Id']] = sim
#     tag_post_similarities[tag['Id']] = this_tag_similarities
#
#
# """
# 4 - Rank posts by similarity to users (who are defined as tag documents)
#
# This is the core recommendation step
#
# Input(s):
#
# Output(s):
#  - user_post_rankings (pandas dataframe) - each row is a tagType-user-post combination that tells you
#                                            how similar a post is to a given user under a particular criterion (tagType)
#
# """
#
# import os
#
# print "Step 4: Ranking posts by similarity to users..."
#
# user_post_rankings = []
# # for each user
# for userId, userData in informative_user_tags.groupby("userId"):
#     # do known and tolearn skill tags separately
#     for tagType, tagTypeData in userData.groupby("tagType"):
#         # go through all the posts
#         for index, post in posts.iterrows():
#             tagSims = []
#             # get all the tags associated with this post
#             thisPostTags = post_tags[post_tags['PostId']==post['Id']]['TagId']
#             # aggregate similarity between post and all tags of this type for this user
#             for tagId in tagTypeData['tagId']:
#                 # if this tag is already associated with the post, then similarity = 1
#                 if tagId in thisPostTags:
#                     tagSims.append({'tagId': tagId, 'sim': 1.0})
#                 else:
#                     tagSims.append({'tagId': tagId, 'sim': tag_post_similarities[tagId][post['Id']]})
#             tagSims = pd.DataFrame(tagSims)
#             user_post_rankings.append({
#                     'userId': userId,
#                     'postId': post['Id'],
#                     'rankSum': np.sum(tagSims['sim']),
#                     'rankMean': np.mean(tagSims['sim']),
#                     'rankMax': np.max(tagSims['sim']),
#                     'rankType': tagType,
#                     'mostSimilarTagId': tagSims.sort_values(by="sim", ascending=False)['tagId'].values[0]
#                 })
# user_post_rankings = pd.DataFrame(user_post_rankings)
#
# """
# 5 - Print out prototypes to inspect recommendations
# """
#
# print "Step 5: Ranking posts by similarity to users..."
# # filter down posts to only the ones that "public"
# topic_filters = [
#     "discuss",
#     "ideas",
#     "problems"
# ]
# filtered_posts = posts[posts['TopicKey'].isin(topic_filters)]
#
# bigDivider = "*"*20
# smallDivider = "-"*10
#
# user_post_recommendations_filtered = []
# for userId, userData in informative_user_tags.groupby('userId'):
#     userPath = "/Users/jchan/Projects/conservationx/recommendations_postType-public_tags-originalSkills_sim-max/%s" %userId
#     if not os.path.exists(userPath):
#         os.mkdir(userPath)
#     f_profile = open(os.path.join(userPath, "profile_%s.txt" %userId), 'w')
#     out_profile = ""
#     out_profile += "%s\n" %bigDivider
#     out_profile += "%s\n" %userId
#     out_profile += "%s\n" %bigDivider
#     for recType in ["SkillsKnownLower", "SkillsToLearnLower"]:
#         out_profile += "%s: %s\n" %(recType, ", ".join(userData[userData['tagType'] == recType]['tagName']))
#     f_profile.write(out_profile)
#     f_profile.close()
#
#     for recType in ["SkillsKnownLower", "SkillsToLearnLower"]:
#         f_recs = open(os.path.join(userPath, "top10_%s_%s.txt" %(recType, userId)), 'w')
#         out_recs = ""
#         out_recs += "%s: %s\n" %(recType, ", ".join(userData[userData['tagType'] == recType]['tagName']))
# #         out_recs += "%s\n\n" %smallDivider
#         out_recs += "top 10 recs:\n\n"
#         user_posts = user_post_rankings[(user_post_rankings['postId'].isin(filtered_posts['Id'])) &
#                                         (user_post_rankings['userId']==userId) &
#                                         (user_post_rankings['rankType']==recType)
#                                        ].sort_values(by="rankMax", ascending=False)
#
#         rank=1
#         for index, post in user_posts.head(10).iterrows():
#             out_recs += "%s\n" %smallDivider
#             out_recs += "%s\n" %posts[posts['Id']==post['postId']]['Title'].values[0]
#             out_recs += "Rank: %i, SimRankScore: %.2f, PostID: %i\n" %(rank, post['rankMax'], post['postId'])
#             out_recs += "Top Matching Tag: %s\n" %tags[tags['Id'] == post['mostSimilarTagId']]['NameLower_Joel'].values[0]
#             out_recs += "%s\n" %smallDivider
#             out_recs += "%s\n\n" %posts[posts['Id']==post['postId']]['MainText'].values[0]
#             rank += 1
#             user_post_recommendations_filtered.append({
#                     'userId': userId,
#                     'recType': recType,
#                     'recTags': ", ".join(userData[userData['tagType'] == recType]['tagName']),
#                     'postId': post['postId'],
#                     'postRank': post['rankMax'],
#                     'postTitle': posts[posts['Id']==post['postId']]['Title'].values[0],
#                     'postContent': posts[posts['Id']==post['postId']]['MainText'].values[0],
#                     'mostSimilarTag': tags[tags['Id'] == post['mostSimilarTagId']]['NameLower_Joel'].values[0],
#                     'mostSimilarTagId': post['mostSimilarTagId']
#                 })
#         f_recs.write(out_recs)
#         f_recs.close()
# user_post_recommendations_filtered = pd.DataFrame(user_post_recommendations_filtered)
#
# print "Finished!"