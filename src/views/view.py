from views import view_types, ray_trace, standard


class Viewer:
    view_mode: view_types.Perspective = view_types.Perspective.ORTHOGONAL
    light_mode: view_types.Lighting = view_types.Lighting.STANDARD

    def render(
        self,
        display: view_types.common_types.Display,
        figures: list[view_types.common_types.Display],
    ) -> view_types.common_types.Raster:
        if self.light_mode == view_types.Lighting.STANDARD:
            return standard.render(display, figures)
        if self.light_mode == view_types.Lighting.RAY_TRACE:
            return ray_trace.render(display, figures)
