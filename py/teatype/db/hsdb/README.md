# HSDB - Hybrid Storage Database

An in-memory object database with a write-through raw-file store on disk, served over HTTP.
Models are plain Python classes; queries run against in-memory indices; the disk copy is a
JSON-file-per-entry mirror.

Status of this document: written from reading the code and running it (examples below were executed).
Statements marked **(verified)** were reproduced by running code, **(code)** come from reading it only.

---

## 1. Architecture

```mermaid
flowchart LR
    subgraph Host process - first importer
        M[HSDBModel classes] --> HS[HybridStorage singleton]
        HS --> IDB[IndexDatabase - memory]
        HS --> RFH[RawFileHandler - disk]
        U[HSDB unit - FastAPI/uvicorn thread] --> HS
    end
    RFH --> FS[(hsdb/indexdb/&lt;plural&gt;/&lt;id&gt;.json)]
    C1[HSDBClient in process B] -- HTTP /hsdb/... --> U
    C2[HSDBClient in process C] -- HTTP /hsdb/... --> U
    C0[HSDBClient in the host itself] -- HTTP /hsdb/... --> U
```

| Layer | File | Role |
|---|---|---|
| Models | `core/HSDBModel.py`, `HSDBAttribute.py`, `HSDBRelation.py`, `HSDBField.py`, `HSDBMeta.py` | Declarative schema, validation, serialization, ORM-ish classmethods |
| Query | `core/HSDBQuery.py` | Chainable query builder, also parses URL query strings |
| Memory | `IndexDatabase.py`, `indices/*` | Primary index + model index + field index + relational index |
| Disk | `RawFileHandler.py`, `RawFileStructure.py` | JSON file per entry under a fixed folder tree |
| Glue | `HybridStorage.py` | Singleton that applies every write to memory first, then disk |
| Serving (A) | `HSDBServer.py`, `django_support/*` | Django + DRF server with auto REST routes per model (standalone script style) |
| Serving (B) | `modulo/hsdb.py` (`HSDB` unit) + `HSDBClient.py` | Embedded FastAPI server in a background thread + launch-or-connect client (see section 6) |

Two serving paths exist and are independent: **(A)** `HSDBServer` is a blocking Django `runserver`
(`examples/student-db/student_db_server.py`), **(B)** the `HSDB` modulo unit is what you import from application code.
Both sit on the same `HybridStorage`.

---

## 2. The hybrid memory-disk store

### Write path (`HybridStorage.create_entry`)

1. `IndexDatabase.create_entry` builds the model instance (validation happens in `HSDBModel.__init__`),
   adds it to the primary index, the model index and all indexed-field indices.
2. If `write=True` and not cold mode, `RawFileHandler.create_entry` writes `<root>/hsdb/indexdb/<plural>/<id>.json`.
3. If the file does not exist afterwards, the memory entry is **rolled back** and `410` is returned.

`update_entry` / `delete_entry` apply to memory first, then disk. **Disk failures there are only logged**:
memory and disk can diverge silently.

Return codes used throughout: `200` ok, `404` not found, `409` already exists, `410` disk write lost, `500` error.

### Read path

Reads never touch disk. Everything is served from memory:

| Lookup | Cost | Mechanism |
|---|---|---|
| by id | O(1) | primary index (`Index`, dict keyed by id string) |
| all of a model | O(1) to get ids | `ModelIndex`: `{ModelName: {ids}}` |
| equality on an `indexed=True` attribute | O(1) | `FieldsIndex`: `{"Model.field": {value: {ids}}}` |
| anything else (`>`, `<`, `contains`, non-indexed `==`) | O(n) over the model's entries | linear filter |
| relation lookup | O(1) | `RelationalIndex` (forward + reverse dicts) |

Multiple indexed equality conditions are intersected. Remaining conditions are filtered linearly on the narrowed set.

### Cold mode

`cold_mode=True` skips creating the folder tree and all disk writes: a pure in-memory database
(this is what the example uses). Otherwise the root is `root_path` -> env `HSDB_ROOT_PATH` -> `/var/lib`, and
`<root>/hsdb/` is created. If the folder cannot be created the process **exits** (`err(exit=True)`).

