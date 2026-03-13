def show_full(page, file: dict, refresh_function=None):
    """Show the gallery in a full-page view."""
    from views.sections.full_view import FullViewPage

    full_view_page = FullViewPage(page, file, on_close=refresh_function)
    page.views.append(full_view_page.build())
