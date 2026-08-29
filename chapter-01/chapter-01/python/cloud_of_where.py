import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial import Voronoi

def gaussian_1d(x, x0, sigma):
    """1D Gaussian wavefunction probability density."""
    return (1 / np.sqrt(2 * np.pi * sigma**2)) * np.exp(-(x - x0)**2 / (2 * sigma**2))

def probability_density_2d(x, y, x0, y0, sigma_x, sigma_y):
    """2D probability density as product of two 1D Gaussians."""
    return gaussian_1d(x, x0, sigma_x) * gaussian_1d(y, y0, sigma_y)

def create_cloud_of_where(resolution=1000, sigma_x=0.3, sigma_y=0.3,
                          x0=0, y0=0, voronoi=False, voronoi_points=50):
    """
    Generate the Cloud of Where visualization.

    Parameters:
    - resolution: grid resolution (pixels per side)
    - sigma_x, sigma_y: width of Gaussian in each dimension
    - x0, y0: center of the cloud
    - voronoi: whether to overlay Voronoi diagram
    - voronoi_points: number of random points for Voronoi diagram
    """

    # Create 2D grid
    x = np.linspace(-2, 2, resolution)
    y = np.linspace(-2, 2, resolution)
    X, Y = np.meshgrid(x, y)

    # Compute probability density
    P = probability_density_2d(X, Y, x0, y0, sigma_x, sigma_y)

    # Normalize for visualization
    P_normalized = P / P.max()

    # Create custom colormap: white/silver -> violet -> deep indigo
    colors = ['#0a001a', '#2d0d4d', '#5d2d8f', '#9d5dff', '#fffdff']
    n_bins = 256
    cmap = LinearSegmentedColormap.from_list('cloud_where', colors, N=n_bins)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 12), dpi=100)

    # Plot the cloud
    im = ax.imshow(P_normalized, extent=[-2, 2, -2, 2], origin='lower',
                    cmap=cmap, interpolation='bilinear', alpha=0.95)

    # Optional: overlay Voronoi diagram
    if voronoi:
        # Generate random points for Voronoi diagram
        np.random.seed(42)
        points = np.random.uniform(-2, 2, size=(voronoi_points, 2))

        # Create Voronoi diagram
        vor = Voronoi(points)

        # Plot Voronoi edges with low alpha
        for simplex in vor.ridge_vertices:
            simplex = np.asarray(simplex)
            if np.all(simplex >= 0):
                ax.plot(vor.vertices[simplex, 0], vor.vertices[simplex, 1],
                       'w-', alpha=0.15, linewidth=0.8)

    # Styling
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_xlabel('Position x', fontsize=12)
    ax.set_ylabel('Position y', fontsize=12)
    ax.set_title('The Cloud of Where: Gaussian Wavefunction Probability Density',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_aspect('equal')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, label='|ψ(x,y)|²')

    plt.tight_layout()
    return fig, ax

if __name__ == '__main__':
    # Generate and display the cloud
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend

    fig, ax = create_cloud_of_where(resolution=1200, sigma_x=0.35, sigma_y=0.35,
                                     voronoi=True, voronoi_points=60)

    output_path = '/Users/ivanroche/cloud_of_where.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f'Image saved to {output_path}')
