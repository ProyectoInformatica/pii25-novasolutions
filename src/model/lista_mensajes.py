from __future__ import annotations
from typing import Optional, Iterator
from src.model.mensaje import Mensaje


class NodoMensaje:
    __slots__ = ("dato", "siguiente")

    def __init__(self, dato: Mensaje) -> None:
        self.dato: Mensaje = dato
        self.siguiente: Optional[NodoMensaje] = None


class ListaMensajes:
    """Lista simplemente enlazada de Mensaje (insertion-order, O(1) append)."""

    def __init__(self) -> None:
        self._cabeza: Optional[NodoMensaje] = None
        self._cola:   Optional[NodoMensaje] = None
        self._longitud: int = 0

    def agregar(self, mensaje: Mensaje) -> None:
        nodo = NodoMensaje(mensaje)
        if self._cola is None:
            self._cabeza = self._cola = nodo
        else:
            self._cola.siguiente = nodo
            self._cola = nodo
        self._longitud += 1

    def ultimo_id(self) -> Optional[int]:
        """ID del mensaje más reciente (cola), o None si la lista está vacía."""
        return self._cola.dato.id_mensaje if self._cola else None

    def __len__(self) -> int:
        return self._longitud

    def __bool__(self) -> bool:
        return self._longitud > 0

    def __iter__(self) -> Iterator[Mensaje]:
        nodo = self._cabeza
        while nodo is not None:
            yield nodo.dato
            nodo = nodo.siguiente