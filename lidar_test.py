import math
import numpy as np
import matplotlib.pyplot as plt
from rplidar import RPLidar


# ============================================================
# CONFIGURATION
# ============================================================

PORT = "COM3"              # Windows example
# PORT = "/dev/ttyUSB0"    # Linux example

MAP_SIZE = 200             # Map is MAP_SIZE x MAP_SIZE cells
CELL_SIZE = 0.05           # 5 cm per cell

MAX_DISTANCE = 18.0        # Maximum distance to map (meters)

# Robot position in the map
ROBOT_X = MAP_SIZE // 2
ROBOT_Y = MAP_SIZE // 2


# ============================================================
# MAP
# ============================================================

# -1 = unknown
#  0 = free
#  1 = occupied

occupancy_grid = np.full(
    (MAP_SIZE, MAP_SIZE),
    -1,
    dtype=np.int8
)


# ============================================================
# COORDINATE CONVERSION
# ============================================================

def world_to_grid(x, y):
    """
    Convert coordinates in meters relative to robot/map origin
    into grid indices.
    """

    gx = int(ROBOT_X + x / CELL_SIZE)
    gy = int(ROBOT_Y + y / CELL_SIZE)

    return gx, gy


# ============================================================
# RAY TRACING
# ============================================================

def update_ray(angle, distance):
    """
    Update the occupancy grid using one LiDAR measurement.

    angle:
        Angle in degrees.

    distance:
        Distance in meters.
    """

    # Ignore invalid measurements
    if distance <= 0:
        return

    if distance > MAX_DISTANCE:
        return

    # Convert degrees to radians
    theta = math.radians(angle)

    # RPLIDAR coordinate system:
    #
    # x = forward
    # y = left/right
    #
    # You may need to flip the sign of y depending on
    # your coordinate convention.

    end_x = distance * math.cos(theta)
    end_y = distance * math.sin(theta)

    # Convert endpoint to grid
    end_gx, end_gy = world_to_grid(end_x, end_y)

    # Robot position in grid
    start_gx = ROBOT_X
    start_gy = ROBOT_Y

    # Number of samples along ray
    steps = max(
        abs(end_gx - start_gx),
        abs(end_gy - start_gy)
    )

    if steps == 0:
        return

    # Mark cells along the ray as free
    for i in range(steps):

        t = i / steps

        gx = int(
            start_gx +
            t * (end_gx - start_gx)
        )

        gy = int(
            start_gy +
            t * (end_gy - start_gy)
        )

        if (
            0 <= gx < MAP_SIZE and
            0 <= gy < MAP_SIZE
        ):
            occupancy_grid[gy, gx] = 0

    # Mark final cell as occupied
    if (
        0 <= end_gx < MAP_SIZE and
        0 <= end_gy < MAP_SIZE
    ):
        occupancy_grid[end_gy, end_gx] = 1


# ============================================================
# DISPLAY
# ============================================================

plt.ion()

fig, ax = plt.subplots()

image = ax.imshow(
    occupancy_grid,
    cmap="gray",
    vmin=-1,
    vmax=1,
    origin="lower"
)

ax.set_title("RPLIDAR S2 Map")

# Robot marker
ax.plot(
    ROBOT_X,
    ROBOT_Y,
    "ro",
    markersize=5
)


# ============================================================
# LIDAR
# ============================================================

lidar = RPLidar(PORT,1000000)
scan_num = 0
SCAN_REQUIREMENT = 10
try:

    print("Starting LiDAR...")

    for scan in lidar.iter_scans():
        scan_num += 1
        if (scan_num < SCAN_REQUIREMENT):
            continue
        scan_num = 0

        # Each scan contains multiple measurements
        #
        # scan looks approximately like:
        #
        # [
        #     (quality, angle, distance_mm),
        #     (quality, angle, distance_mm),
        #     ...
        # ]

        for quality, angle, distance_mm in scan:

            # Convert mm → meters
            distance_m = distance_mm / 1000.0

            # Ignore low-quality points
            if quality < 5:
                continue

            update_ray(
                angle,
                distance_m
            )

        # Update display
        image.set_data(
            occupancy_grid
        )

        plt.pause(0.001)


except Exception as e:
    print("ERROR: ",e)

finally:

    lidar.stop()
    lidar.disconnect()

    plt.ioff()
    plt.show()