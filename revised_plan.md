### Analysis of Modern Era Philosophy
###### ***Revised Plan***

#### Story
* Focus only on Modern Era Philosophers
* 17th - Early 20th centuries
* Beginning with Rene Descartes, Ending with Ludwig Wiggenstein

#### Motivations / Hypotheses
* Did philosophical thought differ between countries?
	* Are there any patterns between philosophers in the same countries?
* What works appeared to be influencing society the most?
	* E.g. John Locke and Thomas Hobbes (American Revolution)
* Are certain schools of thought more prominent?
	* Use counts of documents
	* Only interested if there's a significant deviation from the mean
* Are there any significant shifts in thinking throughout the era?

#### Algorithm Stuff
* Is there any way to determine if particular works led to big shifts in thinking?
	* If so, are these predictions consistent with what others who study philosophy claim?
* How significant was each author weighted by the volume of work produced?
	* Any way to determine how impactful a work was?
	* If they wrote a lot but aren't considered impactful, not significant.
	* However, if they wrote a little but those works had impact, then significant.
* Are the changes in philosophical thought reflected in societal/economical change as well?
	* How do these two things change together?
* Group philosophers by Nationality
	* See if there's differences between philosophers in different countries
* Cluster philosophers based on similar word frequencies
	* Use for summary page
* If there's a way to obtain information for each document and which school of thought
it falls in, use the information to analyze the changes in that school's topics

#### Web App Stuff
* Still a story setting - Take the listeners through the time period
	* A map that zooms in based on location - location markers for each philosopher
	* Hovering over brings up more information about the philosopher
		* Clicking brings to summary page
	* Have a separate panel for other visualizations
		* Text importances, word clouds, graphs
		* Also other important things to take away from that time
		* Can type in year to go to specific year of the era
* Functionality to look up an author and see their relevant information
	* Suggestions pop up as typing
	* Author summaries have similar authors listed
* Have information on main page giving technical information about project
	* Libraries/technologies used
	* Email, phone, linkedin, github, etc...

#### Dirty work
* Try lots of different analysis tactics
	* Simply looking for interesting findings based on initial questions
* Focus on getting more document data
	* Drop any philosophers with only one document
* Find the nationality of each philosopher
* Have birthplace for each philosopher
* Possibly find some data that can be used to determine impact of a work
	* If time allows, use this information to train a supervised learning
	classifier
		* Based on text data, determine if a document will have high impact
* Try to find the school of thought each document falls into
* Try to discover a way to determine a document's influence on the outside
world
