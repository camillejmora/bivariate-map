# bivariate-map
Code to plot bivariate map.

This repository has two folders:
- data: contains processed data in excel format to produce the figure and shapefile used for the map. 
- outputs: where the figure is saved.

The data for undernourishment and wheat imports/exports per country in 2010 is available from FAOSTAT (1). The method used to calculate the wheat import dependence follows the approach in (2). The shapefile is publicly available from: https://www.naturalearthdata.com/. 

The notebook uses Python 3.11.8. The packages required for this code are: 
- geopandas
- pandas
- matplotlib.pyplot
- numpy
- matplotlib.colors
- cartopy.crs
- cartopy.feature
- matplotlib.patches

Please cite this work as: ... 

References: 

(1) FAOSTAT. (2024), Retrieved on 18 October from https://www.fao.org/faostat/en/#data/QCL.

(2) S. Vishwakarma, X. Zhang, V. Lyubchich. (2024), Wheat trade tends to happen between countries with contrasting extreme weather stress and synchronous yield variation. Communications Earth & Environment 3.
