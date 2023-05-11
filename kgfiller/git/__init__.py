from typing import Type, Any
import git
import pathlib
from gitdb.db.loose import LooseObjectDB
from kgfiller import logger, PATH_DATA_DIR, escape
from kgfiller.kg import PATH_ONTOLOGY


class DataRepository(git.Repo):
    def __init__(self, path: Any | None = None, odbt: Type[LooseObjectDB] = git.GitCmdObjectDB, search_parent_directories: bool = False, expand_vars: bool = True) -> None:
        if path is None:
            path = PATH_DATA_DIR
        git.Repo.__init__(self, path, odbt, search_parent_directories, expand_vars)

    def commit_edits_if_any(self, message: str, file: str | pathlib.Path = None, description=None, *other_files):
        if file is None:
            file = PATH_ONTOLOGY
        elif not isinstance(file, pathlib.Path):
            file = pathlib.Path(file)
        all_files = [file] + [f if isinstance(f, pathlib.Path) else pathlib.Path(f) for f in other_files]
        for i in range(0, len(all_files)):
            f = all_files[i]
            if not f.exists():
                raise FileNotFoundError(f"File {f} does not exist")
            else:
                all_files[i] = f.relative_to(self.working_dir)
        full_message = escape(f"{message}\n\n{description}" if description else message)
        self.git.add(*all_files)
        try:
            self.git.commit("-m", full_message)
            logger.info("Committed changes to files %s, with message: `%s`", map(str, all_files), message)
        except git.exc.GitCommandError as e:
            if "nothing to commit" in (str(e.stdout) + str(e.stderr)):
                logger.info("Files %s, didin't change: skipping commit", map(str, all_files))
            else:
                raise e
