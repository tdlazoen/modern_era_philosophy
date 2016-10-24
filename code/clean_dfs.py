import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import us
from modern_dfs import ModernPhilosophers, ModernDocuments

# Determines nationality based off of birthplace
def determine_nationality(df):

	df_temp = df.fillna('')
	for i in range(df_temp.shape[0]):
		if not df_temp.loc[i, 'nationality'] and df_temp.loc[i, 'birthplace']:
			birthplace = re.split(r'\,', df.loc[i, 'birthplace'])[-1].strip()

			if birthplace == 'greece' or birthplace == 'turkey':
				df.loc[i, 'nationality'] = 'greek'

			elif birthplace == 'italy':
				df.loc[i, 'nationality'] = 'italian'

			elif birthplace == 'france':
				df.loc[i, 'nationality'] = 'french'

			elif birthplace == 'germany':
				df.loc[i, 'nationality'] = 'german'

			elif birthplace == 'united kingdom':
				df.loc[i, 'nationality'] = 'british'

			elif birthplace == 'united states':
				df.loc[i, 'nationality'] = 'american'

			elif birthplace == 'poland':
				df.loc[i, 'nationality'] = 'poland'

			elif birthplace == 'ireland':
				df.loc[i, 'nationality'] = 'irish'

			elif birthplace == 'austria':
				df.loc[i, 'nationality'] = 'austrian'

			elif birthplace == 'algeria':
				df.loc[i, 'nationality'] = 'algerian'

			elif birthplace == 'iran':
				df.loc[i, 'nationality'] = 'iranian'

			elif birthplace == 'netherlands':
				df.loc[i, 'nationality'] = 'dutch'

			elif birthplace == 'israel':
				df.loc[i, 'nationality'] = 'israeli'

			elif birthplace == 'egypt':
				df.loc[i, 'nationality'] = 'egyptian'

			elif birthplace == 'jordan':
				df.loc[i, 'nationality'] = 'jordanian'

			elif birthplace == 'south africa':
				df.loc[i, 'nationality'] = 'south african'

			elif birthplace == 'spain':
				df.loc[i, 'nationality'] = 'spanish'

			elif birthplace == 'czech republic':
				df.loc[i, 'nationality'] = 'czech'

	return df

# Changes american birthplaces from city, state to state, country
def american_birthplaces(df):
	df_temp = df.fillna('')

	for i in range(df_temp.shape[0]):
		if df_temp.loc[i, 'nationality'] == 'american' and df_temp.loc[i, 'birthplace']:
			birthplace = re.split(r',', df.loc[i, 'birthplace'])[-1].strip()
			print(birthplace)
			if len(birthplace) > 2:
				continue
			df.loc[i, 'birthplace'] = us.states.lookup(birthplace).name.lower() + ', united states'

	return df

# Removes copyright sections from documents
def remove_copyright(author, text):
	start = text.find('copyright')
	end = text[start:].find(author) + start

	# Check if the start and end worked.  If not, just scrape entire text
	if not (start == -1 or end == -1):
		text = text[:start] + text[end-1:]
		name_first = text.find(author)
		idx = name_first + len(author)
		text = text[:idx] + text[idx:].replace(author, '')

	return text

if __name__ == '__main__':
	phils = ModernPhilosophers()
	docs = ModernDocuments()
	print('Modern Authors with no documents: ', len([x for x in phils.df['name'] if x not in docs.df.author.values]))
	print('Modern Authors with documents not in philosopher df: ', [x for x in np.unique(docs.df['author']) if x not in phils.df.name.values])
	print('Modern Authors with more than one document: ', len([x for x in np.unique(docs.df['author']) if docs.df[docs.df.author == x].shape[0] > 1]))
	print('Documents with no year: ', docs.df[docs.df.year == 0].shape[0])
	print('Shape of Modern Philosopher dataframe: ', phils.df.shape)
	print('Shape of Modern Documents dataframe: ', docs.df.shape)
	print('Number of null nationalities: ', phils.df[phils.df.nationality.isnull()].shape[0])
	print('Number of null birthplaces: ', phils.df[phils.df.birthplace.isnull()].shape[0])