### Folder layout (`RawFileStructure._FS`)

`audits`, `backups/{indexdb,migration,rawfiles}`, `dumps/migrations`, `exports`, `indexdb`, `logs/{migrations,reads,writes}`,
`lut`, `models/adapters`, `rawfiles`, `redundancy`, `rejectpile/{indexdb,rawfiles}`, `reports`.
Only `indexdb/<plural>/` is actually used today; the rest is scaffolding.

### Restart behaviour: disk is write-only today

Nothing loads the files back at startup, and the manual path is broken **(verified)**:
`HybridStorage.install_index_files()` expects files shaped `{base_data, model_data, ...}` but
`RawFileHandler` writes the flat `Model.serialize()` dict, so it fails with `'NoneType' object has no attribute 'get'`.
A restarted host therefore starts empty even in non-cold mode.

---

## 3. Models

```python
class Student(HSDBModel):
    age        = HSDBAttribute(int, required=True, indexed=True)
    name       = HSDBAttribute(str, required=True, searchable=True)
    university = HSDBRelation.ManyToOne(University, required=True)
```

- Attribute types: `bool, dt, float, int, str`. Options: `required, indexed, unique, computed, editable, default, max_size, searchable, description`.
- Base attributes on every model: `id`, `created_at`, `updated_at` (all computed; passing them in `data` raises).
- Ids are generated at construction (`generate_id()`), **global across models** (not per model).
- Relations: `OneToOne`, `ManyToOne`, `ManyToMany` (`HSDBRelation.<Kind>(TargetModel)`). Stored as ids in the `RelationalIndex`,
  accepted as model instances, id strings, or id wrappers.
- Class metadata is derived on first instantiation: `model_name`, `resource_name(_plural)` (kebab case, `-model` suffix stripped), `path = <plural>/<id>.json`.
- Serialization: `Model.serialize(instance, include_relations=False, expand_relations=False)`.
  **Relations are omitted by default**; `include_relations` adds ids, `expand_relations` nests full objects (one level).
- Classmethods: `create, get, all, find_by, count, schema`; instance: `save, update, delete, validate`.
  They act on `HybridStorage.instance()` of *the current process*, so they only work in the host process.
- `unique=True` is **not enforced** on create (no check in `IndexDatabase.create_entry`) (code).

---

## 4. Querying

```python
Student.query.where('age').greater_than_or_equals(18).sort_by('name', 'desc').first()
```

Verbs: `equals, greater_than(_or_equals), less_than(_or_equals), contains`, aliases `eq/gt/gte/lt/lte`.
Terminals: `all, collect, first, last, count, get(id), paginate(page, size)`, plus iteration/`len`.
A query object is single-use (`already_executed`). `page=-1` means last page.

### URL form (`HSDBQuery.from_params`, used by both servers)

`?age__gte=18&gender=male&sort=-name&page=0&page_size=20&include_relations=true`

- Operators: `eq` (default), `gt`, `gte`, `lt`, `lte`, `contains`. `ne` and `in` are parsed but **silently ignored**.
- Values are coerced: `"18"` -> int, `"1.5"` -> float, `"true"/"false"` -> bool, `"null"/"none"` -> None.
  A *string* field whose value looks numeric (e.g. `"123"`) can therefore not be matched.
- `limit` only works together with `page`. `fields` and `ids_only` make the result non-model objects, which the
  serialization step cannot handle (the REST views and the HSDB unit do not support them).
- `HSDBQuery.to_query_string()` is the inverse and exists for building these URLs.

---

## 5. Quirks and gotchas

**Singleton / initialization**
- `HybridStorage` is a `SingletonMeta` singleton: the first construction wins, later `models`/`root_path`/`cold_mode` arguments are ignored.
- Anything that calls `HybridStorage()` bare (`HSDBQuery(...)`/`Model.query`, and instantiating any model that has relations) creates the
  default **non-cold** storage if none exists yet -> tries `/var/lib/hsdb` and may exit. In a client process never instantiate relation-bearing
  models or use `Model.query`; use `HSDBClient`.
