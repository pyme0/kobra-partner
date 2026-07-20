# kobra-partner

Cliente Python de la API Partner de Kobra.

## Instalar

```bash
pip install kobra-partner
pip install -U kobra-partner
```

## Uso

```python
from kobra_partner import Client

client = Client(
    api_key="pk_…",
    base_url="https://control-center-production-03de.up.railway.app",
)
client.me()
```

`base_url` es el host del control-center (sin path). La clave se envía como `X-Kobra-Partner-Key`.

## Documentación de la API

Referencia y playground (oficial en staging):

https://control-center-production-03de.up.railway.app/partner/docs

En cualquier entorno: `{base_url}/partner/docs`.

## Paquete

- PyPI: https://pypi.org/project/kobra-partner/
- Código: https://github.com/pyme0/kobra-partner

MIT
