
# Project Title
Group 3 Magnificent Seven Stock Adviser

# Description
The goal of this application is to develop a ML adviser to Magnificent Seven Stock prices, noting whether the algorithm thinks the stock's price will rise or fall the following day, and suggesting to the client a relevant action - to sell if the price will fall, and to buy if the price will rise. 
Other features of the app include a home page which spells out the project to the client, as well as a number of tables and graphs for each individual stock, giving the client a chance to see the historical information the relative algorithm was built on. 

# Installation Instructions
The app is easy to set up. Please make your way to the public site "https://pygroupproject-ensx4wypmgy59rhnmzvdlr.streamlit.app/" where you will come in contact with the homepage. Please browse through the homepage to gather additional information on the companies we selected, as well as additional details regarding the structuring of our ML algorithm.
In your left menu, you'll see the option to "Choose a Stock." Navigate to this page, where you will be asked to enter your personal SimFin API key. This is to ensure API charges are sent exclusively to the client using the app. 

# Usage
This app can be used via the public link listed above, or, locally. If you'd like to guage the app locally, clone the respository, install the dependencies listed in the requirements text (pip install -r requirements.txt), and run the API. 

# Contact Information
You can reach the group via its conglomerate email address, mdb2024s1group3@gmail.com, or via the group members individual IE University email addresses. 

# Additional Information
There are many iterative versions of the application available in the GitHub repository, 'How_Does_Our_App_Works?.py' being the final python script. Please note that other files, stored in the test_code folder, are previous versions where you can see our applications development - however these files are unnecessary to launch the application in a successful manner. 
The pages folder is crucial for the app's "Choose a Stock" page. 
The 'simfin_api.py' script provides the API wrapper necessary for the various functions referenced in the API script. 
Finally the 'mag7_final_model.json' file holds the predictive ML algorithm. It is already trained and doesn't need further development/alteration. 
Lastly, the requirements.txt, README.md and .gitignore files work as assumed. 
