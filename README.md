# Deník

## 9. 11. 2026 – Propojení publikací s časopisy

Do společného projektu jsme přidali modely Journal a JournalType z naší části Journals. Jsou ve stejné složce `src/DBDefinitions/Publications` jako modely publikací. Publikace odkazuje přes `journal_id` na existující časopis. Přes vztahy `journal` a `publications` můžeme načíst obě strany vazby.

V `systemdata.json` máme 10 ukázkových časopisů TEST01 až TEST10 a 10 publikací, jednu pro každý časopis. Názvy časopisů jsou pouze testovací. Zachovali jsme původní ID záznamů a jejich vzájemné odkazy. Pro typy časopisů máme jeden hlavní typ a jeden podtyp.

Soubor jsme zjednodušili na základní údaje bez auditních ID, datumů vytvoření a dalších nepovinných podrobností. Sekce jsou v pořadí: `journaltypes`, `journals`, `publicationtypes`, `publications`, `authors`, `authorships`. Autoři a autorství zůstávají kvůli úplnému propojení publikací. Nepovinná pole modelů stále existují; jen je v těchto ukázkových datech nevyplňujeme. Další kopii datového souboru nemáme.

V `seed.py` jsme doplnili pořadí importu podle cizích klíčů. Úpravy spolužáků pro načítání datumů a samostatné sessions zůstaly zachované. Pomocnou funkci `UUIDFKey` jsme u `PublicationModel.journal_id` nahradili přímým `mapped_column(ForeignKey(...))`, aby databáze vazbu skutečně kontrolovala.

Ověřili jsme import celé sady dvakrát bez duplicit, načítání vazeb, změnu časopisu u publikace a odmítnutí chybného odkazu nebo smazání používaného časopisu. Ve vlastním `.venv` společného projektu prošlo 26 databázových testů a 4 kontroly architektury. Celou testovací sadu šablony jsme tím neověřovali.

Backend jsme spustili nad databází `publications_demo`. Přes databázový `main.py` jsme načetli všech 10 publikací s časopisy a všech 10 časopisů s jejich publikacemi. Ověřili jsme i databázový cizí klíč a dostupnost GraphQL stránky a schématu učitelovy šablony.

### Spuštění společného projektu

