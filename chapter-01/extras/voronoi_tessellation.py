import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, geometric_slerp
from scipy.spatial._plotutils import _adjust_bounds
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.colors as mcolors

def generate_voronoi_tessellation(n_points=15, seed=42):
    """Generate a 3D Voronoi tessellation with random seed points."""
    np.random.seed(seed)

    # Generate random seed points in 3D space
    points = np.random.rand(n_points, 3) * 10

    # Compute Voronoi tessellation
    vor = Voronoi(points)

    return vor, points

def plot_voronoi_3d(vor, points, figsize=(12, 10)):
    """Plot the Voronoi tessellation in 3D with translucent cells and glowing edges."""
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')

    # Extract vertices
    vertices = vor.vertices

    # Color palette for cells
    colors = plt.cm.hsv(np.linspace(0, 1, len(vor.point_region)))

    # Plot each Voronoi region
    plotted_regions = set()

    for point_idx, region_idx in enumerate(vor.point_region):
        region = vor.regions[region_idx]

        # Skip regions with point at infinity or invalid regions
        if -1 in region or len(region) < 3:
            continue

        if region_idx in plotted_regions:
            continue
        plotted_regions.add(region_idx)

        # Get vertices for this region
        region_vertices = vertices[region]

        try:
            # Create faces (simplices/triangles) from convex hull approximation
            from scipy.spatial import ConvexHull

            if len(region_vertices) > 3:
                hull = ConvexHull(region_vertices)
                faces = hull.simplices
            else:
                continue

            # Create polygon collection
            poly_verts = [region_vertices[face] for face in faces]

            # Create face colors with transparency
            face_color = list(colors[point_idx])
            face_color[3] = 0.3  # Set alpha to 0.3 for translucency

            # Add the polyhedral cells
            poly = Poly3DCollection(
                poly_verts,
                alpha=0.3,
                edgecolor='cyan',
                facecolor=colors[point_idx],
                linewidth=1.5
            )

            ax.add_collection3d(poly)

        except Exception:
            # Skip problematic regions
            continue

    # Plot seed points
    ax.scatter(points[:, 0], points[:, 1], points[:, 2],
               c='red', s=50, marker='o', edgecolors='darkred', linewidth=2,
               label='Seed points', zorder=10)

    # Set labels and title
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Voronoi Tessellation in 3D\nSpace-Filling Foam Structure', fontsize=14, fontweight='bold')

    # Set viewing angle
    ax.view_init(elev=20, azim=45)

    # Set axis limits
    ax.set_xlim([0, 10])
    ax.set_ylim([0, 10])
    ax.set_zlim([0, 10])

    ax.legend()

    return fig, ax

def create_inset_pebbles_diagram(fig, ax):
    """Add an inset diagram showing the crossed-out pebbles concept."""
    from matplotlib.patches import Rectangle, Circle
    import matplotlib.patches as mpatches

    # Create inset axis
    inset_ax = ax.inset_axes([0.65, 0.6, 0.3, 0.3])

    # Draw pebbles (circles)
    pebble_positions = [(0.2, 0.5), (0.5, 0.3), (0.8, 0.6), (0.35, 0.8)]

    for i, (x, y) in enumerate(pebble_positions):
        circle = Circle((x, y), 0.12, color=plt.cm.Set3(i), alpha=0.7, ec='black', linewidth=2)
        inset_ax.add_patch(circle)

        # Add X through half the pebbles
        if i < 2:
            inset_ax.plot([x - 0.08, x + 0.08], [y - 0.08, y + 0.08], 'k-', linewidth=2)
            inset_ax.plot([x - 0.08, x + 0.08], [y + 0.08, y - 0.08], 'k-', linewidth=2)

    inset_ax.set_xlim(0, 1)
    inset_ax.set_ylim(0, 1)
    inset_ax.set_aspect('equal')
    inset_ax.axis('off')
    inset_ax.set_title('Seed Points Concept', fontsize=10, fontweight='bold')

    return inset_ax

def main():
    """Generate and display the Voronoi tessellation."""
    print("Generating Voronoi tessellation...")
    vor, points = generate_voronoi_tessellation(n_points=12, seed=42)

    print("Plotting 3D visualization...")
    fig, ax = plot_voronoi_3d(vor, points)

    print("Adding inset diagram...")
    inset_ax = create_inset_pebbles_diagram(fig, ax)

    # Add mathematical description as text
    description = (
        "Voronoi Tessellation: A space-filling foam where each cell is\n"
        "defined by points closer to one seed than any other seed.\n"
        "By construction: No gaps, complete space coverage."
    )
    fig.text(0.5, 0.02, description, ha='center', fontsize=9,
             style='italic', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.savefig('/Users/ivanroche/voronoi_tessellation.png', dpi=300, bbox_inches='tight')
    print("Image saved to: /Users/ivanroche/voronoi_tessellation.png")

    plt.show()

if __name__ == "__main__":
    main()
