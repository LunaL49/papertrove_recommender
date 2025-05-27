
from supabase import create_client
import numpy as np
import ast
import os

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

users = supabase.table("users").select("*").execute()
users = users.data

papers = supabase.table("latest_papers").select("*").execute()
papers = papers.data

for i in range(0, len(users)):
  user_pref_vec = users[i]["embedding"]
  user_pref_vec = np.asarray(ast.literal_eval(user_pref_vec), dtype=np.float32)
  similarities = []

  for j in range(0, len(papers)):
    doi_vec = papers[j]["embedding"]
    doi_vec = np.asarray(ast.literal_eval(doi_vec), dtype=np.float32)
    similarities.append(np.dot(user_pref_vec, doi_vec))

    rank = np.flip(np.argsort(similarities), axis=0) # sort the index, highest similarity first
    best_fit = rank[:users[i]["digest_length"]] # take the top x items

  if len(papers) > 0: # only do this part if there are actually new papers
    for n in range(0,len(best_fit)):
      index = best_fit[n]
      if similarities[index]>0.7:
        data = {
          "user_email": users[i]["email"],
          "doi": papers[index]["doi"],
          "title": papers[index]["title"],
          "abstract": papers[index]["abstract"],
          "author": papers[index]["author"],
          "link": papers[index]["link"],
          "score": float(similarities[index])
        }
        response = supabase.table("recommendations").insert(data).execute()
        if response.data:
          print("added one paper to recommendations")

supabase.table("latest_papers").delete().neq('id', '00000000-0000-0000-0000-000000000000').execute() # delete all rows in the latest_papers database