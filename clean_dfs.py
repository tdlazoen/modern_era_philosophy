import numpy as np
import pandas as pd
import re
import us
import json
from modern_dfs import ModernPhilosophers, ModernDocuments

def determine_nationality(df):
	'''
	INPUT:
		df - dataframe containing philosopher data
	OUTPUT:
		df - dataframe with null nationalities filled in
			 (if the same row has a non-null birthplace)

	Determines the nationality of philosophers with null nationalities but non-null birthplaces based on their birthplace
	'''
	with open('data/nationalities.json', 'r') as f:
		nationality_dict = json.load(f)
	df_temp = df.fillna('')

	for i in range(df_temp.shape[0]):
		if not df_temp.loc[i, 'nationality'] and df_temp.loc[i, 'birthplace']:
			birthplace = re.split(r'\,', df.loc[i, 'birthplace'])[-1].strip()

			for country in nationality_dict.keys():
				if birthplace == country:
					df.loc[i, 'nationality'] = nationality_dict[country]
	return df

def remove_copyright(author, text):
	'''
	INPUT:
		author - author of document's name
		text - full text of document
	OUTPUT:
		text with copyright section removed

	Removes copyright sections from documents if they exist
	'''
	start = text.find('copyright')
	end = text[start:].find(author.split()[-1]) + start

	# Check if the start and end worked.  If not, just scrape entire text
	if not (start == -1 or end == -1):
		text = text[:start] + text[end-1:]
		name_first = text.find(author)
		idx = name_first + len(author)
		text = text[:idx] + text[idx:].replace(author, '')

	return text

if __name__ == '__main__':
	# Load dataframes
	phils = ModernPhilosophers()
	docs = ModernDocuments()

	# Pring out useful information
	print('# of Modern Authors with no documents: ', len([x for x in phils.df['name'] if x not in docs.df.author.values]))

	print('Modern Authors with no documents: ', [x for x in phils.df['name'] if x not in docs.df.author.values])

	print('Modern Authors with documents not in philosopher df: ', [x for x in np.unique(docs.df['author']) if x not in phils.df.name.values])

	print('Modern Authors with more than one document: ', len([x for x in np.unique(docs.df['author']) if docs.df[docs.df.author == x].shape[0] > 1]))

	print('Modern Authors with more than two documents: ', len([x for x in np.unique(docs.df['author']) if docs.df[docs.df.author == x].shape[0] > 2]))

	print('Documents with no year: ', docs.df[docs.df.year == 0].shape[0])

	print('Shape of Modern Philosopher dataframe: ', phils.df.shape)

	print('Shape of Modern Documents dataframe: ', docs.df.shape)

	print('Number of null nationalities: ', phils.df[phils.df.nationality.isnull()].shape[0])

	print('Number of null birthplaces: ', phils.df[phils.df.birthplace.isnull()].shape[0])

	print('Number of philosophers with birthplaces but no nationalities: ',
	phils.df[(phils.df.birthplace.notnull()) & (phils.df.nationality.isnull())].shape[0])
