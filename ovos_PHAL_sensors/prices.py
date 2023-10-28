from dataclasses import dataclass
from typing import Tuple, List, Optional

import requests
from json_database import JsonStorageXDG
from ovos_utils import timed_lru_cache
from unidecode import unidecode

from ovos_PHAL_sensors.inventory import InventoryItem, ItemPrice, \
    ItemCapacity, ItemImage, ItemShoppingLink
from ovos_PHAL_sensors.base import _norm


@dataclass
class Result:
    hiper: str = ""
    name: str = ""
    price: float = 0.0  # eur
    price_per_unit: float = 0.0  # eur / unit
    unit: str = ""
    capacity: float = 0.0
    item_capacity: float = 0.0
    image_url: str = ""
    date: str = ""
    url: str = ""
    currency: str = "€"
    n_items: int = 1

    @property
    def unique_id(self):
        return f"{_norm(self.hiper)}_{_norm(self.name)}"


# TODO - own package for inventory / prices
# allow sensors as plugins once we have CommonIOT
class HipermercadosPortugal:
    base_url = "https://app.supersave.pt/crawler/product.php"
    hipers = ['Auchan', 'Continente', 'Minipreço', 'PingoDoce']

    def __init__(self, queries: list = None, debug=False):
        # TODO - from config
        default_queries = [
            Query("cerveja", required=["super bock"], blacklist=["sagres", "sem alcool"]),
            Query("café", required=["cápsulas"], blacklist=["máquina"]),
            Query("bife de peru", required=["bife"]),
            Query("bife de frango", required=["bife"]),
            Query("frango inteiro", blacklist=["bife"]),
            Query("douradinhos"),
            Query("leite"),
            Query("arroz"),
            Query("salsichas"),
            Query("bife de vaca", required=["bife"]),
            Query("bife de boi", required=["bife"]),
            Query("manteiga"),
            Query("cereais de chocolate", blacklist=["tablete", "barra"]),
            Query("almondegas"),
            Query("hamburger"),
            Query("pizza"),
            Query("papel higienico"),
            Query("pasta dos dentes"),
            Query("sabão")
        ]
        self.queries = queries or default_queries
        self.databases = {}
        self.debug = debug
        for hiper in self.hipers:
            if hiper not in self.databases:
                self.databases[hiper] = JsonStorageXDG(name=f"{hiper}_prices", subfolder="ovos_sensors")

    @property
    def sensors(self):
        sensors = []
        for hiper, db in self.databases.items():
            for sensor_name, data in db.items():
                sensor_name = _norm(sensor_name)
                sensors += [
                    InventoryItem(sensor_name, n_items=data["n_items"], device_name=hiper),
                    ItemPrice(sensor_name + "_price", price=data["price_per_unit"], device_name=hiper),
                    ItemShoppingLink(sensor_name + "_buy", url=data["url"], device_name=hiper),
                    ItemImage(sensor_name + "_image", url=data["image_url"], device_name=hiper),
                    ItemCapacity(sensor_name + "_capacity", capacity=data["item_capacity"],
                                 device_name=hiper, unit=data["unit"])
                ]
        return sensors

    def scan(self, hipers=None):
        hipers = hipers or self.hipers
        for hiper in hipers:
            if hiper not in self.databases:
                self.databases[hiper] = JsonStorageXDG(name=f"{hiper}_prices", subfolder="hipermercadosPT")
        for q in self.queries:
            try:
                if isinstance(q, Query):
                    res = q.search(self)
                else:
                    res = self.update(q)
            except:
                print("rate limited, try again in a few hours")
                break

            for item in res:
                if item.hiper not in hipers:
                    continue
                self.databases[item.hiper][item.name] = item.__dict__
                yield item

        for db in self.databases.values():
            db.store()

    @staticmethod
    def _parse_price(data) -> float:
        price = data["normalPrice"].replace(",", ".").split("/")[0]
        price = "".join([c for c in price if c.isdigit() or c == "."])
        return float(price)

    def _parse_capacity(self, data, price) -> Tuple[int, float, float, str]:

        capacity = data["capacity"].lower()
        if capacity.startswith("x"):
            capacity = f"1{capacity}"
        for r in ["emb.", "garrafa", " ",
                  "aprox", "peso escorrido"]:
            capacity = capacity.replace(r, "")

        if capacity == "0":
            # try to get from name, usually means a bad parse upstream
            name = data["name"]
            if "kg" in name.lower().split():
                capacity = "".join([c for c in data["name"] if c.isdigit() or c in ["."]]) + "kg"
            else:
                raise RuntimeError("malformed result")

        # number X number unit
        if "x" in capacity:
            n, icapacity = capacity.split("x")
            n = int("".join([c for c in n if c.isdigit()]))

            unit = "".join([c for c in icapacity if not c.isdigit() and c not in ["."]])
            icapacity = float("".join([c for c in icapacity if c.isdigit() or c in ["."]]))
            capacity = round(n * icapacity, 5)
        # unit | number unit | empty
        else:
            n = 1
            unit = "".join([c for c in capacity if not c.isdigit() and c not in ["."]])
            capacity = "".join([c for c in capacity if c.isdigit() or c in ["."]])
            if not capacity and unit:
                capacity = 1
            else:
                capacity = float(capacity)
            icapacity = capacity

        if self.debug:
            print(data["name"], "###", data["capacity"])
            print("n items:", n)
            print("total price:", price, "€")
        return n, icapacity, capacity, unit

    def _standardize_units(self, icapacity, capacity, unit, price) -> Tuple[float, float, str, float]:
        target = unit
        if unit.lower() in ["cl", "ml"]:
            target = "l"
        elif unit.lower() in ["g"]:
            target = "kg"
        if target != unit:
            if target == f"k{unit}":  # g -> kg
                icapacity = icapacity / 1000
                capacity = capacity / 1000
                unit = target

            elif unit == f"m{target}":  # ml -> L
                icapacity = icapacity / 1000
                capacity = capacity / 1000
                unit = target
            elif unit == f"c{target}":  # cl -> L
                icapacity = icapacity / 100
                capacity = capacity / 100
                unit = target

        ppunit = round(price / capacity, 5)  # eg, price per liter
        if self.debug:
            print(f"total {unit}:", capacity)
            print(f"{unit} per item:", icapacity)
            print(f"price per {unit}:", ppunit, "€")
        return icapacity, capacity, unit, ppunit

    @classmethod
    @timed_lru_cache()
    def _do_request(cls, query):
        return requests.get(cls.base_url, params={"search": query}).json()

    def update(self, query, required=None, blacklist=None):
        data = self._do_request(query)
        required = required or []
        blacklist = blacklist or []
        for hiper, prices in data.items():

            def _norm(s):
                return unidecode(s.lower().replace(",", "."))

            if blacklist:
                prices = [v for v in prices
                          if not any(_norm(b) in _norm(v["name"]) for b in blacklist)]
            if required:
                prices = [v for v in prices
                          if all(_norm(r) in _norm(v["name"]) for r in required)]
            for p in prices:
                if not p["capacity"]:  # usually means malformed results
                    continue
                p["name"] = _norm(p["name"])
                try:
                    price = self._parse_price(p)
                    n, icapacity, capacity, unit = self._parse_capacity(p, price)
                    icapacity, capacity, unit, ppunit = self._standardize_units(icapacity, capacity, unit, price)
                    if self.debug:
                        print("hipermercado:", hiper, "\n")
                    yield Result(hiper=hiper,
                                 name=p["name"],
                                 price=price,
                                 price_per_unit=float(ppunit),
                                 capacity=capacity,
                                 url=p["productURL"],
                                 image_url=p["imageURL"],
                                 date=p["date"],
                                 unit=unit,
                                 currency="€",
                                 item_capacity=icapacity,
                                 n_items=n)

                except GeneratorExit:
                    return
                except:
                    print("## ERROR: failed to parse", p)
                    continue


class Auchan(HipermercadosPortugal):
    hipers = ['Auchan']


class Continente(HipermercadosPortugal):
    hipers = ['Continente']


class Minipreco(HipermercadosPortugal):
    hipers = ['Minipreço']


class PingoDoce(HipermercadosPortugal):
    hipers = ['PingoDoce']


@dataclass
class Query:
    query: str
    required: Optional[List[str]] = None
    blacklist: Optional[List[str]] = None

    def search(self, hiper: Optional[HipermercadosPortugal] = None):
        hiper = hiper or HipermercadosPortugal()
        return hiper.update(query=self.query,
                            blacklist=self.blacklist,
                            required=self.required)


if __name__ == "__main__":
    hiper = HipermercadosPortugal()

    for res in hiper.scan():
        print(res.unique_id)
