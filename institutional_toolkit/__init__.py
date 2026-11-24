"""Road Safety Institutional Toolkit, loaded lazily for testable data services."""
def render(*args, **kwargs):
    from .ui import render as _render
    return _render(*args, **kwargs)
__all__ = ["render"]
