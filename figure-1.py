import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import cartopy.crs as ccrs

plt.rcParams['font.size'] = 12
plt.rcParams['font.family'] = 'Helvetica'
plt.rcParams['font.style'] = 'normal'

class BivariateFoodMap:
    def __init__(self):
        # Read data
        try:
            self.df = pd.read_excel('/Users/cmor7802/repos/bivariate-map/data/figure-data.xlsx', sheet_name='data')
            self.world = gpd.read_file('/Users/cmor7802/repos/wheatlosses10/bivariate_maps/data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')
        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise

        # Y-axis cutoffs - Wheat Import Dependence
        self.y_cutoffs = [0, 10, 40, 100]

    def blend_colors(self, color1, color2, ratio):
        """Blends two colors given a ratio."""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:], 16)
        r = round(r1 * (1 - ratio) + r2 * ratio)
        g = round(g1 * (1 - ratio) + g2 * ratio)
        b = round(b1 * (1 - ratio) + b2 * ratio)
        return f'#{r:02x}{g:02x}{b:02x}'

    def generate_bivariate_cmap(self, blending_ratio=0.5):
        """Generates a bivariate colormap with defined scales."""
        blue_scale = ['#e8e8e8', '#83c3da', '#0069A6']  # X-axis blues (Undernourishment)
        orange_scale = ['#f4e3da', '#f4a36a', '#E76800']  # Y-axis oranges (Wheat Import Dependence)

        color_scale = []
        for i in range(len(orange_scale)):         # y-axis iteration first
            for j in range(len(blue_scale)):   # x-axis iteration second
                blended_color = self.blend_colors(blue_scale[j], orange_scale[i], blending_ratio)
                color_scale.append(blended_color)
        return mcolors.ListedColormap(color_scale)

    def map_values_to_colors(self, y_histco2, food_insecurity, x_cutoffs, cmap):
        """Maps the data values to the appropriate colors."""
        # Note the swapped parameters in the function signature
        
        # Get the bin indices (subtract 1 to convert to 0-based index)
        x_bin_index = np.digitize(food_insecurity, x_cutoffs, right=True) - 1
        y_bin_index = np.digitize(y_histco2, self.y_cutoffs, right=True) - 1
        
        # Clip to valid range
        x_bin_index = np.clip(x_bin_index, 0, len(x_cutoffs) - 2)
        y_bin_index = np.clip(y_bin_index, 0, len(self.y_cutoffs) - 2)
        
        # Calculate the color index
        # Note: x_bin_index determines the position within each row (purple scale)
        #       y_bin_index determines which row (red scale)
        index = x_bin_index + y_bin_index * (len(x_cutoffs) - 1)
        return cmap(index / (9 - 1))  # Normalize to [0, 1]

    def create_map(self, x_column, x_no_column, x_cutoffs, output_path, x_label):
        """Creates and saves a bivariate map."""
        cmap = self.generate_bivariate_cmap()
        
        # Apply color mapping
        self.df['color'] = self.df.apply(
            lambda row: self.map_values_to_colors(
                row['y_IDR'], 
                row[x_column], 
                x_cutoffs, 
                cmap
            ), 
            axis=1
        )
        
        # Convert colors to hex
        self.df['color_hex'] = self.df['color'].apply(
            lambda c: '#%02x%02x%02x' % (
                int(c[0]*255), int(c[1]*255), int(c[2]*255)
            )
        )

        # Create figure
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # Merge data
        merged_world = self.world.merge(
            self.df[['Country', 'color_hex', 'y_IDR', 'no_IDR', x_column, x_no_column]], 
            left_on='NAME', 
            right_on='Country', 
            how='left'
        )

        # Add hatching patterns
        merged_world['hatch'] = merged_world['no_IDR'].apply(lambda a: '//////' if a == " " else '')
        merged_world['dots'] = merged_world[x_no_column].apply(lambda a: '....' if a == " " else '')

        # Plot countries and hatches
        for _, row in merged_world.iterrows():
            facecolor = row['color_hex'] if pd.notnull(row['color_hex']) else 'white'
            ax.add_geometries([row['geometry']], ccrs.PlateCarree(), facecolor=facecolor, edgecolor='black', linewidth=1)
            
            hatch = row['hatch'] + row['dots']
            if hatch:
                ax.add_geometries([row['geometry']], ccrs.PlateCarree(), facecolor='none', edgecolor='black', linewidth=1, hatch=hatch)

        # Add legend
        legend_ax = fig.add_axes([0.12, 0.32, 0.2, 0.2])
        cz = np.zeros((3, 3))
        for xi in range(3):
            for yi in range(3):
                cz[xi, yi] = xi * 3 + yi

        legend_ax.imshow(cz, cmap=cmap, interpolation='none', origin='lower', aspect='equal')
        legend_ax.set_xticks([-0.5, 0.5, 1.5, 2.5])
        legend_ax.set_yticks([-0.5, 0.5, 1.5, 2.5])
        legend_ax.set_xticklabels([x_cutoffs[0], x_cutoffs[1], x_cutoffs[2], x_cutoffs[3]])
        legend_ax.set_yticklabels([self.y_cutoffs[0], self.y_cutoffs[1], self.y_cutoffs[2], self.y_cutoffs[3]])
        legend_ax.set_ylabel("Wheat Import Dependence (%)")
        legend_ax.set_xlabel(x_label)
        legend_ax.set_zorder(3)
        ax.set_zorder(1)

        # Save and close
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

# Create maps
mapper = BivariateFoodMap()

# Map 1: Severe food insecurity
mapper.create_map(
    x_column='x_Undernourishment',
    x_no_column='no_Undernourishment',
    x_cutoffs=[0, 5, 20, 55],
    output_path='/Users/cmor7802/repos/bivariate-map/outputs/figure-1-undernourishment.jpeg',
    x_label='Prevelance of Undernourishment (%)'
)
plt.show()
