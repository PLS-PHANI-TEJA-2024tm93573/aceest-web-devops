"""Simple in-memory client store for the ACEest Flask app.

Clients are stored as dictionaries with keys:
  - name (str)
  - age (int or str)
  - weight (float or str)
  - program (str)
  - adherence (int)
  - notes (str)

This module provides thread-safe helpers to add/list/clear clients and
optional simple JSON persistence helpers for durability between restarts.
"""

import threading
import json
from typing import List, Dict, Any

_lock = threading.Lock()
_clients: List[Dict[str, Any]] = []


def add_client(client: Dict[str, Any]) -> None:
	"""Add a client dictionary to the in-memory store.

	The client is copied before storing to avoid accidental external mutation.
	"""
	with _lock:
		_clients.append(client.copy())


def get_clients() -> List[Dict[str, Any]]:
	"""Return a shallow copy of the list of clients."""
	with _lock:
		return [c.copy() for c in _clients]


def clear_clients() -> None:
	"""Clear all clients from the store."""
	with _lock:
		_clients.clear()


def save_to_file(path: str) -> None:
	"""Persist the current clients list to a JSON file (overwrites)."""
	with _lock:
		with open(path, "w", encoding="utf-8") as f:
			json.dump(_clients, f, indent=2, ensure_ascii=False)


def load_from_file(path: str) -> None:
	"""Load clients from a JSON file into the in-memory store.

	If the file does not exist the function returns silently. Only lists of
	dicts are accepted; malformed entries are ignored.
	"""
	try:
		with open(path, "r", encoding="utf-8") as f:
			data = json.load(f)
	except FileNotFoundError:
		return

	if not isinstance(data, list):
		return

	with _lock:
		_clients.clear()
		for item in data:
			if isinstance(item, dict):
				_clients.append(item)

