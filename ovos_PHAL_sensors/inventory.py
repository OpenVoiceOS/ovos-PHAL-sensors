from dataclasses import dataclass

from json_database import JsonStorageXDG

from ovos_PHAL_sensors.base import NumericSensor, _norm


@dataclass
class InventoryItem(NumericSensor):
    n_items: int = 0
    unit: str = "count"
    device_name: str = "inventory"
    _slow: bool = True

    @property
    def value(self):
        return self.n_items

    @property
    def attrs(cls):
        return {
            "friendly_name": f"{cls.unique_id.replace('_price', '').replace('_', ' ').title()} {cls.device_name} Item Number",
            "icon": "mdi:counter"
            }


@dataclass
class ItemPrice(NumericSensor):
    unit: str = "€"
    device_name: str = "price"
    price: float = 0.0
    _slow: bool = True

    @property
    def value(self):
        return self.price

    @property
    def attrs(cls):
        return {
            "friendly_name": f"{cls.unique_id.replace('_price', '').replace('_', ' ').title()} {cls.device_name} Price",
            "icon": "mdi:currency-eur",
            "unit_of_measurement": cls.unit
            }


@dataclass
class ItemCapacity(NumericSensor):
    device_name = "capacity"
    capacity: float = 0.0
    _slow: bool = True

    @property
    def value(self):
        return self.capacity

    @property
    def attrs(cls):
        icon = "mdi:numeric"
        if cls.unit.lower() in ["l", "ml", "cl"]:
            icon = "mdi:cup-water"
        if cls.unit.lower() in ["kg"]:
            icon = "mdi:weight-kilogram"
        if cls.unit.lower() in ["g"]:
            icon = "mdi:weight-gram"
        if cls.unit.lower() in ["mg"]:
            icon = "mdi:weight"
        if cls.unit.lower() in ["pound"]:
            icon = "mdi:weight-pound"
        return {"friendly_name": f"{cls.unique_id.replace('_price', '').replace('_', ' ').title()} {cls.device_name}",
                "icon": icon,
                "unit_of_measurement": cls.unit
                }


@dataclass
class ItemImage(NumericSensor):
    device_name = "image_url"
    url: str = ""
    _slow = True

    @property
    def value(self):
        return self.url

    @property
    def attrs(cls):
        return {
            "friendly_name": f"{cls.unique_id.replace('_price', '').replace('_', ' ').title()} {cls.device_name} Image",
            "icon": "mdi:image-album"
            }


@dataclass
class ItemShoppingLink(NumericSensor):
    device_name = "shopping_url"
    url: str = ""
    _slow = True

    @property
    def value(self):
        return self.url

    @property
    def attrs(cls):
        return {
            "friendly_name": f"Buy {cls.unique_id.replace('_price', '').replace('_', ' ').title()} {cls.device_name}",
            "icon": "mdi:cart-variant"
            }


# TODO - own package for inventory / prices
# allow sensors as plugins once we have CommonIOT
class Inventory:
    def __init__(self):
        self.db = JsonStorageXDG(name="inventory", subfolder="ovos_sensors")

    def add_item(self, name):
        name = _norm(name)
        if name not in self.db:
            self.db[name] = {"value": 0, "device_name": "inventory"}
            self.db.store()

    @property
    def sensors(self):
        return [
            InventoryItem(unique_id=name,
                          n_items=data["value"],
                          device_name=data["device_name"])
            for name, data in self.db.items()
        ]


if __name__ == "__main__":
    inv = Inventory()
    inv.add_item("beer")
    print(inv.sensors)

    from ovos_PHAL_sensors.prices import HipermercadosPortugal

    hiper = HipermercadosPortugal()

    # get results from the web
    # for res in hiper.scan():
    #    print(res)

    # get values from database
    for s in hiper.sensors():
        print(s)
