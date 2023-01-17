
def within_regions(regions):
    """
    A predicate function that check whether the coordinate is in the regions.
    This function should be used as the value of `filter_cons` dictionary.
    and its key should be a coordinate property. The function will return true
    if the computed coordinate values of the property is in the regions.

    :param regions: one region or a list of regions, where region should be
            a list of coordinates and coordinates is a tuple of (x, y).
            The coordinates should be the exterior points of a Polygon.

    """
    if type(regions[0]) is tuple:
        regions = [regions]

    def point_within_regions(coordinate):
        from shapely.geometry import Point, Polygon
        point = Point(coordinate)
        for region in regions:
            poly = Polygon(region)
            if poly.area <= 0:
                raise ValueError(f"The area with in region {region} is less"
                                 f"than zero. Please check your region"
                                 f"coordinates.")
            if point.within(poly):
                return True
        return False
    return point_within_regions
