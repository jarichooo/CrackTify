def show_full(page, file: dict):
    """Show the gallery in a full-page view."""
    from views.sections.full_view import FullViewPage

    full_view_page = FullViewPage(page, file)
    page.views.append(full_view_page.build())