Při první přípravě ve složce společného projektu:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest pytest-asyncio pytest-cov aiosqlite
```

Na našem počítači používáme stávající kontejnery a novou databázi `publications_demo`. Původní databázi `data` tím neměníme. Po zapnutí Docker Desktop:

```powershell
docker start uois-postgres_gql-1 uois-pgadmin-1
```

Databázi už máme vytvořenou. Na dalším počítači se stejnou Docker sestavou ji založíme jednou:

```powershell
docker exec uois-postgres_gql-1 createdb -U postgres publications_demo
```

Při běžném spuštění ve složce společného projektu:

```powershell
.\.venv\Scripts\Activate.ps1
$env:POSTGRES_DB = "publications_demo"
$env:DEMODATA = "True"
python -m uvicorn main:app --reload
```

GraphQL stránka učitelovy šablony je na http://localhost:8000/gql. Vlastní operace pro časopisy ještě nejsou součástí schématu. pgAdmin otevřeme na http://localhost:31122 a po obnovení seznamu databází vybereme **Databases → publications_demo → Schemas → public → Tables**.

Backend zastavíme přes **Ctrl+C**. Ve stejném terminálu můžeme vypsat data:

```powershell
python -m src.DBDefinitions.main Journal list
python -m src.DBDefinitions.main Publication list
```

V novém terminálu znovu aktivujeme `.venv` a nastavíme `POSTGRES_DB`, jinak se použije výchozí databáze `data`.

### Testy propojení

```powershell
python -m pytest tests/db/test_journals.py tests/db/test_publication_model_mapping.py -q -o addopts=
python -m pytest tests/test_architecture.py -q -o addopts=
```

Pro ruční načtení dat spustíme aplikaci s `DEMODATA=True`. Nový cizí klíč se vytvoří na nové databázi; pokud už tabulka `publications` existuje ze starší verze, samotné `create_all` její strukturu nezmění. V takovém případě je potřeba samostatně doplnit cizí klíč po kontrole existujících odkazů, nebo ukázku spustit v nové vývojové databázi.

Tímto jsme ověřili databázové propojení. Vlastní služby a GraphQL operace pro časopisy ještě zbývá doplnit.

## 23.10. 2026

Změny:
- zprovoznění databázové vrsty, včetně všech příkazů CRUD
- vytvoření základních dat pro Publication a PublicationType

Problémy k řešení:
- implementace základních dat








# Event boilerplate project

Demonstrační boilerplate pro doménu `Event / EventInvitation` podle funkčního vzoru ze `src.zip`.

## Zásady

- GQL vrstva nesmí importovat DB vrstvu ani typově odkazovat na DB modely.
- Pro decoupling mezi vrstvami se používají `Protocol` kontrakty v `src/common/protocols.py`.
- `LoaderMap`, services a GQL typy jsou explicitně definované.
- `EventInvitation` je vazba `Event - User` se stavem pozvánky/účasti.
- `UserGQLModel` je externí federovaná entita pro Apollo Federation.
- `StateGQLModel` je také externí federovaná entita, protože stav pozvánky typicky patří do UG / state-machine subgrafu.
- Page resolvery vždy používají `whereType` definovaný přes `@createInputs2`.
- Mutace používají `BaseService.ExecuteServiceMethod` a `CreateErrorCallback`, aby resolver neobsahoval lokální zpracování výjimek.
- `BaseGQLModel.from_dataclass()` zůstává kompatibilní název, ale interně volá `from_db()` a ukládá původní entitu do `_dbdata` bez `dataclasses.asdict()`.


## Závislost na `uoishelpers`

Projekt pracuje s balíkem `uoishelpers` z repozitáře:

```text
https://github.com/hrbolek/uoishelpers/archive/4e41615436d6effbe248d8503e4df373549bcec3.zip
```

Závislost je uvedená přímo v `pyproject.toml`:

```toml
'uoishelpers @ https://github.com/hrbolek/uoishelpers/archive/4e41615436d6effbe248d8503e4df373549bcec3.zip'
```

Boilerplate proto nepřidává lokální náhražky pro `uoishelpers`. Používá importy ve stejném stylu jako funkční vzor, například:

```python
from uoishelpers.dataloaders.LoaderMapBase import LoaderMapBase
from uoishelpers.dataloaders.IDLoader import IDLoader
from uoishelpers.gqlpermissions import OnlyForAuthentized
from uoishelpers.resolvers import PageResolver, createInputs2
```

Závislost je připnutá na konkrétní commit, aby instalace i CI používaly stejnou verzi.

### Instalace závislostí ve Windows

V kořenovém adresáři projektu vytvořte a aktivujte virtuální prostředí a
nainstalujte projekt včetně závislostí z `pyproject.toml`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Instalaci lze ověřit příkazem:

```powershell
python -c "import uoishelpers; print(uoishelpers.__file__)"
```

Pokud už virtuální prostředí existuje, stačí ho aktivovat a spustit
`python -m pip install -e .`. Používejte stejný aktivní Python pro instalaci
i spuštění aplikace; jinak může import `uoishelpers` stále skončit chybou
`ModuleNotFoundError`.

## Vrstvy

```text
DBDefinitions/
  Domain_Events/
    EventModel.py
    EventInvitationModel.py

Dataloaders/
  __init__.py        # explicitní LoaderMap

ServiceDefinitions/
  Domain_Events/
    EventService.py
    EventInvitationService.py

GraphTypeDefinitions/
  BaseGQLModel.py    # _dbdata + LoaderName kontrakt
  Domain_Events/
    EventGQLModel.py
    EventInvitationGQLModel.py
  Domain_UG/
    UserGQLModel.py  # externí federovaná entita
    StateGQLModel.py # externí federovaná entita
```

## Studenti typicky doplní

1. DB model do `DBDefinitions/Domain_X`.
2. Explicitní položku v `LoaderMap`.
3. Service třídu do `ServiceDefinitions/Domain_X`.
4. GQL typ bez importu DB vrstvy.
5. `InputFilter` přes `@createInputs2`.
6. Query přes `PageResolver(... whereType=...)`.
7. Mutace přes `ExecuteServiceMethod`.

## Spuštění Coder

```bash
python .CoderDefinitions/main.py
```