- Import cycle: `core/` and `indices/` import `HybridStorage`/`IndexDatabase` from the package while `teatype/db/hsdb/__init__.py` is still
  executing, so `from teatype.db.hsdb import HybridStorage` yields the **module**, not the class (`'module' object is not callable`).
  Code in this cycle must import lazily from the submodule path (`from teatype.db.hsdb.HybridStorage import HybridStorage`).
- `HybridStorage` subclasses `Thread` but is never started; `coroutines/*.py` are empty; the queues are unused.

**Behaviour**
- Entry ids are global: `HybridStorage.fetch_entry(id)` does not check the model. The HSDB unit adds that check per route.
- Querying a completely empty database raises `KeyError('No db entries found')` (also `first()`/`last()`).
- Cold mode + `create_entry(write=True)` always yields `410` because no file is ever produced. Pass `write=False` in cold mode (the HSDB unit does).
- `HybridStorage.delete_entry` for an unknown id returns `500` (not `404`), because the lookup raises inside its `try`.
- `RawFileHandler.create_entry(model_instance, compress)` takes `compress` as 2nd parameter; `HybridStorage` passes `overwrite_path` there.
- `BaseIndex.__iter__` yields **values**, while `IndexDatabase.fetch_all()` and `print()` iterate it as if it yielded ids (code, not run).

**Modulo unit (`ApplicationUnit`) traps that the HSDB unit works around**
- `CoreUnit` forbids `Unit(...)`; use `Unit.create(**kwargs)` (keyword args only).
- `ApplicationUnit.__init__` installs SIGINT/SIGTERM handlers that call `shutdown()` and then **do not exit**, i.e. they swallow Ctrl+C for the whole host process; it also only works on the main thread. `HSDB` overrides `_setup_signal_handlers` to a no-op.
- The backend thread is non-daemon, so the host process would never exit. `HSDB` sets `backend.daemon = True`.
- Defaults start a Vite dashboard (`pnpm start`), Redis service, RAX and socket units. `HSDB` disables all of them.
- `teatype.modulo.hsdb` is both a submodule and (via `modulo/__init__.__getattr__`) a lazy attribute. If the submodule is imported first,
  `from teatype.modulo import hsdb` returns the module, not a client. Prefer `from teatype.modulo.hsdb import HSDB`.

---

## 6. The launch-or-connect pattern (`HSDB` unit + `HSDBClient`)

### Usage

```python
from teatype.modulo.hsdb import HSDB
from server.models import Class, Professor, Student, University

hsdb = HSDB.attach(models=[Class, Professor, Student, University], port=9876, cold_mode=True)
```

`attach()` always returns an `HSDBClient`:

1. Probe `GET http://host:port/hsdb` (250 ms). If a service answers with `{"service": "hsdb"}` -> **connect as client**.
   If models were passed and the running server lacks some, a warning is logged.
2. Otherwise **launch** the server in this process: `HybridStorage(models, root_path, cold_mode)` + FastAPI/uvicorn in a daemon thread,
   wait until it answers, return a client. `client.server` is then the `HSDB` unit (`None` for pure clients),
   so `if hsdb.server:` is the "am I the host" check and `hsdb.server.hybrid_storage` gives direct local access (e.g. for bulk seeding).
3. Bind race (two processes start simultaneously): the loser's uvicorn thread dies on `address in use`, `attach()` notices its thread is
   not running and falls back to client **(verified: 4 simultaneous processes -> 1 host, 3 clients)**.
4. Calling `attach()` again in the same process returns the same client (first call wins, arguments ignored).

Identity of "the one HSDB" is the `host:port`. One server per port; use another port for another database.
The server lives and dies with the **launching process**; for a long-lived server run a small host script that calls `attach()` and
`hsdb.server.join()`.

### Client API (`HSDBClient`)

Models are given as class or name string. Results are **dicts**, not model instances (model constructors refuse computed fields like `id`).

```python
hsdb.count(Student)
hsdb.get(Student, id)                                  # dict or None
hsdb.all(Student, expand_relations=True)
hsdb.find(Student, gender='male', age__gte=18, sort='-name')
hsdb.query(Student).where('age').greater_than_or_equals(18).sort_by('age', 'desc').first()   # HSDBRemoteQuery, same verbs as HSDBQuery (no gt/gte aliases)
hsdb.create(Student, {...})                            # relations by id string
hsdb.update(Student, id, {'age': 21})                  # PATCH, partial
hsdb.delete(Student, id)                               # bool
hsdb.info()                                            # {'service','pid','models':{name:count}}
```

