"""
Visual Metaphors Library

This module contains visual metaphor creation functions for different data structures
and algorithms used in 3Blue1Brown-style animations.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional
from ..core.data_structures import VisualElement

# 3D animation imports
try:
    from manimlib import ThreeDScene, ThreeDAxes, Sphere, Arrow3D, Text3D
    MANIM_3D_AVAILABLE = True
except ImportError:
    MANIM_3D_AVAILABLE = False


# ManimGL imports (3Blue1Brown's original version)
try:
    from manimlib import *
    MANIMGL_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("ManimGL available for visual metaphors")
except (ImportError, TypeError, AttributeError) as e:
    MANIMGL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"ManimGL not available for visual metaphors: {e}")

    # Try regular Manim as fallback
    try:
        from manim import *
        MANIM_AVAILABLE = True
        logger.info("Using Manim Community Edition as fallback")
    except (ImportError, TypeError, AttributeError) as e2:
        MANIM_AVAILABLE = False
        logger.warning(f"Manim Community Edition also not available: {e2}")

    # Create dummy classes for when Manim is not available
    class VGroup:
        def __init__(self, *args):
            self.elements = list(args)
        def move_to(self, pos):
            return self
        def scale(self, factor):
            return self
        def get_center(self):
            return [0, 0, 0]

    class Rectangle:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        def move_to(self, pos):
            return self
        def get_center(self):
            return [0, 0, 0]

    class Circle:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        def move_to(self, pos):
            return self
        def get_center(self):
            return [0, 0, 0]

    class Line:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class Text:
        def __init__(self, text, **kwargs):
            self.text = text
            self.kwargs = kwargs
        def move_to(self, pos):
            return self

    class Arrow:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    class Axes:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        def get_center(self):
            return [0, 0, 0]
        def c2p(self, x, y):
            return [x, y, 0]

    class ParametricFunction:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    # Color constants
    WHITE = "#ffffff"
    RED = "#ff0000"
    BLUE = "#0000ff"
    GREEN = "#00ff00"
    YELLOW = "#ffff00"
    PURPLE = "#800080"
    ORANGE = "#ffa500"
    GRAY = "#808080"
    PI = 3.14159265359
    UP = [0, 1, 0]
    DOWN = [0, -1, 0]
    LEFT = [-1, 0, 0]
    RIGHT = [1, 0, 0]

logger = logging.getLogger(__name__)

class VisualMetaphorLibrary:
    """Library of visual metaphors for different data structures and algorithms."""

    def __init__(self):
        """Initialize the visual metaphor library."""
        self.metaphors = {
            "rectangle_array": self.create_rectangle_array,
            "hierarchical_tree": self.create_hierarchical_tree,
            "network_graph": self.create_network_graph,
            "vertical_stack": self.create_vertical_stack,
            "horizontal_queue": self.create_horizontal_queue,
            "array_with_pivot": self.create_array_with_pivot,
            "array_with_pointer": self.create_array_with_pointer,
            "complexity_graph": self.create_complexity_graph,
            "summary_dashboard": self.create_summary_dashboard,
            "text": self.create_text_element
        }

        logger.info("VisualMetaphorLibrary initialized with metaphor functions")

    def create_visual_element(self, element: VisualElement) -> Any:
        """Create a visual element based on its type."""
        try:
            if not MANIMGL_AVAILABLE and not MANIM_AVAILABLE:
                logger.warning("Neither ManimGL nor Manim available, using fallback")
                return self.create_fallback_element(element)

            if element.type in self.metaphors:
                return self.metaphors[element.type](element)
            else:
                logger.warning(f"Unknown visual element type: {element.type}")
                return self.create_fallback_element(element)
        except Exception as e:
            logger.error(f"Error creating visual element {element.type}: {e}")
            return self.create_fallback_element(element)

    def create_rectangle_array(self, element: VisualElement) -> VGroup:
        """Create a rectangle array visualization."""
        try:
            values = element.properties.get("values", [1, 2, 3, 4, 5])
            size = element.properties.get("size", len(values))

            # Create rectangles for each value
            rectangles = []
            for i, value in enumerate(values):
                rect = Rectangle(
                    width=0.8,
                    height=0.8,
                    fill_opacity=0.7,
                    fill_color=element.color,
                    stroke_color=WHITE,
                    stroke_width=2
                )
                rect.move_to([i * 1.2 - (size-1) * 0.6, 0, 0])

                # Add value text
                value_text = Text(
                    str(value),
                    font_size=24,
                    color=WHITE
                ).move_to(rect.get_center())

                # Group rectangle and text
                group = VGroup(rect, value_text)
                rectangles.append(group)

            return VGroup(*rectangles)

        except Exception as e:
            logger.error(f"Error creating rectangle array: {e}")
            return VGroup()

    def create_hierarchical_tree(self, element: VisualElement) -> VGroup:
        """Create a hierarchical tree visualization."""
        try:
            values = element.properties.get("values", [1, 2, 3, 4, 5])

            # Create tree structure
            nodes = []
            edges = []

            # Root node
            root_circle = Circle(
                radius=0.3,
                fill_opacity=0.7,
                fill_color=element.color,
                stroke_color=WHITE,
                stroke_width=2
            ).move_to([0, 2, 0])

            root_text = Text(
                str(values[0]) if values else "R",
                font_size=20,
                color=WHITE
            ).move_to(root_circle.get_center())

            nodes.append(VGroup(root_circle, root_text))

            # Child nodes
            for i, value in enumerate(values[1:min(4, len(values))]):
                x_offset = (i - 1) * 1.5
                y_offset = 0

                child_circle = Circle(
                    radius=0.25,
                    fill_opacity=0.7,
                    fill_color=element.color,
                    stroke_color=WHITE,
                    stroke_width=2
                ).move_to([x_offset, y_offset, 0])

                child_text = Text(
                    str(value),
                    font_size=18,
                    color=WHITE
                ).move_to(child_circle.get_center())

                nodes.append(VGroup(child_circle, child_text))

                # Create edge
                edge = Line(
                    start=root_circle.get_center() + DOWN * 0.3,
                    end=child_circle.get_center() + UP * 0.25,
                    color=WHITE,
                    stroke_width=2
                )
                edges.append(edge)

            return VGroup(*nodes, *edges)

        except Exception as e:
            logger.error(f"Error creating hierarchical tree: {e}")
            return VGroup()

    def create_network_graph(self, element: VisualElement) -> VGroup:
        """Create a network graph visualization."""
        try:
            values = element.properties.get("values", [1, 2, 3, 4, 5])

            # Create nodes in a circular arrangement
            nodes = []
            edges = []
            radius = 2.0
            num_nodes = min(len(values), 6)

            for i in range(num_nodes):
                angle = i * 2 * PI / num_nodes
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)

                node_circle = Circle(
                    radius=0.3,
                    fill_opacity=0.7,
                    fill_color=element.color,
                    stroke_color=WHITE,
                    stroke_width=2
                ).move_to([x, y, 0])

                node_text = Text(
                    str(values[i]) if i < len(values) else str(i+1),
                    font_size=18,
                    color=WHITE
                ).move_to(node_circle.get_center())

                nodes.append(VGroup(node_circle, node_text))

                # Create edges to next node
                if i < num_nodes - 1:
                    edge = Line(
                        start=node_circle.get_center(),
                        end=nodes[(i + 1) % num_nodes][0].get_center(),
                        color=WHITE,
                        stroke_width=2
                    )
                    edges.append(edge)

            return VGroup(*nodes, *edges)

        except Exception as e:
            logger.error(f"Error creating network graph: {e}")
            return VGroup()

    def create_vertical_stack(self, element: VisualElement) -> VGroup:
        """Create a vertical stack visualization."""
        try:
            values = element.properties.get("values", [1, 2, 3, 4, 5])

            stack_elements = []
            for i, value in enumerate(values):
                rect = Rectangle(
                    width=1.0,
                    height=0.6,
                    fill_opacity=0.7,
                    fill_color=element.color,
                    stroke_color=WHITE,
                    stroke_width=2
                ).move_to([0, i * 0.8 - (len(values)-1) * 0.4, 0])

                text = Text(
                    str(value),
                    font_size=20,
                    color=WHITE
                ).move_to(rect.get_center())

                stack_elements.append(VGroup(rect, text))

            return VGroup(*stack_elements)

        except Exception as e:
            logger.error(f"Error creating vertical stack: {e}")
            return VGroup()

    def create_horizontal_queue(self, element: VisualElement) -> VGroup:
        """Create a horizontal queue visualization."""
        try:
            values = element.properties.get("values", [1, 2, 3, 4, 5])

            queue_elements = []
            for i, value in enumerate(values):
                rect = Rectangle(
                    width=0.8,
                    height=0.8,
                    fill_opacity=0.7,
                    fill_color=element.color,
                    stroke_color=WHITE,
                    stroke_width=2
                ).move_to([i * 1.2 - (len(values)-1) * 0.6, 0, 0])

                text = Text(
                    str(value),
                    font_size=20,
                    color=WHITE
                ).move_to(rect.get_center())

                queue_elements.append(VGroup(rect, text))

            return VGroup(*queue_elements)

        except Exception as e:
            logger.error(f"Error creating horizontal queue: {e}")
            return VGroup()

    def create_array_with_pivot(self, element: VisualElement) -> VGroup:
        """Create an array with pivot visualization for sorting."""
        try:
            values = element.properties.get("values", [3, 1, 4, 1, 5])

            array_elements = []
            pivot_index = len(values) // 2

            for i, value in enumerate(values):
                # Different color for pivot
                color = RED if i == pivot_index else element.color

                rect = Rectangle(
                    width=0.8,
                    height=0.8,
                    fill_opacity=0.7,
                    fill_color=color,
                    stroke_color=WHITE,
                    stroke_width=2
                ).move_to([i * 1.2 - (len(values)-1) * 0.6, 0, 0])

                text = Text(
                    str(value),
                    font_size=20,
                    color=WHITE
                ).move_to(rect.get_center())

                # Add pivot label
                if i == pivot_index:
                    pivot_label = Text(
                        "PIVOT",
                        font_size=12,
                        color=RED
                    ).move_to(rect.get_center() + DOWN * 0.8)
                    array_elements.append(VGroup(rect, text, pivot_label))
                else:
                    array_elements.append(VGroup(rect, text))

            return VGroup(*array_elements)

        except Exception as e:
            logger.error(f"Error creating array with pivot: {e}")
            return VGroup()

    def create_array_with_pointer(self, element: VisualElement) -> VGroup:
        """Create an array with pointer visualization for searching."""
        try:
            values = element.properties.get("values", [1, 3, 5, 7, 9])

            array_elements = []
            pointer_index = 0  # Start at beginning

            for i, value in enumerate(values):
                rect = Rectangle(
                    width=0.8,
                    height=0.8,
                    fill_opacity=0.7,
                    fill_color=element.color,
                    stroke_color=WHITE,
                    stroke_width=2
                ).move_to([i * 1.2 - (len(values)-1) * 0.6, 0, 0])

                text = Text(
                    str(value),
                    font_size=20,
                    color=WHITE
                ).move_to(rect.get_center())

                # Add pointer arrow
                if i == pointer_index:
                    pointer = Arrow(
                        start=rect.get_center() + UP * 0.8,
                        end=rect.get_center() + UP * 0.1,
                        color=YELLOW,
                        stroke_width=3
                    )
                    pointer_label = Text(
                        "P",
                        font_size=16,
                        color=YELLOW
                    ).move_to(pointer.get_start() + UP * 0.3)
                    array_elements.append(VGroup(rect, text, pointer, pointer_label))
                else:
                    array_elements.append(VGroup(rect, text))

            return VGroup(*array_elements)

        except Exception as e:
            logger.error(f"Error creating array with pointer: {e}")
            return VGroup()

    def create_complexity_graph(self, element: VisualElement) -> VGroup:
        """Create a complexity analysis graph."""
        try:
            time_complexity = element.properties.get("time_complexity", "O(n)")
            space_complexity = element.properties.get("space_complexity", "O(1)")

            # Create axes
            axes = Axes(
                x_range=[0, 10, 1],
                y_range=[0, 10, 1],
                x_length=6,
                y_length=4,
                axis_config={"color": WHITE}
            )

            # Create complexity curves
            x_vals = np.linspace(0, 10, 100)

            if "O(n)" in time_complexity:
                y_vals = x_vals
                curve_color = BLUE
            elif "O(n²)" in time_complexity:
                y_vals = x_vals ** 2
                curve_color = RED
            elif "O(log n)" in time_complexity:
                y_vals = np.log(x_vals + 1)
                curve_color = GREEN
            else:
                y_vals = np.ones_like(x_vals)
                curve_color = YELLOW

            # Scale to fit axes
            y_vals = y_vals * 8 / np.max(y_vals)

            curve = ParametricFunction(
                lambda t: axes.c2p(t, y_vals[int(t * 10)]),
                t_range=[0, 10],
                color=curve_color,
                stroke_width=3
            )

            # Labels
            time_label = Text(
                f"Time: {time_complexity}",
                font_size=20,
                color=curve_color
            ).move_to(axes.get_center() + UP * 3)

            space_label = Text(
                f"Space: {space_complexity}",
                font_size=20,
                color=WHITE
            ).move_to(axes.get_center() + DOWN * 3)

            return VGroup(axes, curve, time_label, space_label)

        except Exception as e:
            logger.error(f"Error creating complexity graph: {e}")
            return VGroup()

    def create_summary_dashboard(self, element: VisualElement) -> VGroup:
        """Create a summary dashboard visualization."""
        try:
            algorithms = element.properties.get("algorithms", [])
            data_structures = element.properties.get("data_structures", [])

            # Create dashboard background
            dashboard = Rectangle(
                width=8,
                height=6,
                fill_opacity=0.1,
                fill_color=element.color,
                stroke_color=WHITE,
                stroke_width=2
            )

            # Algorithm section
            algo_title = Text(
                "Algorithms",
                font_size=24,
                color=WHITE
            ).move_to(dashboard.get_center() + UP * 2 + LEFT * 3)

            algo_items = []
            for i, algo in enumerate(algorithms[:3]):  # Limit to 3 items
                item = Text(
                    f"• {algo}",
                    font_size=16,
                    color=WHITE
                ).move_to(algo_title.get_center() + DOWN * (i + 1) * 0.8)
                algo_items.append(item)

            # Data structure section
            ds_title = Text(
                "Data Structures",
                font_size=24,
                color=WHITE
            ).move_to(dashboard.get_center() + UP * 2 + RIGHT * 3)

            ds_items = []
            for i, ds in enumerate(data_structures[:3]):  # Limit to 3 items
                item = Text(
                    f"• {ds}",
                    font_size=16,
                    color=WHITE
                ).move_to(ds_title.get_center() + DOWN * (i + 1) * 0.8)
                ds_items.append(item)

            return VGroup(
                dashboard,
                algo_title,
                *algo_items,
                ds_title,
                *ds_items
            )

        except Exception as e:
            logger.error(f"Error creating summary dashboard: {e}")
            return VGroup()

    def create_text_element(self, element: VisualElement) -> Text:
        """Create a text element."""
        try:
            text_content = element.properties.get("text", "Text")
            font_size = element.properties.get("font_size", 24)

            return Text(
                text_content,
                font_size=font_size,
                color=element.color
            )

        except Exception as e:
            logger.error(f"Error creating text element: {e}")
            return Text("Error", color=RED)

    def create_fallback_element(self, element: VisualElement) -> VGroup:
        """Create a fallback visual element."""
        try:
            fallback = Rectangle(
                width=1,
                height=1,
                fill_opacity=0.5,
                fill_color=element.color,
                stroke_color=WHITE,
                stroke_width=2
            )

            label = Text(
                element.type,
                font_size=16,
                color=WHITE
            ).move_to(fallback.get_center())

            return VGroup(fallback, label)

        except Exception as e:
            logger.error(f"Error creating fallback element: {e}")
            return VGroup()
