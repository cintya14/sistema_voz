// Funcionalidad de búsqueda en tiempo real para artículos
function inicializarBusquedaArticulos(searchInputId, selectId, callback = null) {
    const searchInput = document.getElementById(searchInputId);
    const selectArticulo = document.getElementById(selectId);

    if (!searchInput || !selectArticulo) return;

    // Mostrar todos los artículos inicialmente
    filtrarArticulos(selectArticulo, '');

    // Búsqueda en tiempo real
    searchInput.addEventListener('input', function() {
        filtrarArticulos(selectArticulo, this.value);
    });

    // Mostrar el select cuando se hace focus
    searchInput.addEventListener('focus', function() {
        selectArticulo.style.display = 'block';
        filtrarArticulos(selectArticulo, this.value);
    });

    // Cuando se selecciona un artículo
    selectArticulo.addEventListener('change', function() {
        if (this.value && callback) {
            callback(this);
        }
    });
}

function filtrarArticulos(selectElement, searchTerm) {
    const options = selectElement.getElementsByTagName('option');
    let hasVisibleOptions = false;

    for (let i = 0; i < options.length; i++) {
        if (options[i].value === '') continue;

        const text = options[i].textContent.toLowerCase();
        if (text.includes(searchTerm.toLowerCase())) {
            options[i].style.display = '';
            hasVisibleOptions = true;
        } else {
            options[i].style.display = 'none';
        }
    }

    if (!hasVisibleOptions && searchTerm) {
        selectElement.innerHTML = '<option value="">No se encontraron artículos</option>';
    }
}

function limpiarBusqueda(searchInputId, selectId) {
    const searchInput = document.getElementById(searchInputId);
    const selectArticulo = document.getElementById(selectId);

    searchInput.value = '';
    searchInput.focus();
    filtrarArticulos(selectArticulo, '');
}