import math

def project_pixel_to_ground(
    pixel_coord,             # (x, y) in pixels
    image_width,             # e.g. 1920
    image_height,            # e.g. 1080
    sensor_lat,              # drone GPS latitude
    sensor_lon,              # drone GPS longitude
    sensor_relative_altitude,                # drone height above ground (in meters)
    takeoff_altitude,
    sensor_relative_elevation_angle,                   # camera pitch in degrees (negative = downward)
    heading,                 # camera heading in degrees (0 = North)
    fov_horizontal,          # in degrees
    fov_vertical             # in degrees
):
    # step 0: compute altitude
    altitude = sensor_relative_altitude - takeoff_altitude
    # Step 1: angular offsets from image center
    center_x = image_width / 2
    center_y = image_height / 2
    dx = pixel_coord[0] - center_x
    dy = pixel_coord[1] - center_y

    x_angle_per_pixel = fov_horizontal / image_width
    y_angle_per_pixel = fov_vertical / image_height

    horizontal_angle_offset = dx * x_angle_per_pixel
    vertical_angle_offset = -dy * y_angle_per_pixel  # invert y for image down direction

    # Step 2: adjust pitch and heading
    bbox_pitch = sensor_relative_elevation_angle + vertical_angle_offset
    bbox_heading = heading + horizontal_angle_offset

    # Step 3: compute distance from drone to projected ground point
    pitch_rad = math.radians(abs(bbox_pitch))
    ground_offset_m = altitude / math.tan(pitch_rad)

    # Step 4: project ground point using spherical trigonometry
    R = 6378137  # Earth radius in meters
    bearing = math.radians(bbox_heading)
    lat1 = math.radians(sensor_lat)
    lon1 = math.radians(sensor_lon)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(ground_offset_m / R) +
        math.cos(lat1) * math.sin(ground_offset_m / R) * math.cos(bearing)
    )

    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(ground_offset_m / R) * math.cos(lat1),
        math.cos(ground_offset_m / R) - math.sin(lat1) * math.sin(lat2)
    )

    dest_lat = math.degrees(lat2)
    dest_lon = math.degrees(lon2)

    return (dest_lon, dest_lat)

sensor_lat = 34.060275154
sensor_lon = -117.196949636
sensor_relative_altitude = 335.47              # drone height above ground (in meters)
takeoff_altitude = 319.77
sensor_relative_elevation_angle = -36.84
heading = 52
fov_horizontal = 66.69
fov_vertical = 40.62
image_width = 1920
image_height = 1080
