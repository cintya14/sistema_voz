# app/utils/pagination.py

from flask import request
from math import ceil


class Paginator:
    """Clase para manejar paginación de forma reutilizable"""

    def __init__(self, items, page=None, per_page=None, default_per_page=10):
        """
        Inicializa el paginador

        Args:
            items: Lista de items a paginar
            page: Número de página actual (si es None, se toma de request.args)
            per_page: Items por página (si es None, se toma de request.args)
            default_per_page: Valor por defecto de items por página
        """
        self.items = items
        self.total_items = len(items)

        # Obtener parámetros de paginación
        self.page = page if page is not None else request.args.get('page', 1, type=int)
        self.per_page = per_page if per_page is not None else request.args.get('per_page', default_per_page, type=int)

        # Calcular totales
        self.total_pages = ceil(self.total_items / self.per_page) if self.per_page > 0 else 1

        # Ajustar página si está fuera de rango
        if self.page < 1:
            self.page = 1
        if self.page > self.total_pages and self.total_pages > 0:
            self.page = self.total_pages

        # Calcular índices
        self.start_index = (self.page - 1) * self.per_page
        self.end_index = self.start_index + self.per_page

        # Obtener items de la página actual
        self.paginated_items = items[self.start_index:self.end_index]

        # Información de navegación
        self.has_prev = self.page > 1
        self.has_next = self.page < self.total_pages
        self.prev_num = self.page - 1 if self.has_prev else None
        self.next_num = self.page + 1 if self.has_next else None

    def get_items(self):
        """Retorna los items de la página actual"""
        return self.paginated_items

    def get_pagination_data(self):
        """Retorna un diccionario con toda la información de paginación"""
        return {
            'page': self.page,
            'per_page': self.per_page,
            'total_items': self.total_items,
            'total_pages': self.total_pages,
            'has_prev': self.has_prev,
            'has_next': self.has_next,
            'prev_num': self.prev_num,
            'next_num': self.next_num,
            'start_index': self.start_index + 1 if self.total_items > 0 else 0,
            'end_index': min(self.end_index, self.total_items),
            'pages': list(range(1, self.total_pages + 1))
        }

    def get_page_range(self, window=2):
        """
        Retorna un rango de páginas para mostrar en la navegación

        Args:
            window: Número de páginas a mostrar antes y después de la actual
        """
        start_page = max(1, self.page - window)
        end_page = min(self.total_pages, self.page + window)

        return {
            'start_page': start_page,
            'end_page': end_page,
            'show_first_ellipsis': start_page > 1,
            'show_last_ellipsis': end_page < self.total_pages,
            'pages': list(range(start_page, end_page + 1))
        }


def paginate(items, per_page=10):
    """
    Función helper para paginar rápidamente

    Args:
        items: Lista de items a paginar
        per_page: Items por página

    Returns:
        Tupla (items_paginados, datos_paginacion)
    """
    paginator = Paginator(items, per_page=per_page)
    return paginator.get_items(), paginator.get_pagination_data()


def apply_filters(items, filters):
    """
    Aplica filtros a una lista de items

    Args:
        items: Lista de items (diccionarios)
        filters: Diccionario con los filtros {campo: valor}

    Returns:
        Lista filtrada
    """
    filtered_items = items

    for field, value in filters.items():
        if value:  # Solo aplicar si el valor no está vacío
            filtered_items = [
                item for item in filtered_items
                if str(item.get(field, '')) == str(value)
            ]

    return filtered_items


def search_items(items, search_term, fields):
    """
    Busca un término en múltiples campos de los items

    Args:
        items: Lista de items (diccionarios)
        search_term: Término a buscar
        fields: Lista de campos donde buscar

    Returns:
        Lista filtrada con items que coinciden
    """
    if not search_term:
        return items

    search_term = search_term.lower()
    filtered_items = []

    for item in items:
        for field in fields:
            field_value = str(item.get(field, '')).lower()
            if search_term in field_value:
                filtered_items.append(item)
                break

    return filtered_items