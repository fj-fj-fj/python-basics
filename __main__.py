#!/usr/bin/env python
"""This module includes finding the shortest path.

Check:
`curl -fsSL https://raw.githubusercontent.com/fj-fj-fj/python-basics/main/__main__.py | python3 -`

"""
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, TypeVar, Tuple, Union


_TInputValidator = TypeVar("_TInputValidator", bound="InputValidator")
_TRoute = TypeVar("_TRoute", bound="Route")

@dataclass(frozen=True)
class InputValidator:

    """Class for representing validated data."""

    data: List[Tuple[int, int, str]]

    def __post_init__(self: _TInputValidator):
        """Check typing."""
        try:
            data = self.__dict__["data"]
            assert isinstance(data, list), "self.data is not list"
            assert isinstance(data[0], tuple), "self.data[0] is not tuple"
            assert len(data[0]) == 3, "len(self.data[0]) != 3 items"
            assert isinstance(data[0][0], int), "self.data[0][0] is not int"
            assert isinstance(data[0][1], int), "self.data[0][1] is not int"
            assert isinstance(data[0][2], str), "self.data[0][2] is not str"
        except AssertionError:
            raise TypeError(f"The field 'data' must be "
                f"`{self.__annotations__['data']}`")


@dataclass(frozen=True)
class Point:

    """Class for representing a point on a coordinate plane."""

    x: int
    y: int
    address: str


class Route:

    """Class for representing a shortest distance."""

    def __init__(self: _TRoute, start: str = "почтовое отделение"):
        """Initialize Route."""
        self.validated: Optional[InputValidator] = None
        self._start_address = start
        self._start_point: Optional[Point] = None
        self._finish_point: Optional[Point] = None
        self._row_route: List[Optional[Point]] = []
        self._all_distances: Optional[Dict[str, Dict[str, float]]] = []
        self._paths: List[Optional[str]] = []
        self._display: Optional[str] = None

    def shortify(self: _TRoute) -> _TRoute:
        """Find the shortest way and return self."""
        self._set_preroute()
        self._calculate_minimal_route()
        return self

    @property
    def display(self: _TRoute) -> str:
        """Return the path with the shortest route length."""
        start_point: Point = self._start_point
        previous: Point = start_point
        distance: float = .0
        route = f"({previous.x}, {previous.y}) -> "
        for point in self._display["points"]:
            point: Optional[Point]
            if point:
                distance += Route._calc_distance_between_points(previous, point)
                route += f"({point.x}, {point.y})[{distance}] -> "
                previous = point
        min_distance: float = self._display["minimal_distance"]
        min_path = f"{route}({start_point.x}, {start_point.y})[{min_distance}]"
        result = f"{min_path} = {min_distance}"
        return result

    def _set_preroute(self: _TRoute):
        """Set a list of waypoints."""
        for point in self.validated.data:
            if point[-1].lower() == self._start_address:
                self._start_point = Point(*point)
            else:
                self._row_route.append(Point(*point))
        self._finish_point = self._start_point

    def _calculate_minimal_route(self: _TRoute):
        """Calculate a valid possible route."""
        def _get_point_by_address(address: str) -> Optional[Point]:
            """Return `Point` by `Point.address`."""
            for point in self._row_route:
                if point.address == address:
                    return point
        points = [self._start_point, *self._row_route, self._finish_point]
        self._generate_matrix(points, points)
        self._create_all_combinations()
        mininal_distance: float = math.inf
        minimal_path: List[str] = []
        start_point: str = self._start_point.address
        for path in self._paths:
            path: List[str]
            route_dist = .0
            for point_address in path:
                route_dist += self._all_distances[start_point][point_address]
                start_point = point_address
            if mininal_distance > route_dist:
                mininal_distance = route_dist
                minimal_path = path

        mininal_route: List[Optional[Point]] = []
        for point_address in minimal_path:
            mininal_route.append(_get_point_by_address(point_address))

        self._display: Dict[str, Union[List[Point], float]] = {
            "points": mininal_route,
            "minimal_distance": mininal_distance
        }

    def _generate_matrix(self: _TRoute, start_arr: list, finish_arr: list):
        """Construct the table of distances between points."""
        def _generate_row(start: Point, finish_arr: list) -> dict:
            """Return a table row (list of the distances)."""
            row: Dict[str, float] = {}
            for finish in finish_arr:
                row[finish.address] = self._calc_distance_between_points(
                    start, finish)
            return row

        start_arr: List[Point]
        finish_arr: List[Point]

        matrix: Dict[str, Dict[str, float]] = {}
        for start in start_arr:
            matrix[start.address] = _generate_row(start, finish_arr)
        self._all_distances = matrix


    @staticmethod
    def _calc_distance_between_points(start: Point, finish: Point) -> float:
        """Return the calculated distance between two points.

        The distance is calculated by `√(x₂ - x₁)²(y₂ - y₁)²`
        where `x₁` and `y₁` are the coordinates of the first
        point(`start`), `x₂` and `y₂` are the coordinates
        of the second point(`finish`).

        """
        diff_x = finish.x - start.x
        diff_y = finish.y - start.y
        return (diff_x ** 2 + diff_y ** 2) ** .5

    def _create_all_combinations(self: _TRoute):
        """Create all possible routes."""
        def _permute(arr: list, len_arr: int):
            """Use the permutation heap method to create all
            possible combinations of elements.

            """
            if len_arr == 1:
                self._paths.append([
                    self._start_point.address,
                    *arr,
                    self._finish_point.address
                ])
            else:
                for i in range(len_arr):
                    _permute(arr, len_arr - 1)
                    if len_arr % 2 == 0:
                        arr[i], arr[len_arr - 1] = arr[len_arr - 1], arr[i]
                    else:
                        arr[0], arr[len_arr - 1] = arr[len_arr - 1], arr[0]

        points_address: List[Optional[str]] = []
        for point in self._row_route:
            points_address.append(point.address)
        _permute(points_address, len(points_address))


