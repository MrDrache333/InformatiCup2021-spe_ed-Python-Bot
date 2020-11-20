import copy
import heapq


class Cell(object):
    def __init__(self, x, y, reachable):
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f


class AStar(object):
    def __init__(self, coordinateSystem, x, y):
        """
        :param coordinateSystem: CoordinateSystem
        :param x: Start X
        :param y: Start Y
        """
        self.opened = []
        heapq.heapify(self.opened)
        self.closed = set()
        self.coordinateSystem = copy.deepcopy(coordinateSystem)
        self.cells = []
        self.grid_height = len(coordinateSystem)
        self.grid_width = len(coordinateSystem[0])
        for y_ in range(self.grid_height):
            for x_ in range(self.grid_width):
                self.cells.append(Cell(x_, y_, self.coordinateSystem[y_][x_] == 0 if x != x_ and y != y_ else True))
                self.coordinateSystem[y_][x_] = 1 if self.coordinateSystem[y_][x_] != 0 else 0
        self.start = self.getCell(x, y)

    def getCell(self, x, y):
        return self.cells[y * self.grid_width + x]

    def get_heuristic(self, cell):
        """Compute the heuristic value H for a cell.
        Distance between this cell and the ending cell multiply by 10.
        @returns heuristic value H
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def get_adjacent_cells(self, cell):
        """Returns adjacent cells to a cell.
        Clockwise starting from the one on the right.
        @param cell get adjacent cells for this cell
        @returns adjacent cells list.
        """
        cells = []
        if cell.x < self.grid_width - 1:
            cells.append(self.getCell(cell.x + 1, cell.y))
        if cell.y > 0:
            cells.append(self.getCell(cell.x, cell.y - 1))
        if cell.x > 0:
            cells.append(self.getCell(cell.x - 1, cell.y))
        if cell.y < self.grid_height - 1:
            cells.append(self.getCell(cell.x, cell.y + 1))
        return cells

    def get_path(self):
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start and cell.parent is not None:
            cell = cell.parent
            path.append((cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    def update_cell(self, adj, cell):
        """Update adjacent cell.
        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def solve(self, end):
        if end == self.start:
            return []
        self.end = self.getCell(*end)
        """Solve maze, find path to ending cell.
        @returns path or None if not found.
        """
        # add starting cell to open heap queue
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.opened)
            # add cell to closed list so we don't process it twice
            self.closed.add(cell)
            # if ending cell, return found path
            if cell is self.end:
                return self.get_path()
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closed:
                    if (adj_cell.f, adj_cell) in self.opened:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found
                        # for this adj cell.
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        heapq.heappush(self.opened, (adj_cell.f, adj_cell))