`HSDBRemoteQuery` supports `where, equals, greater_than(_or_equals), less_than(_or_equals), contains, sort_by, paginate, all, first, last, count`
(`count()` fetches the list). Two conditions with the same field and operator overwrite each other.

### HTTP routes (all JSON, served by the unit)

| Method | Path | Purpose |
|---|---|---|
| GET | `/hsdb` | identity + per-model counts |
| GET | `/hsdb/{Model}` | query via `from_params` syntax |
| POST | `/hsdb/{Model}` | create |
| GET / PATCH / DELETE | `/hsdb/{Model}/{id}` | read / partial update / delete (404 if id missing or belongs to another model) |

`include_relations` / `expand_relations` are accepted on the GET and PATCH routes. The unit also keeps the generic `ApplicationUnit` routes
(`/status`, `/api/app/status`, `/api/logs`, ...). Handlers are plain `def`, so FastAPI runs them in its thread pool.

### Why HTTP and not Redis

Measured on loopback in this setup: `HSDBClient.get` by id **~0.95 ms** median, indexed `find` **~1.2 ms**, full-collection sorted
query (200 rows) **~4 ms** (keep-alive `requests.Session`). A bare Redis `PING` is ~0.04 ms, but a request/response over Redis would
additionally need a worker thread, a reply channel and serialization in the host, and a running Redis daemon; the repo's Redis layer is pub/sub
message dispatch, not RPC. The achievable gain is a fraction of a millisecond per call while adding an infrastructure dependency, so HTTP was
chosen (also: works across machines, debuggable with curl, reuses `from_params`). If per-call latency ever matters, batch with `find` instead
of many `get` calls, or add a Redis list-based RPC behind the same `HSDBClient` interface.

### Security

The server has no authentication and exposes create/update/delete. It binds to `127.0.0.1` by default; do not expose it on other interfaces
without adding auth. Model names from URLs are looked up in the registered-model dict (no dynamic import/eval).

---

## 7. Example

`examples/student-db/student_db_hsdb.py`: run it in two terminals from `examples/student-db/`.

```bash
../../teatype-venv/bin/python student_db_hsdb.py     # terminal 1: launches HSDB, seeds, queries, waits on Enter
../../teatype-venv/bin/python student_db_hsdb.py     # terminal 2: connects as client, queries
```

`examples/student-db/student_db_server.py` is the standalone Django (`HSDBServer`) variant with auto REST routes per model.

---

## 8. Fixes made while building the unit

These were pre-existing breakages that blocked creating/serving entries:

- `HybridStorage.__init__`: `IndexDatabase` resolved to the module (import cycle) -> lazy import.
- `HSDBRelation.__init__`, `HSDBQuery.__init__`: same cycle for `HybridStorage` -> lazy import.
- `RawFileHandler` / `parse_index_files`: used `fs.index`, folder was renamed to `indexdb` -> `fs.indexdb`.
- `HybridStorage.create_entry`: `model_instance.serialize()` (classmethod without instance) -> `model_instance.model.serialize(model_instance)`.
- `HSDBModel.__setattr__`: relations given as plain id strings (the JSON case) crashed on `.instance` -> wrapped into a field.
- `HSDBModel.serialize`: imported `HSDBRelation` from the package (not exported) -> removed, it is already imported at module top.
- `django_support/views.py`: imported `HSDBQuery` from the package root -> from `core`.
- `modulo/__init__.py`: lazy `hsdb` accessor imported a non-existent `teatype.db.hsdb.HSDB`.
- `HSDBClient.py` was a stub that instantiated a unit at import time; replaced by the HTTP client.

## 9. Open items (not changed)

- Restore from disk on startup (format mismatch, see section 2).
- Enforce `unique=True`; `ne`/`in` operators; `ids_only`/`fields` serialization.
- Relation resolution only fully implemented for many-to-one in `HSDBRelation._RelationWrapper` (see TODOs in `HSDBModel.py`).
- Detached host process (models passed by import path) instead of "dies with the launching process".
