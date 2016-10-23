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

if __name__ == '__main__':
	mod_phils = ModernPhilosophers()
	mod_docs = ModernDocuments()
	print('Modern Authors with no documents: ', len([x for x in mod_phils.df['name'] if x not in mod_docs.df.author.values]))
	print('Modern Authors with documents not in philosopher df: ', [x for x in np.unique(mod_docs.df['author']) if x not in mod_phils.df.name.values])
	print('Modern Authors with more than one document: ', len([x for x in np.unique(mod_docs.df['author']) if mod_docs.df[mod_docs.df.author == x].shape[0] > 1]))
	print('Documents with no year: ', mod_docs.df[mod_docs.df.year == 0].shape[0])
	print('Shape of Modern Philosopher dataframe: ', mod_phils.df.shape)
	print('Shape of Modern Documents dataframe: ', mod_docs.df.shape)
	print('Number of null nationalities: ', mod_phils.df[mod_phils.df.nationality.isnull()].shape[0])
	print('Number of null birthplaces: ', mod_phils.df[mod_phils.df.birthplace.isnull()].shape[0])
