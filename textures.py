TEXTURE_PATH = 'assets/textures/texture.png'

def tex_coord(x, y, n=4):
    """ Returns list represeinting the bounding
        vertices of the texture square.

    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side.

    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result


GRASS = tex_coords((1, 0), (0, 1), (0, 0))
DIRT = tex_coords((0, 1), (0, 1), (0, 1))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
STONE = tex_coords((2, 1), (2, 1), (2, 1))
CLOUD = tex_coords((3, 0), (3, 0), (3, 0))
WATER = tex_coords((0, 2), (0, 2), (0, 2))
BODY = tex_coords((1, 2), (1, 2), (1, 2))
HEAD = tex_coords((1, 2), (1, 2), (2, 2))
WOOD = tex_coords((1, 3), (1, 3), (0, 3))
LEAVES = tex_coords((2, 3), (2, 3), (2, 3))


FACES = [
    ( 0, 1, 0),
    ( 0,-1, 0),
    (-1, 0, 0),
    ( 1, 0, 0),
    ( 0, 0, 1),
    ( 0, 0,-1),
]