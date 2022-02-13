## How to run?
The app is built around [`streamlit`](https://streamlit.io/). You can run it either locally (Python3.9 needed) or in docker.<br>
To run it locally, you can run the following commands from a fresh start:
```
make venv-create
make local-run
```
To run it in docker, you can run the following commands:
```
make docker-build
make docker-run
```
Then you need to copy the URL (e.g. http://10.160.129.162:8501) from the cli to your browser to open the app.

Enjoy! :blush:

## Visualization examples
Here are some example plots for all European countries
<img src="/plots/russian_interference_eu.png" width="800">
<img src="/plots/eu_position_eu.png" width="800">

Here are some example plots for all parties from Finland
<img src="/plots/eu_position_fin.png" width="800">
<img src="/plots/corrupt_salience_fin.png" width="800">

To summarize, the main difference between the plots is what the data points on each plot stand for. For the first-type plot, one point stands for a party, and the value is the average value of all the scores the party gets for that question. For the second-type plot, one point stands for one score the party gets for that question from an expert. You can think this way - all the same-color points from a second-type plot are averaged into one single point in a first-type plot.

For example, we can see that the points in `russian_interference` (plot 1) are quite clustered. It means Russian-related issues are country-specific rather than party-specific. As shown in the plots, most parties in eastern European countries think of russian-influence as a quite important issue. On the other hand, the points in `eu_position` for all European countries (plot 2) are quite scattered. This is because, in each country, there is great variance among the parties' opinions towards the EU, just as shown in the `eu_position` for all Finnish parties (plot 3). In plot 3, the points for each party are quite clustered and the medium value varies a lot. It means experts think the stance toward the EU for the shown Finnish parties are quite different. Additionally, if the points are scattered in the second-type plot, as shown in `corrupt_salience` (plot 4), it could mean that the question is ambiguous and experts don't have a unified view towards the question. Surely, no party will openly support corruption, so the scores might be more based on personal insights from each expert.
