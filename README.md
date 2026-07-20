# kobra-partner

Cliente Python de la API Partner de Kobra.

```bash
pip install "git+https://github.com/pyme0/kobra-partner.git"
pip install -U "git+https://github.com/pyme0/kobra-partner.git"
```

```python
from kobra_partner import Client

client = Client(api_key="pk_…", base_url="https://su-entorno.example.com")
client.me()
```

Documentación de la API: `{base_url}/partner/docs`

MIT
