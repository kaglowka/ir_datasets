from . import lazy_libs
from . import log
from . import util
from . import formats
registry = util.Registry()
from . import datasets
from . import indices
from . import wrappers
from . import commands

Dataset = datasets.base.Dataset


def load(name):
    return registry[name]


def _parent_id(dataset_id: str, entity_type: str) -> str:
    """
    Maps a dataset_id to a more general ID that shares the same entity handler (e.g., docs_handler). For example,
    for docs, "msmarco-document/trec-dl-2019/judged" -> "msmarco-document" or "wikir/en1k/test" -> "wikir/en1k".
    This is useful when creating shared document resources among multiple subsets, such as an index.

    Note: At this time, this function operates by convention; it finds the lowest dataset_id in the
    hierarchy that has the same docs_handler instance. This function may be updated in the future to
    also use explicit links added when datasets are registered.
    """
    ds = load(dataset_id)
    segments = dataset_id.split("/")
    handler = getattr(ds, f'{entity_type}_handler')()
    parent_ds_id = dataset_id
    while len(segments) > 1:
        segments.pop()
        try:
            parent_ds = load("/".join(segments))
            if getattr(parent_ds, f'has_{entity_type}')() and getattr(parent_ds, f'{entity_type}_handler')() == handler:
                parent_ds_id = "/".join(segments)
        except KeyError:
            pass # this dataset doesn't exist
    return parent_ds_id


def docs_parent_id(dataset_id: str) -> str:
    return _parent_id(dataset_id, 'docs')
corpus_id = docs_parent_id # legacy


def queries_parent_id(dataset_id: str) -> str:
    return _parent_id(dataset_id, 'queries')


def qrels_parent_id(dataset_id: str) -> str:
    return _parent_id(dataset_id, 'qrels')


def scoreddocs_parent_id(dataset_id: str) -> str:
    return _parent_id(dataset_id, 'scoreddocs')


def docpairs_parent_id(dataset_id: str) -> str:
    return _parent_id(dataset_id, 'docpairs')


def qlogs_parent_id(dataset_id: str) -> str:
    return _parent_id(dataset_id, 'qlogs')


def create_dataset(docs_tsv=None, queries_tsv=None, qrels_trec=None):
    TsvDocs = formats.TsvDocs
    TsvQueries = formats.TsvQueries
    TrecQrels = formats.TrecQrels
    components = []
    if docs_tsv is not None:
        components.append(TsvDocs(util.File(docs_tsv)))
    if queries_tsv is not None:
        components.append(TsvQueries(util.File(queries_tsv)))
    if qrels_trec is not None:
        components.append(TrecQrels(util.File(qrels_trec), {}))
    return datasets.base.Dataset(*components)


def main(args):
    import sys
    if len(args) < 1 or args[0] not in commands.COMMANDS:
        cmds = ','.join(commands.COMMANDS.keys())
        sys.stderr.write(f'Usage: ir_datasets {{{cmds}}} ...\n')
        sys.exit(1)
    commands.COMMANDS[args[0]](args[1:])


def main_cli():
    import sys
    main(sys.argv[1:])

__version__ = "0.4.3" # NOTE: keep this in sync with setup.py
