# Inventory and Billing System

Este repositorio contiene un programa sencillo para administrar el inventario de productos, registrar compras y ventas y almacenar rutas de imágenes asociadas a cada producto.

## Requisitos

- Python 3.x
- No se necesitan dependencias externas ya que todo utiliza la biblioteca estándar.

## Uso rápido

Inicialice la base de datos por primera vez:

```bash
python3 inventory.py init-db
```

Agregue un producto indicando código, nombre, descripción, precio y cantidad inicial:

```bash
python3 inventory.py add-product P001 "Arroz" "Arroz blanco" 1.50 100
```

Añada imágenes al producto proporcionando la ruta de los archivos:

```bash
python3 inventory.py add-image P001 /ruta/a/imagen.jpg
```

Registre una compra (aumenta inventario) o una venta (disminuye inventario):

```bash
python3 inventory.py buy P001 20
python3 inventory.py sell P001 5 1.60
```

Muestre la lista de productos o consulte un producto en particular:

```bash
python3 inventory.py list-products
python3 inventory.py show-product P001
```

Finalmente, vea las transacciones registradas:

```bash
python3 inventory.py list-transactions
```

## Archivos

- `inventory.py`: Implementación del programa y su interfaz de línea de comandos.
- `inventory.db`: Se crea automáticamente para almacenar los datos.

