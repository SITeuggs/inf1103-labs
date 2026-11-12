# Lab 7 – UML Class Diagram (Inventory Management System)

```mermaid
classDiagram
    direction TB

    class Product {
        <<abstract>>
        -product_id : str
        -name : str
        -price : float
        -stock : int
        +__init__(product_id, name, price, stock)
        +get_product_id() str
        +get_name() str
        +get_price() float
        +get_stock() int
        +update_stock(quantity) bool
        +display_information() void
        +to_dict() dict
        +get_fulfilment_info()* str
    }

    class CanBeShipped {
        <<interface>>
        +calculate_shipping_cost()* float
    }

    class PhysicalProduct {
        +BASE_SHIPPING_FEE : float = 5.00$
        +COST_PER_KG : float = 2.00$
        -weight : float
        +__init__(product_id, name, price, stock, weight)
        +get_weight() float
        +calculate_shipping_cost() float
        +get_fulfilment_info() str
        +display_information() void
        +to_dict() dict
    }

    class DigitalProduct {
        -download_size : float
        +__init__(product_id, name, price, stock, download_size)
        +get_download_size() float
        +get_fulfilment_info() str
        +display_information() void
        +to_dict() dict
    }

    class Inventory {
        -products : list~Product~
        +__init__()
        +add_product(product) bool
        +search_product(product_id) Product
        +display_all() void
        +to_list() list
    }

    Product <|-- PhysicalProduct : inherits
    Product <|-- DigitalProduct : inherits
    CanBeShipped <|.. PhysicalProduct : implements
    Inventory o-- "0..*" Product : manages
```

## Notation key

| Notation | Meaning |
|----------|---------|
| `<<abstract>>` | Abstract class – cannot be instantiated (`Product` inherits `ABC`) |
| `<<interface>>` | Interface-style abstract base class (`CanBeShipped`) |
| Method ending in `*` (shown in *italics*) | Abstract method (`@abstractmethod`, no implementation) |
| Solid line, hollow triangle → parent | Inheritance / generalisation (`PhysicalProduct` and `DigitalProduct` **is-a** `Product`) |
| Dashed line, hollow triangle → interface | Interface realisation (`PhysicalProduct` **can-be-shipped**) |
| Hollow diamond on `Inventory` | `Inventory` holds 0..* `Product` objects |
| `-` / `+` | Private (`__attribute`) / public |
| Underlined attribute | Class (static) attribute |

## Notes
- `PhysicalProduct` and `DigitalProduct` **override** `display_information()` and `to_dict()`, calling the parent version with `super()` first, and **implement** the abstract `get_fulfilment_info()`.
- `DigitalProduct` does **not** realise `CanBeShipped`, so it has no `calculate_shipping_cost()`.
- `PhysicalProduct` has single class inheritance (`Product`) plus one interface (`CanBeShipped`).
- The module-level functions (`create_default_inventory`, `product_from_dict`, `load_inventory`, `save_inventory` and the menu functions) are not classes, so they are not shown.