def main(data: Any) -> str:
    """Validate data an return the shortest route or raise Error."""
    validated: InputValidator = InputValidator(data) # or raise Error !
    route: Route = Route()
    route.validated = validated
    result: str = route.shortify().display
    return result


if __name__ == "__main__":
    data: List[List[Tuple[int, int, str]]]
    data_set = [
        [
            (0, 2, "Почтовое отделение"),
            (8, 3, "Вечнозелёная Аллея, 742"),
            (6, 6, "Ул. Большая Садовая, 302-бис"),
            (5, 2, "Ул. Бейкер стрит, 221б"),
            (2, 5, "Ул. Грибоедова, 104/25"),
        ],
        [
            (2, 5, "Ул. Грибоедова, 104/25"),
            (5, 2, "Ул. Бейкер стрит, 221б"),
            (6, 6, "Ул. Большая Садовая, 302-бис"),
            (8, 3, "Вечнозелёная Аллея, 742"),
            (0, 2, "Почтовое отделение"),
        ],
        [
            (8, 3, "Вечнозелёная Аллея, 742"),
            (6, 6, "Ул. Большая Садовая, 302-бис"),
            (0, 2, "Почтовое отделение"),
            (5, 2, "Ул. Бейкер стрит, 221б"),
            (2, 5, "Ул. Грибоедова, 104/25"),
        ]
    ]

    expected = (
        "(0, 2) -> (5, 2)[5.0] -> "
        "(8, 3)[8.16227766016838] -> "
        "(6, 6)[11.76782893563237] -> "
        "(2, 5)[15.890934561250031] -> "
        "(0, 2)[19.49648583671402] = 19.49648583671402"
    )

    for data in data_set:
        result: str = main(data)
        assert result == expected
